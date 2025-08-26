from typing import List, Optional
from fastapi import UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.exception_handler import (
    BadRequestException,
    ConflictException,
    DatabaseException,
    FileProcessingException,
    NotFoundException,
    ValidationException,
)
from app.core.logging_config import logger
from app.core.util import validate_application_type
from app.db.models import Application, Org, Usecase
from app.repositories.application_repo import ApplicationRepo
from app.schemas.util import PaginationQuery
from app.schemas.application_schema import (
    CreateApplicationRequest,
    GetApplicationsResponse,
)


class ApplicationService:
    """
    Application service class
    """

    _instance = None
    application_repo: ApplicationRepo

    def __init__(self) -> None:
        if ApplicationService._instance is not None:
            raise RuntimeError(
                "Use get_instance to get an instance of Application Service"
            )

        self.application_repo = ApplicationRepo().get_instance()

    @classmethod
    def get_instance(cls):
        """
        Get instance of ApplicationService
        """
        if not cls._instance:
            cls._instance = cls()

        return cls._instance

    async def get_all_applications(
        self, org: Org, usecase: Usecase, pagination: PaginationQuery, db: AsyncSession
    ) -> GetApplicationsResponse:
        """
        Get all applications
        """
        try:
            applications, total = await self.application_repo.get_all_applications(
                org, usecase, pagination, db
            )
            return GetApplicationsResponse(applications=applications, total=total)
        except Exception as e:
            logger.error(f"Error in get_all_applications: {str(e)}", exc_info=True)
            raise DatabaseException(f"Failed to retrieve applications: {str(e)}")

    async def get_application_by_underwriting_id(
        self, underwriting_id: str, db: AsyncSession
    ) -> Optional[Application]:
        """
        Get application by underwriting id
        """
        try:
            if not underwriting_id:
                raise BadRequestException("Underwriting ID is required")

            application = await db.exec(
                select(Application).where(
                    Application.underwriting_application_id == underwriting_id
                )
            )
            return application.first()
        except BadRequestException:
            raise
        except Exception as e:
            logger.error(
                f"Error in get_application_by_underwriting_id: {str(e)}", exc_info=True
            )
            raise DatabaseException(f"Failed to retrieve application: {str(e)}")

    async def create_application(
        self,
        org: Org,
        usecase: Usecase,
        application_data: CreateApplicationRequest,
        files: List[UploadFile],
        db: AsyncSession,
    ) -> None:
        """
        Create application
        """
        try:
            # Validate input data
            if not application_data.application_id:
                raise BadRequestException("Application ID is required")

            if not application_data.application_type:
                raise BadRequestException("Application type is required")

            if not files:
                raise BadRequestException("At least one file is required")

            # Validate application data
            application_type = await validate_application_type(
                application_data.application_type, db
            )

            # Check if application already exists
            existing_application = await self.get_application_by_underwriting_id(
                application_data.application_id, db
            )

            if existing_application:
                raise ConflictException(
                    f"Application with ID {application_data.application_id} already exists"
                )

            # Create application
            application = await self.application_repo.create_application(
                org, usecase, application_data, application_type, files, db
            )

            # TODO: Implement file processing logic
            # for file in files:
            #     # validate file
            #     # build document model for database
            #     # build ocr request
            #     # upload document to gcs
            #     # send ocr request
            #     # update document models as per ocr response
            #     # save document models in db
            #     # build document result json for application response
            #     # update application as per document result

            return application

        except (BadRequestException, ConflictException, ValidationException):
            raise
        except Exception as e:
            logger.error(f"Error in create_application: {str(e)}", exc_info=True)
            raise DatabaseException(f"Failed to create application: {str(e)}")
