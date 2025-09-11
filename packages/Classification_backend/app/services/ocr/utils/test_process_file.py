import os
import tempfile
import shutil
import pytest
from unittest import mock
from ocr.schema import FileProperties

from document_reader.ocr.utils.process_file import (
    process_file,
    FileTypes,
    generate_random_string,
    identify_file_type,
    identify_file_type_by_magic,
    process_pdf,
    download_file,
)

@pytest.fixture
def temp_png_file():
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "test.png")
    # Minimal valid PNG header
    with open(file_path, "wb") as f:
        f.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 10)
    yield file_path
    shutil.rmtree(temp_dir)

@pytest.fixture
def temp_jpeg_file():
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "test.jpg")
    # Minimal valid JPEG header
    with open(file_path, "wb") as f:
        f.write(b'\xff\xd8\xff' + b'\x00' * 10)
    yield file_path
    shutil.rmtree(temp_dir)

@pytest.fixture
def temp_pdf_file():
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "test.pdf")
    # Minimal valid PDF header
    with open(file_path, "wb") as f:
        f.write(b'%PDF-1.4\n%')
    yield file_path
    shutil.rmtree(temp_dir)

def test_generate_random_string_length():
    s = generate_random_string(24)
    assert isinstance(s, str)
    assert len(s) == 24

def test_identify_file_type_png(temp_png_file):
    assert identify_file_type(temp_png_file) == FileTypes.PNG

def test_identify_file_type_jpeg(temp_jpeg_file):
    assert identify_file_type(temp_jpeg_file) == FileTypes.JPEG

def test_identify_file_type_pdf(temp_pdf_file):
    assert identify_file_type(temp_pdf_file) == FileTypes.PDF

def test_identify_file_type_by_magic_png(temp_png_file):
    assert identify_file_type_by_magic(temp_png_file) == FileTypes.PNG

def test_identify_file_type_by_magic_jpeg(temp_jpeg_file):
    assert identify_file_type_by_magic(temp_jpeg_file) == FileTypes.JPEG

def test_identify_file_type_by_magic_pdf(temp_pdf_file):
    assert identify_file_type_by_magic(temp_pdf_file) == FileTypes.PDF

def test_process_file_png(temp_png_file):
    props = process_file(file_path=temp_png_file)
    assert props.file_present is True
    assert props.file_type == FileTypes.PNG
    assert props.pages == 1
    assert props.page_paths == [props.file_path]

def test_process_file_jpeg(temp_jpeg_file):
    props = process_file(file_path=temp_jpeg_file)
    assert props.file_present is True
    assert props.file_type == FileTypes.JPEG
    assert props.pages == 1
    assert props.page_paths == [props.file_path]

def test_process_file_pdf_calls_process_pdf(temp_pdf_file):
    # Patch process_pdf to avoid actual PDF processing
    with mock.patch("document_reader.ocr.utils.process_file.process_pdf", return_value=["page1.png", "page2.png"]):
        props = process_file(file_path=temp_pdf_file)
        assert props.file_present is True
        assert props.file_type == FileTypes.PDF
        assert props.pages == 2
        assert props.page_paths == ["page1.png", "page2.png"]

def test_download_file_success(tmp_path, requests_mock):
    url = "http://example.com/test.png"
    file_path = tmp_path / "test.png"
    requests_mock.get(url, content=b"abc", status_code=200)
    download_file(url, str(file_path))
    assert file_path.read_bytes() == b"abc"

def test_download_file_failure(tmp_path, requests_mock):
    url = "http://example.com/test.png"
    file_path = tmp_path / "test.png"
    requests_mock.get(url, status_code=404)
    with pytest.raises(Exception):
        download_file(url, str(file_path))