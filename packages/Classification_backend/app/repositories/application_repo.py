from typing import List, Tuple
from uuid import UUID

from sqlmodel import false, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exception_handler import DatabaseException
from app.core.logging_config import logger
from app.db.models import Application, ApplicationType, ApplicationTypeDocumentTypeAssociation, Org, Usecase, User
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

    async def get_all_applications(
        self, org: Org, usecase: Usecase, pagination: PaginationQuery, db: AsyncSession
    ) -> Tuple[List[Application], int]:
        """Get all applications"""
        try:
            query = select(Application).where(
                Application.usecase_id == usecase.usecase_id
            )
            query = query.offset((pagination.page - 1) * pagination.page_size)
            query = query.limit(pagination.page_size)
            result = await db.exec(query)
            applications = result.all()

            total = await db.exec(
                select(func.count())
                .select_from(Application)
                .where(Application.usecase_id == usecase.usecase_id)
            )
            return applications, total.first()
        except Exception as e:
            logger.error(f"Error in get_all_applications: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")

    async def create_application(
        self,
        org: Org,
        usecase: Usecase,
        application_data: CreateApplicationRequest,
        application_type: ApplicationType,
        user: User,
        db: AsyncSession,
    ) -> Application:
        """
        Create application
        """
        try:
            application = Application(
                underwriting_application_id=application_data.application_id,
                application_type_id=application_type.application_type_id,
                usecase_id=usecase.usecase_id,
                created_by=user.user_id,
                updated_by=user.user_id,
            )

            document_result = []
            # get all document application type associations for application type
            associations = await db.exec(
                select(
                    ApplicationTypeDocumentTypeAssociation).where(
                        ApplicationTypeDocumentTypeAssociation.usecase_id == usecase.usecase_id,
                        ApplicationTypeDocumentTypeAssociation.application_type_id == application_type.application_type_id
                    )
                )
            associations = associations.all()

            for association in associations:
                document_result.append({
                    "document_category": association.document_type.category,
                    "document_type": association.document_type.name,
                    "optional": association.is_optional,
                    "result": False,
                    "reason": f"{association.document_type.name} is missing from the application"
                })

            application.document_result = document_result

            db.add(application)
            await db.commit()
            await db.refresh(application)
            return application
        except Exception as e:
            logger.error(f"Error in create_application: {str(e)}", exc_info=True)
            await db.rollback()
            raise DatabaseException(f"{str(e)}")
