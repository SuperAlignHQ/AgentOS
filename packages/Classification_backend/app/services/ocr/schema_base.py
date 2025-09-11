from pydantic import BaseModel, Field
from enum import Enum


class StrEnumBase(str, Enum):
    """Base enum with str-like behaviour."""
    def __str__(self):
        return self.value

    @classmethod
    def keys(cls):
        return [m.name for m in cls]

    @classmethod
    def values(cls):
        return [str(m) for m in cls]

    @classmethod
    def items(cls):
        return [(m.name, str(m)) for m in cls]


class FileProperties(BaseModel):
    file_path: str = Field(default="", description="Local file path")
    file_dir: str = Field(default="", description="Temp dir for file artifacts")
    file_type: str = Field(default="", description="File type (pdf, png, jpeg)")
    pages: int = Field(default=0, description="Number of pages/images")
    page_paths: list[str] = Field(default_factory=list, description="Paths to per-page images")
    file_present: bool = Field(default=False, description="Whether file exists")


class DocumentCategoryDetails(BaseModel):
    """Classification results for one file."""
    document_category: str | None = Field(default=None, description="e.g. income_document")
    document_type: str | None = Field(default=None, description="e.g. payslip")
    status: str | None = Field(default=None, description="classified / extra / unknown")
    note: str | None = Field(default=None, description="Any extra comment")


class FileResults(BaseModel):
    """Aggregated result (file metadata + classification)."""
    properties: FileProperties = FileProperties()
    document_category_details: DocumentCategoryDetails = DocumentCategoryDetails()
    ocr_results: dict | None = Field(default=None, description="Optional OCR/LLM raw output")
