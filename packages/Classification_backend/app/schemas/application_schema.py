from datetime import datetime
import json
from typing import Any, Dict, List, Optional
from fastapi import Form
from pydantic import BaseModel

from app.db.models import Application, ApplicationStatus, UnderwriterStatus


class ApplicationResponse(BaseModel):
    """
    Application response schema
    """
    application_id: str
    application_type: str
    status: ApplicationStatus
    underwriter_status: UnderwriterStatus
    underwriter_review: str | None = None
    document_result: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

    @classmethod
    def from_orm(cls, application: Application):
        """
        Create a new ApplicationResponse from an Application model
        """ 
        return cls(
            application_id=application.underwriting_application_id,
            application_type=application.application_type.application_type_code,
            status=application.status,
            underwriter_status=application.underwriter_status,
            underwriter_review=application.underwriter_review,
            document_result=application.document_result,
            created_at=application.created_at,
            updated_at=application.updated_at,
            created_by=application.creator.name,
            updated_by=application.updator.name,
        )


class GetApplicationsResponse(BaseModel):
    """
    Get applications response schema
    """
    applications: List[ApplicationResponse]
    total: int

    @classmethod
    def from_orm(cls, applications: List[Application], total: int):
        """
        Create a new GetApplicationsResponse from a list of Application models
        """
        return cls(
            applications=[ApplicationResponse.from_orm(application) for application in applications],
            total=total,
        )


class CreateApplicationRequest(BaseModel):
    """
    Create application request schema
    """
    application_type: str = Form(...)
    application_id: str = Form(...)


class CreateApplicationResponse(BaseModel):
    application_id: str
    application_type: str
    classification_overall_result: bool
    classification_results: list


class UpdateApplicationRequest(BaseModel):
    """
    Update application request schema
    """
    underwriter_status: UnderwriterStatus
    underwriter_review: str
