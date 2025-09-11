from typing import Optional
from fastapi import status, Request
from fastapi.responses import JSONResponse

from app.core.logging_config import logger


class AppException(Exception):
    """Base Exception for the application"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(
        self, message: str = "Resource not found", details: Optional[dict] = None
    ):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class BadRequestException(AppException):
    def __init__(self, message: str = "Bad Request", details: Optional[dict] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized", details: Optional[dict] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class ValidationException(AppException):
    def __init__(
        self, message: str = "Validation Failed", details: Optional[dict] = None
    ):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden", details: Optional[dict] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class ConflictException(AppException):
    def __init__(
        self, message: str = "Resource Conflict", details: Optional[dict] = None
    ):
        super().__init__(message, status.HTTP_409_CONFLICT, details)


class DatabaseException(AppException):
    def __init__(
        self, message: str = "Database Operation Failed", details: Optional[dict] = None
    ):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)


class FileProcessingException(AppException):
    def __init__(
        self, message: str = "File Processing Failed", details: Optional[dict] = None
    ):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)


class ServiceUnavailableException(AppException):
    def __init__(
        self, message: str = "Service Unavailable", details: Optional[dict] = None
    ):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, details)


class Exceptionhandler:
    @staticmethod
    def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.error(f"AppException: {exc.message} | Details: {exc.details}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.message,
                "details": exc.details,
                "path": request.url.path,
            },
        )

    @staticmethod
    def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Server Error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal Server Error",
                "details": {},
                "path": request.url.path,
            },
        )
