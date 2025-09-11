# schema.py
from pydantic import BaseModel, Field, field_validator
from typing import Any
from schema_base import StrEnumBase


class DocumentCategoryEnum(StrEnumBase):
    IDENTITY_VERIFICATION_DOCUMENT = "identity_verification_document"
    BANK_STATEMENT = "bank_statement"
    INCOME_DOCUMENT = "income_document"
    EXPENDITURE = "expenditure"
    CREDIT_REPORT = "credit_report"
    OTHER = "other"
    UNKNOWN = "unknown"


class DocumentTypeEnum(StrEnumBase):
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"
    NATIONAL_IDENTITY_CARD = "national_identity_card"
    BANK_STATEMENT = "bank_statement"
    PAYSLIP = "payslip"
    P60 = "p60"
    CONTRACT_OF_EMPLOYMENT = "contract_of_employment"
    MARRIAGE_CERTIFICATE = "marriage_certificate"
    PRE_MATERNITY_PAYSLIP = "pre_maternity_payslip"
    PENSION_PAYSLIP = "pension_payslip"
    ANNUAL_PENSION_STATEMENT = "pension_annual_statement"
    EMPLOYER_LETTER = "letter_from_employer"
    CREDIT_TRANSUNION = "transunion"
    CREDIT_EXPERIAN = "experian"
    OTHER = "other"
    UNKNOWN = "unknown"


# mapping dictionaries to fix name mismatches
CATEGORY_MAPPING = {
    "income": DocumentCategoryEnum.INCOME_DOCUMENT.value,
    "income_document": DocumentCategoryEnum.INCOME_DOCUMENT.value,
    "id proof": DocumentCategoryEnum.IDENTITY_VERIFICATION_DOCUMENT.value,
    "identity": DocumentCategoryEnum.IDENTITY_VERIFICATION_DOCUMENT.value,
    "identity_document": DocumentCategoryEnum.IDENTITY_VERIFICATION_DOCUMENT.value,
    "identity_verification_document": DocumentCategoryEnum.IDENTITY_VERIFICATION_DOCUMENT.value,
    "expenditure": DocumentCategoryEnum.EXPENDITURE.value,
    "bank statement": DocumentCategoryEnum.BANK_STATEMENT.value,
    "credit report": DocumentCategoryEnum.CREDIT_REPORT.value,
}

TYPE_MAPPING = {
    "pay slip": DocumentTypeEnum.PAYSLIP.value,
    "payslip": DocumentTypeEnum.PAYSLIP.value,
    "p60": DocumentTypeEnum.P60.value,
    "marriage certificate": DocumentTypeEnum.MARRIAGE_CERTIFICATE.value,
    "contract of employment": DocumentTypeEnum.CONTRACT_OF_EMPLOYMENT.value,
    "previous contract of employment": DocumentTypeEnum.CONTRACT_OF_EMPLOYMENT.value,
    "pre maternity pay slip": DocumentTypeEnum.PRE_MATERNITY_PAYSLIP.value,
    "annual pension scheme statement": DocumentTypeEnum.ANNUAL_PENSION_STATEMENT.value,
    "confirmation of pension scheme": DocumentTypeEnum.ANNUAL_PENSION_STATEMENT.value,
    "pension pay slip": DocumentTypeEnum.PENSION_PAYSLIP.value,
    "pension annual statement": DocumentTypeEnum.ANNUAL_PENSION_STATEMENT.value,
    "uk paaport": DocumentTypeEnum.PASSPORT.value,  # typo fixed
    "passport": DocumentTypeEnum.PASSPORT.value,
    "share code": DocumentTypeEnum.NATIONAL_IDENTITY_CARD.value,
    "indefinite leave to remain": DocumentTypeEnum.NATIONAL_IDENTITY_CARD.value,
    "bank statements": DocumentTypeEnum.BANK_STATEMENT.value,
    "transunion": DocumentTypeEnum.CREDIT_TRANSUNION.value,
    "experian": DocumentTypeEnum.CREDIT_EXPERIAN.value,
}


class DocumentCategoryAndType(BaseModel):
    document_category: str = Field(..., description="Category of the document")
    document_type: str = Field(..., description="Type of the document")

    @field_validator("document_category", mode="before")
    @classmethod
    def _coerce_category(cls, v: Any) -> str:
        if v is None:
            return DocumentCategoryEnum.UNKNOWN.value
        s = str(v).strip().lower()
        return CATEGORY_MAPPING.get(s, s.replace(" ", "_").replace("-", "_"))

    @field_validator("document_type", mode="before")
    @classmethod
    def _coerce_type(cls, v: Any) -> str:
        if v is None:
            return DocumentTypeEnum.UNKNOWN.value
        s = str(v).strip().lower()
        return TYPE_MAPPING.get(s, s.replace(" ", "_").replace("-", "_"))
