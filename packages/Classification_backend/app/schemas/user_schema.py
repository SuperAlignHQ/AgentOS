from datetime import datetime
from typing import List
from uuid import UUID
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import regex

from app.core.exception_handler import BadRequestException, ValidationException
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

    @field_validator("user_name")
    @classmethod
    def validate_name(cls, value: str):
        try:
            ans = regex.match(r".*\S.*", value)
            if not ans:
                raise ValidationException("Name cannot contain only whitespaces")
            updated_value = value.strip()

            if not value:
                raise ValidationException("Name cannot be empty")

            return updated_value
        except ValidationException as e:
            raise BadRequestException(
                message=e.message,
                details=e.details,
            )


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

    @field_validator("user_name")
    @classmethod
    def validate_name(cls, value: str):
        try:
            ans = regex.match(r".*\S.*", value)
            if not ans:
                raise ValidationException("Name cannot contain only whitespaces")
            updated_value = value.strip()

            if not value:
                raise ValidationException("Name cannot be empty")

            return updated_value
        except ValidationException as e:
            raise BadRequestException(
                message=e.message,
                details=e.details,
            )
