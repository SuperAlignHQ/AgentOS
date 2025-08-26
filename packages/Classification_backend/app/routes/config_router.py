from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config_manager import ConfigManager
from app.core.util import authorize_user, get_current_user, get_db_session, validate_org_member, validate_org_usecase
from app.db.models import ActionTypeEnum, TargetEnum, User
from app.schemas.config_schema import CreateConfigurationRequest, DeleteConfigRequest, GetConfigResponse
from app.schemas.util import EmptyResponse
from app.services.config_service import ConfigService

router = APIRouter(prefix="/org/{org_id}/usecase/{usecase_id}/config", tags=["Configuration"])


def get_config_service() -> ConfigService:
    """
    Get instance of ConfigService
    """
    return ConfigManager.get_instance().config_service


@router.post("", response_model=EmptyResponse)
async def create_configuration(
    org_id: UUID,
    usecase_id: UUID,
    config_data: List[CreateConfigurationRequest],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    config_service: ConfigService = Depends(get_config_service),
):
    """Create a new configuration"""
    org_member = await validate_org_member(org_id, user, db)
    authorize_user(user.role, org_member.role if org_member else None, TargetEnum.CONFIG, ActionTypeEnum.CREATE)

    config_manager = ConfigManager.get_instance()
    org = await config_manager.org_service.get_org_by_id(org_id, db)
    usecase = await config_manager.usecase_service.get_usecase_by_id(
        usecase_id, db
    )

    validate_org_usecase(org, usecase)

    return await config_service.create_configuration(
        user,
        org,
        usecase,
        config_data,
        db
    )


@router.delete("", response_model=EmptyResponse)
async def delete_configuration(
    org_id: UUID,
    usecase_id: UUID,
    config_data: List[DeleteConfigRequest],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    config_service: ConfigService = Depends(get_config_service),
):
    """Delete a configuration"""
    org_member = await validate_org_member(org_id, user, db)
    authorize_user(user.role, org_member.role if org_member else None, TargetEnum.CONFIG, ActionTypeEnum.DELETE)

    config_manager = ConfigManager.get_instance()
    org = await config_manager.org_service.get_org_by_id(org_id, db)
    usecase = await config_manager.usecase_service.get_usecase_by_id(
        usecase_id, db
    )

    validate_org_usecase(org, usecase)

    return await config_service.delete_configuration(
        user,
        org,
        usecase,
        config_data,
        db
    )


@router.get("", response_model=List[GetConfigResponse])
async def get_configuration(
    org_id: UUID,
    usecase_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    config_service: ConfigService = Depends(get_config_service),
):
    """Get a configuration"""
    org_member = await validate_org_member(org_id, user, db)
    authorize_user(user.role, org_member.role if org_member else None, TargetEnum.CONFIG, ActionTypeEnum.READ)

    config_manager = ConfigManager.get_instance()
    org = await config_manager.org_service.get_org_by_id(org_id, db)
    usecase = await config_manager.usecase_service.get_usecase_by_id(
        usecase_id, db
    )

    validate_org_usecase(org, usecase)

    return await config_service.get_configuration(
        org,
        usecase,
        db
    )
