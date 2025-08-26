

from typing import List, Tuple
from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models import Application, ApplicationType, Org, Usecase
from app.schemas.application_schema import CreateApplicationRequest
from app.schemas.util import PaginationQuery


class ApplicationRepo:
    _instance = None

    def __init__(self) -> None:
        if ApplicationRepo._instance is not None:
            raise Exception("Repositories can't be initialized out of service class")

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()

        return cls._instance

    async def get_all_applications(self, org: Org, usecase: Usecase, pagination: PaginationQuery, db: AsyncSession) -> Tuple[List[Application], int]:
        """Get all applications"""
        query = select(Application).where(Application.usecase_id == usecase.usecase_id)
        query = query.offset((pagination.page - 1) * pagination.page_size)
        query = query.limit(pagination.page_size)
        result = await db.exec(query)
        applications = result.all()

        total = await db.exec(select(func.count()).select_from(Application).where(Application.usecase_id == usecase.usecase_id))
        return applications, total.first()


    async def create_application(self, org: Org, usecase: Usecase, application_data: CreateApplicationRequest, application_type: ApplicationType, db: AsyncSession) -> Application:
        """
        Create application
        """
        application = Application(
            underwriting_application_id=application_data.application_id,
            application_type_id=application_type.application_type_id,
            usecase_id=usecase.usecase_id,
            created_by=org.member_id,
            updated_by=org.member_id
        )
        db.add(application)
        await db.commit()
        await db.refresh(application)
        return application