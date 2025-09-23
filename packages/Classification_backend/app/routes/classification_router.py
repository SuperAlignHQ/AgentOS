import json
from typing import List
from uuid import UUID
from fastapi import APIRouter, Body, Depends, File, Form, UploadFile
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config_manager import ConfigManager
from app.core.exception_handler import (
    BadRequestException,
    DatabaseException,
    FileProcessingException,
    NotFoundException,
    ValidationException,
)
from app.core.logging_config import logger
from app.core.util import (
    authorize_user,
    get_current_user,
    get_db_session,
    validate_file,
    validate_org_member,
    validate_org_usecase,
)
from app.db.models import ActionTypeEnum, Application, TargetEnum, User
from app.schemas.application_schema import (
    ApplicationResponse,
    CreateApplicationRequest,
    CreateApplicationResponse,
    GetApplicationsResponse,
    UpdateApplicationRequest,
)
from app.schemas.util import EmptyResponse, PaginationQuery
from app.services.application_service import ApplicationService


router = APIRouter(
    prefix="/org/{org_id}/usecase/{usecase_id}/classification",
    tags=["Classification"],
)


def get_application_service() -> ApplicationService:
    return ConfigManager.get_instance().application_service


@router.get("", response_model=GetApplicationsResponse)
async def get_all_applications(
    org_id: UUID,
    usecase_id: UUID,
    pagination: PaginationQuery = Depends(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    application_service: ApplicationService = Depends(get_application_service),
):
    """Get all Applications"""
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(
            user.role,
            org_member.role if org_member else None,
            TargetEnum.APPLICATION,
            ActionTypeEnum.READ,
        )

        config_manager = ConfigManager.get_instance()
        org = await config_manager.org_service.get_org_by_id(org_id, db)
        usecase = await config_manager.usecase_service.get_usecase_by_id(usecase_id, db)

        validate_org_usecase(org, usecase)

        return await application_service.get_all_applications(
            org, usecase, pagination, db
        )
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in get_all_applications: {str(e)}")
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error in get_all_applications: {str(e)}", exc_info=True
        )
        raise DatabaseException(f"Failed to retrieve applications: {str(e)}")


@router.get("/{application_id}", response_model=Application)
async def get_application_by_id(
    org_id: UUID,
    usecase_id: UUID,
    application_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    application_service: ApplicationService = Depends(get_application_service),
):
    """Get an Application by ID"""
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(
            user.role,
            org_member.role if org_member else None,
            TargetEnum.APPLICATION,
            ActionTypeEnum.READ,
        )
        return await application_service.get_application_by_underwriting_id(application_id, db)
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in get_application_by_id: {str(e)}")
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error in get_application_by_id: {str(e)}", exc_info=True
        )
        raise DatabaseException(f"Failed to retrieve application: {str(e)}")


@router.post("", response_model=CreateApplicationResponse)
async def create_application(
    org_id: UUID,
    usecase_id: UUID,
    data: str = Form(...),
    files: List[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    application_service: ApplicationService = Depends(get_application_service),
):
    """Create a new Application"""
    try:
        application_data = CreateApplicationRequest(**json.loads(data))

        # Validate file
        if not files:
            raise BadRequestException("File is required")

        # validate_file(file)

        org_member = await validate_org_member(org_id, user, db)
        authorize_user(
            user.role,
            org_member.role if org_member else None,
            TargetEnum.APPLICATION,
            ActionTypeEnum.CREATE,
        )

        config_manager = ConfigManager.get_instance()

        org = await config_manager.org_service.get_org_by_id(org_id, db)
        usecase = await config_manager.usecase_service.get_usecase_by_id(usecase_id, db)

        validate_org_usecase(org, usecase)

        return await application_service.create_application(
            org, usecase, application_data, user, db, files
        )
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in create_application: {str(e)}")
        raise e
    except FileProcessingException as e:
        logger.error(f"File processing error in create_application: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in create_application: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to create application: {str(e)}")


@router.put("/{application_id}", response_model=EmptyResponse)
async def update_application(
    org_id: UUID,
    usecase_id: UUID,
    application_id: str,
    data: UpdateApplicationRequest = Body(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    application_service: ApplicationService = Depends(get_application_service),
):
    """Update an existing Application"""
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(
            user.role,
            org_member.role if org_member else None,
            TargetEnum.APPLICATION,
            ActionTypeEnum.UPDATE,
        )

        config_manager = ConfigManager.get_instance()
        org = await config_manager.org_service.get_org_by_id(org_id, db)
        usecase = await config_manager.usecase_service.get_usecase_by_id(usecase_id, db)

        validate_org_usecase(org, usecase)

        return await application_service.update_application(
            org, usecase, application_id, data, db
        )
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in update_application: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in update_application: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to update application: {str(e)}")
