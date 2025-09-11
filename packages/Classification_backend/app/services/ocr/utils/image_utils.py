import base64
from io import BytesIO
import pymupdf
from PIL import Image
import streamlit as st
import os
from datetime import datetime


def generate_metadata(file_path):
    """Generate metadata dictionary from file path and properties"""
    file_stat = os.stat(file_path)
    file_name = os.path.basename(file_path)
    parent_dir = os.path.basename(os.path.dirname(file_path))

    metadata = {
        "File Name": file_name,
        "Directory": parent_dir,
        "File Size": f"{file_stat.st_size / 1024:.2f} KB",
        "Last Modified": datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        "Created": datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
        "File Extension": os.path.splitext(file_name)[1],
        "Full Path": file_path
    }

    # Add image-specific metadata if it's an image
    if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        try:
            with Image.open(file_path) as img:
                metadata.update({
                    "Image Size": f"{img.size[0]}x{img.size[1]}",
                    "Image Mode": img.mode,
                    "Image Format": img.format
                })
        except Exception as e:
            st.error(f"Error reading image metadata: {str(e)}")

    # Add PDF-specific metadata if it's a PDF
    elif file_name.lower().endswith('.pdf'):
        try:
            doc = pymupdf.Document(file_path)
            metadata.update({
                "Page Count": len(doc),
                "PDF Version": doc.pdf_version,
                "Document Info": doc.metadata if doc.metadata else "No PDF metadata available"
            })
        except Exception as e:
            st.error(f"Error reading PDF metadata: {str(e)}")

    return metadata


def load_pdf_as_image(file_path):
    # Open PDF file
    doc = pymupdf.Document(file_path)

    # Get the first page
    page = doc[0]

    # Convert to image
    pix = page.get_pixmap()

    # Convert to PIL Image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    return img


def im_2_b64(image):
    buff = BytesIO()
    image.save(buff, format="JPEG")
    img_str = base64.b64encode(buff.getvalue()).decode("utf-8")
    return img_str


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
