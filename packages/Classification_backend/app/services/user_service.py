from datetime import datetime, timezone
from typing import List
from uuid import UUID
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exception_handler import BadRequestException, DatabaseException, NotFoundException
from app.core.logging_config import logger
from app.db.models import ActionTypeEnum, AuditLog, Org, OrgMember, Role, RoleType, TargetEnum, User
from app.schemas.user_schema import GetUsersResponse, UserProfileRequest, UserResponse, UserUpdateRequest
from app.schemas.util import EmptyResponse, PaginationQuery
from app.core.exception_handler import ForbiddenException

ORG_ADMIN = "org_admin"
APP_ADMIN = "app_admin"


class UserService:
    """
    User service class
    """

    _instance = None
    # user_repo: UserRepo

    def __init__(self) -> None:
        if UserService._instance is not None:
            raise RuntimeError("Use get_instance to get an instance of User Service")

        # self.user_repo = UserRepo.get_instance()

    @classmethod
    def get_instance(cls):
        """
        Get instance of UserService
        """
        if not cls._instance:
            cls._instance = cls()

        return cls._instance

    async def get_all_users(self, db: AsyncSession, pagination: PaginationQuery) -> GetUsersResponse:
        """
        Get all users
        """
        try:
            offset = (pagination.page - 1) * pagination.page_size
            limit = pagination.page_size

            users = await db.exec(select(User).offset(offset).limit(limit))
            users = users.all()

            total = await db.exec(select(func.count()).select_from(User))
            total = total.first()

            return GetUsersResponse(users=[UserResponse.from_user(user) for user in users], total=total)
        except Exception as e:
            logger.error(f"Error in get_all_users: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")

    async def get_user_by_id(self, user_id: UUID, db: AsyncSession) -> UserResponse:
        """
        Get user by id
        """
        try:
            user = await db.get(User, user_id)
            if not user:
                raise NotFoundException(f"User with id {user_id} not found")
            return UserResponse.from_user(user)
        except Exception as e:
            logger.error(f"Error in get_user_by_id: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")

    async def update_user_profile(self, db: AsyncSession, update_data: UserProfileRequest, user: User) -> UserResponse:
        """
        Update user profile
        """
        try:
            user.name = update_data.user_name
            user.updated_at = datetime.now(timezone.utc)
        except Exception as e:
            logger.error(f"Error in update_user_profile: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")
        try:
            await db.commit()
            await db.refresh(user)
        except Exception as e:
            logger.error(f"Error in update_user_profile: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")
        try:
            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.UPDATE,
                    title=f"User '{user.name}' updated",
                    target_name=TargetEnum.USER,
                    org_id=None,
                    actor_id=user.user_id,
                    target_id=user.user_id,
                )
            )
            return UserResponse.from_user(user)
        except Exception as e:
            logger.error(f"Error in update_user_profile: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")

    async def update_user_by_id(self, user_id: UUID, update_data: UserUpdateRequest, db: AsyncSession, user: User) -> UserResponse:
        """
        Update user by id
        """
        try:
            update_user = await db.get(User, user_id)
            if not update_user:
                raise NotFoundException(f"User with id {user_id} not found")

            if update_user.user_id == user.user_id:
                raise BadRequestException("Cannot update own role!")

            role = await db.exec(select(Role).where(update_data.role.lower() == Role.name))
            role = role.first()
            if not role:
                raise NotFoundException("Role not found!")

            if role.type == RoleType.ORG:
                raise BadRequestException("Invalid user role!")

            if update_user.role.role_id == role.role_id:
                raise BadRequestException(f"User is already assigned to role '{role.name}'")

            # if user.role.name == ORG_ADMIN and (update_user.role.name == APP_ADMIN or role.name == APP_ADMIN):
            #     raise ForbiddenException("Not authorized to update the role")

            update_user.role_id = role.role_id
            update_user.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(update_user)

            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.UPDATE,
                    title=f"User '{update_user.name}' role updated to '{role.name}'",
                    target_name=TargetEnum.USER,
                    org_id=None,
                    actor_id=user.user_id,
                    target_id=update_user.user_id,
                )
            )
            return UserResponse.from_user(update_user)
        except Exception as e:
            logger.error(f"Error in update_user_by_id: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")

    async def delete_user_by_id(self, user_id: UUID, db: AsyncSession, user: User) -> EmptyResponse:
        """
        Delete user by id
        """
        try:
            delete_user = await db.get(User, user_id)
            if not delete_user:
                raise NotFoundException(f"User with id {user_id} not found")

            # remove user from all orgs
            await db.exec(delete(OrgMember).where(OrgMember.user_id == delete_user.user_id))
            await db.delete(delete_user)
            await db.commit()

            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.DELETE,
                    title=f"User '{delete_user.name}' deleted",
                    target_name=TargetEnum.USER,
                    org_id=None,
                    actor_id=user.user_id,
                    target_id=delete_user.user_id,
                )
            )
            return EmptyResponse(message="User deleted successfully!")
        except Exception as e:
            logger.error(f"Error in delete_user_by_id: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")

    async def get_user_orgs(self, db: AsyncSession, user: User) -> List[Org]:
        """
        Get user orgs
        """
        try:
            query = select(Org).join(OrgMember, Org.org_id == OrgMember.org_id).where(OrgMember.user_id == user.user_id)
            orgs = await db.exec(query)
            orgs = orgs.all()
            return orgs
        except Exception as e:
            logger.error(f"Error in get_user_orgs: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")
