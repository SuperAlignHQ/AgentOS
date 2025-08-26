from typing import List, Optional
from fastapi import UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.util import validate_application_type
from app.db.models import Application, Org, Usecase
from app.repositories.application_repo import ApplicationRepo
from app.schemas.util import PaginationQuery
from app.schemas.application_schema import CreateApplicationRequest, GetApplicationsResponse


class ApplicationService:
    """
    Application service class
    """
    _instance = None
    application_repo: ApplicationRepo

    def __init__(self) -> None:
        if ApplicationService._instance is not None:
            raise RuntimeError("Use get_instance to get an instance of Application Service")

        self.application_repo = ApplicationRepo().get_instance()

    @classmethod
    def get_instance(cls):
        """
        Get instance of ApplicationService
        """
        if not cls._instance:
            cls._instance = cls()

        return cls._instance

    async def get_all_applications(self, org: Org, usecase: Usecase, pagination: PaginationQuery, db: AsyncSession) -> GetApplicationsResponse:
        """
        Get all applications
        """
        applications, total = await self.application_repo.get_all_applications(org, usecase, pagination, db)
        return GetApplicationsResponse(applications=applications, total=total)

    async def get_application_by_underwriting_id(self, underwriting_id: str, db: AsyncSession) -> Optional[Application]:
        """
        Get application by underwriting id
        """

        application = await db.exec(select(Application).where(Application.underwriting_application_id == underwriting_id))
        return application.first()

    async def create_application(self, org: Org, usecase: Usecase, application_data: CreateApplicationRequest, files: List[UploadFile], db: AsyncSession) -> None:
        """
        Create application
        """
        # validate application data
        application_type = await validate_application_type(application_data.application_type, db)

        # get application if already exist
        application = await self.get_application_by_underwriting_id(application_data.application_id, db)

        if not application:
            application = await self.application_repo.create_application(org, usecase, application_data, application_type, files, db)

        # for file in files:
            #validate file

            # build document model for database

            # build ocr request

            # upload document to gcs

        # send ocr request

        # supdate document models as per ocr response

        # save document models in db

        # build document result json for application response 

        # update application as per document result

        # return response