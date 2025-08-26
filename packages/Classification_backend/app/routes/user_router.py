from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config_manager import ConfigManager
from app.core.exception_handler import ValidationException
from app.core.util import authorize_user, get_current_user, get_db_session
from app.db.models import ActionTypeEnum, Org, Role, TargetEnum, User
from app.schemas.user_schema import CreateUserRequest, GetUsersResponse, UserProfileRequest, UserResponse, UserUpdateRequest
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

    # authorize_user()

    return UserResponse.from_user(user)

@router.get("/org", response_model=List[Org])
async def get_user_orgs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get user orgs
    """
    # authorize_user(user.role, None, TargetEnum.USER, ActionTypeEnum.READ)

    return await user_service.get_user_orgs(db, user)



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
    # authorize_user(user.role, None, TargetEnum.USER, ActionTypeEnum.CREATE)

    existing_user = await db.exec(select(User).where(User.name == request_data.user_name))
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
    authorize_user(user.role, None, TargetEnum.USER, ActionTypeEnum.READ)

    return await user_service.get_all_users(db, pagination)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):

    authorize_user(user.role, None, TargetEnum.USER, ActionTypeEnum.READ)

    return await user_service.get_user_by_id(user_id, db)




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
    # authorize_user()

    return await user_service.update_user_profile(db, update_data, user)


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
    authorize_user(user.role, None, TargetEnum.USER, ActionTypeEnum.UPDATE)

    return await user_service.update_user_by_id(user_id, update_data, db, user)


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
    authorize_user(user.role, None, TargetEnum.USER, ActionTypeEnum.DELETE)

    return await user_service.delete_user_by_id(user_id, db, user)
