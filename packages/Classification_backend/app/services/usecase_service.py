from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exception_handler import NotFoundException
from app.core.logging_config import logger
from app.db.models import ActionTypeEnum, AuditLog, Org, TargetEnum, Usecase, User
from app.schemas.usecase_schema import CreateUsecaseRequest, UpdateUsecaseRequest


class UsecaseService:
    """
    Usecase service class
    """

    _instance = None
    # usecase_repo: UsecaseRepo

    def __init__(self) -> None:
        if UsecaseService._instance is not None:
            raise RuntimeError("Use get_instance to get an instance of Usecase Service")

        # self.usecase_repo = UsecaseRepo.get_instance()

    @classmethod
    def get_instance(cls):
        """
        Get instance of UsecaseService
        """
        if not cls._instance:
            cls._instance = cls()

        return cls._instance

    async def get_usecase_by_id(self, usecase_id: UUID, db: AsyncSession) -> Optional[Usecase]:
        """
        Get usecase by id
        """
        try:
            usecase = await db.get(Usecase, usecase_id)
            if not usecase:
                raise NotFoundException(f"Usecase with id {usecase_id} not found")
            return usecase
        except Exception as e:
            logger.error(f"Error in get_usecase_by_id: {e}")
            raise e

    async def get_usecases(self, db: AsyncSession, user: User, org: Org) -> List[Usecase]:
        """
        Get all usecases
        """
        try:
            usecases = await db.exec(select(Usecase).where(Usecase.org_id == org.org_id))
            return usecases.all()
        except Exception as e:
            logger.error(f"Error in get_usecases: {e}")
            raise e

    async def create_usecase(self, db: AsyncSession, user: User, org: Org, usecase: CreateUsecaseRequest) -> Usecase:
        """
        Create usecase
        """
        try:
            usecase_model = Usecase(
                name=usecase.name,
                org_id=org.org_id,
                created_by=user.user_id,
                updated_by=user.user_id
            )
            db.add(usecase_model)
            await db.commit()
            await db.refresh(usecase_model)

            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.CREATE,
                    title=f"Usecase '{usecase_model.name}' created",
                    target_name=TargetEnum.USECASE,
                    org_id=org.org_id,
                    actor_id=user.user_id,
                    target_id=usecase_model.usecase_id,
                )
            )
            return usecase_model
        except Exception as e:
            logger.error(f"Error in create_usecase: {e}")
            raise e

    async def update_usecase(self, db: AsyncSession, user: User, org: Org, usecase: Usecase, update_data: UpdateUsecaseRequest) -> Usecase:
        """
        Update usecase
        """
        try:
            usecase.name = update_data.name
            usecase.updated_by = user.user_id
            usecase.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(usecase)

            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.UPDATE,
                    title=f"Usecase '{usecase.name}' updated",
                    target_name=TargetEnum.USECASE,
                    org_id=org.org_id,
                    actor_id=user.user_id,
                    target_id=usecase.usecase_id,
                )
            )
            return usecase
        except Exception as e:
            logger.error(f"Error in update_usecase: {e}")
            raise e

    async def delete_usecase(self, db: AsyncSession, user: User, org: Org, usecase: Usecase) -> None:
        """
        Delete usecase
        """
        try:
            await db.delete(usecase)
            await db.commit()

            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.DELETE,
                    title=f"Usecase '{usecase.name}' deleted",
                    target_name=TargetEnum.USECASE,
                    org_id=org.org_id,
                    actor_id=user.user_id,
                    target_id=usecase.usecase_id,
                )
            )
        except Exception as e:
            logger.error(f"Error in delete_usecase: {e}")
            raise e
