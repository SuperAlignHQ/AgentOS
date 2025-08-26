from typing import Optional
from uuid import UUID
from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exception_handler import (
    DatabaseException,
    UnauthorizedException,
    ValidationException,
)
from app.core.logging_config import logger
from app.db.models import (
    ActionTypeEnum,
    ApplicationType,
    Org,
    OrgMember,
    Role,
    TargetEnum,
    Usecase,
    User,
)
from app.services.user_service import APP_ADMIN


async def get_db_session() -> AsyncSession:
    from app.core.config_manager import ConfigManager

    try:
        db = ConfigManager.get_instance().database

        async with db.session_factory() as session:
            yield session
    except SQLAlchemyError as e:
        logger.error("Database session error occurred.", str(e), exc_info=True)
        raise e
    except Exception as e:
        logger.error(f"Error while getting database session: {str(e)}")
        raise e


async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
) -> Optional[User]:
    try:
        user = await db.exec(
            select(User).where(User.user_id == "dfef8c9e-e06a-46fc-a89a-0f4b1e5c8133")
        )
        user_result = user.first()
        if not user_result:
            raise UnauthorizedException("User not found")
        return user_result
    except UnauthorizedException:
        raise
    except Exception as e:
        logger.error(f"Failed to authenticate user: {str(e)}", exc_info=True)
        raise DatabaseException(f"Authentication failed: {str(e)}")


def authorize_user(
    user_role: Role,
    member_role: Optional[Role],
    resource: TargetEnum,
    action: ActionTypeEnum,
):
    """
    Authorize user based on role, member role, resource, and action
    """
    if user_role.name == APP_ADMIN:
        return True

    if member_role is None:
        if (
            user_role.permissions
            and user_role.permissions.get(resource.value)
            and action.value in user_role.permissions.get(resource.value)
        ):
            return True

    if (
        member_role
        and member_role.permissions.get(resource.value)
        and (action.value in member_role.permissions.get(resource.value))
    ):
        return True

    raise UnauthorizedException(message="User is not authorized to perform this action")


async def validate_org_member(org: UUID, user: User, db: AsyncSession) -> OrgMember:
    if user.role.name == APP_ADMIN:
        return

    org_member = await db.exec(
        select(OrgMember).where(
            OrgMember.org_id == org, OrgMember.user_id == user.user_id
        )
    )
    org_member = org_member.first()
    if not org_member:
        raise ValidationException(message="User is not a member of the organisation")
    return org_member


def validate_org_usecase(org: Org, usecase: Usecase):
    if org.org_id != usecase.org_id:
        raise ValidationException(message="Usecase does not belong to the organisation")


async def validate_application_type(
    application_type: str, db: AsyncSession
) -> ApplicationType:
    """
    Validate application type
    """
    try:
        application_type = await db.exec(
            select(ApplicationType).where(
                ApplicationType.application_type_code == application_type
            )
        )
        if not application_type:
            raise ValidationException(message="Application type does not exist")
        return application_type.scalar_one()
    except ValidationException as e:
        logger.error(f"Failed to validate application type: {str(e)}")
        raise e
    except SQLAlchemyError as e:
        logger.error(f"Database error while validating application type: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Failed to validate application type: {str(e)}")
        raise e
