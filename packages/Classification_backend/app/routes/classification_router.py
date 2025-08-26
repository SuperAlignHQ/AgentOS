from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config_manager import ConfigManager
from app.core.util import (
    authorize_user,
    get_current_user,
    get_db_session,
    validate_org_member,
    validate_org_usecase,
)
from app.db.models import ActionTypeEnum, TargetEnum, User
from app.schemas.application_schema import CreateApplicationRequest, CreateApplicationResponse, GetApplicationsResponse
from app.schemas.util import PaginationQuery
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
    org_member = await validate_org_member(org_id, user, db)
    authorize_user(user.role, org_member.role if org_member else None, TargetEnum.APPLICATION, ActionTypeEnum.READ)

    config_manager = ConfigManager.get_instance()
    org = await config_manager.org_service.get_org_by_id(org_id, db)
    usecase = await config_manager.usecase_service.get_usecase_by_id(
        usecase_id, db
    )

    validate_org_usecase(org, usecase)

    return await application_service.get_all_applications(
        org,
        usecase,
        pagination,
        db
    )


@router.post("", response_model=CreateApplicationResponse)
async def create_application(
    org_id: UUID,
    usecase_id: UUID,
    application_data: CreateApplicationRequest,
    files: List[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    application_service: ApplicationService = Depends(get_application_service),
):
    """Create a new Application"""
    org_member = await validate_org_member(org_id, user, db)
    authorize_user(user.role, org_member.role if org_member else None, TargetEnum.APPLICATION, ActionTypeEnum.CREATE)

    config_manager = ConfigManager.get_instance()

    org = await config_manager.org_service.get_org_by_id(org_id, db)
    usecase = await config_manager.usecase_service.get_usecase_by_id(
        usecase_id, db
    )

    validate_org_usecase(org, usecase)

    return await application_service.create_application(
        org,
        usecase,
        application_data,
        files,
        db
    )
