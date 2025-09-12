from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import regex

from app.core.exception_handler import BadRequestException, ValidationException

class CreateUsecaseRequest(BaseModel):
    name: str

    @field_validator("name")
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


class UpdateUsecaseRequest(BaseModel):
    name: str

    @field_validator("name")
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
