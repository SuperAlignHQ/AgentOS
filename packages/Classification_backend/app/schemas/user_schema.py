from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel

from app.db.models import User


class UserResponse(BaseModel):
    """
    User response schema
    """

    user_id: UUID
    user_name: str
    role: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_user(cls, user: User):
        return cls(
            user_id=user.user_id,
            user_name=user.name,
            role=user.role.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UserProfileRequest(BaseModel):
    """
    User profile request schema
    """

    user_name: str


class UserUpdateRequest(BaseModel):
    """
    User update request schema
    """

    role: str


class GetUsersResponse(BaseModel):
    """
    Get users response schema
    """

    users: List[UserResponse]
    total: int


class CreateUserRequest(BaseModel):
    """
    Create user request schema
    """

    user_name: str
    role: str
