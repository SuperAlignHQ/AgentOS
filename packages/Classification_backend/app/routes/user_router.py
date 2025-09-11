from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config_manager import ConfigManager
from app.core.exception_handler import (
    BadRequestException,
    DatabaseException,
    NotFoundException,
    ValidationException,
)
from app.core.logging_config import logger
from app.core.util import authorize_user, get_current_user, get_db_session
from app.db.models import ActionTypeEnum, Org, Role, TargetEnum, User
from app.schemas.user_schema import (
    CreateUserRequest,
    GetUsersResponse,
    UserProfileRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.schemas.util import EmptyResponse, PaginationQuery
from app.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["User"])


def get_user_service() -> UserService:
    return ConfigManager.get_instance().user_service


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    try:
        # authorize_user()

        return UserResponse.from_user(user)
    except Exception as e:
        logger.error(f"Error in get_user_profile: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to retrieve user profile: {str(e)}")


@router.get("/org", response_model=List[Org])
async def get_user_orgs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get user orgs
    """
    try:
        # authorize_user(user.role, None, TargetEnum.USER, ActionTypeEnum.READ)

        return await user_service.get_user_orgs(db, user)
    except Exception as e:
        logger.error(f"Error in get_user_orgs: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to retrieve user organizations: {str(e)}")


# !TODO REMOVE THIS ROUTE
@router.post("", response_model=EmptyResponse)
async def create_user(
    request_data: CreateUserRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
):
    """
    Create user
    """
    try:
        # authorize_user(user.role, None, TargetEnum.USER, ActionTypeEnum.CREATE)

        # Validate input data
        if not request_data.user_name:
            raise BadRequestException("User name is required")

        if not request_data.role:
            raise BadRequestException("Role is required")

        existing_user = await db.exec(
            select(User).where(User.name == request_data.user_name)
        )
        existing_user = existing_user.first()
        if existing_user:
            raise ValidationException(message="User already exists")

        role = await db.exec(select(Role).where(Role.name == request_data.role))
        role = role.first()
        if not role:
            raise ValidationException(message="Role does not exist")

        create_user = User(
            name=request_data.user_name,
            role_id=role.role_id,
        )
        db.add(create_user)
        await db.commit()
        await db.refresh(create_user)

        return EmptyResponse(message="User created successfully")
    except (ValidationException, BadRequestException):
        raise
    except Exception as e:
        logger.error(f"Error in create_user: {str(e)}", exc_info=True)
        await db.rollback()
        raise DatabaseException(f"Failed to create user: {str(e)}")


@router.get("", response_model=GetUsersResponse)
async def get_all_users(
    pagination: PaginationQuery = Depends(),
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get all users
    """
    try:
        authorize_user(user.role, None, TargetEnum.USER, ActionTypeEnum.READ)

        return await user_service.get_all_users(db, pagination)
    except (ValidationException, BadRequestException) as e:
        logger.error(f"Error in get_all_users: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in get_all_users: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to retrieve users: {str(e)}")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    try:
        authorize_user(user.role, None, TargetEnum.USER, ActionTypeEnum.READ)

        return await user_service.get_user_by_id(user_id, db)
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in get_user_by_id: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in get_user_by_id: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to retrieve user: {str(e)}")


@router.put("", response_model=UserResponse)
async def update_user_profile(
    update_data: UserProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update user profile
    """
    try:
        # authorize_user()

        return await user_service.update_user_profile(db, update_data, user)
    except (ValidationException, BadRequestException, NotFoundException) as e:
        logger.error(f"Error in update_user_profile: {str(e)}")
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error in update_user_profile: {str(e)}", exc_info=True
        )
        raise DatabaseException(f"Failed to update user profile: {str(e)}")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    user_id: UUID,
    update_data: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update user by id
    """
    try:
        authorize_user(user.role, None, TargetEnum.USER, ActionTypeEnum.UPDATE)

        return await user_service.update_user_by_id(user_id, update_data, db, user)
    except (ValidationException, BadRequestException, NotFoundException) as e:
        logger.error(f"Error in update_user_by_id: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in update_user_by_id: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to update user: {str(e)}")


@router.delete("/{user_id}", response_model=EmptyResponse)
async def delete_user_by_id(
    user_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
):
    """
    Delete user by id
    """
    try:
        authorize_user(user.role, None, TargetEnum.USER, ActionTypeEnum.DELETE)

        return await user_service.delete_user_by_id(user_id, db, user)
    except (ValidationException, BadRequestException, NotFoundException) as e:
        logger.error(f"Error in delete_user_by_id: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in delete_user_by_id: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to delete user: {str(e)}")
