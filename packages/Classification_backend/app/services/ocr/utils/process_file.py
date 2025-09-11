import tempfile, os
import secrets
import string
from typing import Optional
from fastapi import UploadFile

from schema_base import FileProperties, FileResults, DocumentCategoryDetails
from .logger import setup_logger
import pdf2image
from PIL import Image


logger = setup_logger(__name__)

# Limits (configurable)
DEFAULT_MAX_UPLOAD_BYTES = 30 * 1024 * 1024  # 30 MB
DEFAULT_MAX_PDF_PAGES = 8
DEFAULT_MAX_IMAGE_DIM = 2500  # px, longest side


class FileTypes(str):
    PNG = "png"
    JPEG = "jpeg"
    PDF = "pdf"


def generate_random_string(length: int = 16) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def identify_file_type_by_magic(file_path: str) -> Optional[str]:
    """Detect png/jpg/pdf using file header magic numbers."""
    with open(file_path, "rb") as f:
        header = f.read(10)
    if header.startswith(b'\x89PNG\r\n\x1a\n'):
        return FileTypes.PNG
    if header.startswith(b'\xff\xd8\xff'):
        return FileTypes.JPEG
    if header.startswith(b'%PDF'):
        return FileTypes.PDF
    return None


def identify_file_type(file_path: str) -> Optional[str]:
    ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    if ext in ("png",):
        return FileTypes.PNG
    if ext in ("jpg", "jpeg"):
        return FileTypes.JPEG
    if ext == "pdf":
        return FileTypes.PDF
    return identify_file_type_by_magic(file_path)


def save_upload_to_temp(upload_file: UploadFile, tmp_dir: Optional[str] = None,
                        max_bytes: int = DEFAULT_MAX_UPLOAD_BYTES) -> str:
    """
    Save uploaded file to a temporary folder (with size limit).
    Returns full path.
    """
    base_dir = tempfile.mkdtemp()
    os.makedirs(base_dir, exist_ok=True)

    _, ext = os.path.splitext(upload_file.filename or "")
    filename = f"{generate_random_string()}{ext}"
    full_path = os.path.join(base_dir, filename)

    total = 0
    chunk_size = 64 * 1024
    with open(full_path, "wb") as out:
        while True:
            chunk = upload_file.file.read(chunk_size)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                out.close()
                try:
                    os.remove(full_path)
                except Exception:
                    pass
                raise ValueError(
                    f"File '{upload_file.filename}' too large. Max allowed is {max_bytes} bytes."
                )
            out.write(chunk)

    # reset file pointer
    try:
        upload_file.file.seek(0)
    except Exception:
        pass

    return full_path


def process_pdf(file_path: str,
                max_pages: int = DEFAULT_MAX_PDF_PAGES,
                max_image_dim: int = DEFAULT_MAX_IMAGE_DIM) -> list[str]:
    """Convert PDF to PNG pages (downscales if > max_image_dim)."""
    images = pdf2image.convert_from_path(file_path)
    file_paths: list[str] = []
    for i, img in enumerate(images):
        if i >= max_pages:
            break
        if max(img.size) > max_image_dim:
            img.thumbnail((max_image_dim, max_image_dim))
        img_path = f"{file_path}_page_{i}.png"
        img.save(img_path, "PNG")
        file_paths.append(img_path)
    return file_paths


def process_file(url: Optional[str] = None,
                 file_path: Optional[str] = None,
                 max_pages: int = DEFAULT_MAX_PDF_PAGES) -> FileResults:
    """
    Process file into FileResults (detect type, convert PDF to images).
    """
    file_properties = FileProperties()
    file_properties.file_dir = tempfile.mkdtemp()
    file_properties.file_path = file_path or os.path.join(file_properties.file_dir, generate_random_string())

    # if url provided, download
    if url is not None:
        import requests
        r = requests.get(url)
        if r.status_code == 200:
            with open(file_properties.file_path, "wb") as f:
                f.write(r.content)
        else:
            raise RuntimeError(f"Failed to download {url}: {r.status_code}")

    file_properties.file_present = os.path.exists(file_properties.file_path)

    if file_properties.file_present:
        ftype = identify_file_type(file_properties.file_path)
        file_properties.file_type = ftype or ""
        if ftype in (FileTypes.PNG, FileTypes.JPEG):
            file_properties.page_paths = [file_properties.file_path]
        elif ftype == FileTypes.PDF:
            file_properties.page_paths = process_pdf(file_properties.file_path, max_pages=max_pages)
        else:
            file_properties.page_paths = []
        file_properties.pages = len(file_properties.page_paths)

    # wrap
    file_results = FileResults(
        properties=file_properties,
        document_category_details=DocumentCategoryDetails(),  # includes status/note now
        ocr_results=None
    )

    logger.info("file_results: %s", file_results.model_dump())
    return file_results
