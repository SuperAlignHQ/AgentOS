from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import regex

from app.core.exception_handler import ValidationException

class CreateUsecaseRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        try:
            ans = regex.match(".*\S.*", value)
            if not ans:
                raise ValidationException("Name cannot contain only whitespaces")
            updated_value = value.strip()

            if not value:
                raise ValidationException("Name cannot be empty")

            return updated_value
        except ValidationException as e:
            JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": e.message,
                "details": e.details,
                "path": "",
            },
        )


class UpdateUsecaseRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        try:
            ans = regex.match(".*\S.*", value)
            if not ans:
                raise ValidationException("Name cannot contain only whitespaces")
            updated_value = value.strip()

            if not value:
                raise ValidationException("Name cannot be empty")

            return updated_value
        except ValidationException as e:
            JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": e.message,
                "details": e.details,
                "path": "",
            },
        )