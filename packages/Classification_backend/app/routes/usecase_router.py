from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config_manager import ConfigManager
from app.core.logging_config import logger
from app.core.util import authorize_user, get_current_user, get_db_session, validate_org_member, validate_org_usecase
from app.db.models import ActionTypeEnum, TargetEnum, Usecase, User
from app.schemas.usecase_schema import CreateUsecaseRequest, UpdateUsecaseRequest
from app.schemas.util import EmptyResponse
from app.services.usecase_service import UsecaseService


router = APIRouter(prefix="/org/{org_id}/usecase", tags=["Usecase"])


def get_usecase_service():
    return ConfigManager.get_instance().usecase_service


@router.get("", response_model=List[Usecase])
async def get_usecases(
    org_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    usecase_service: UsecaseService = Depends(get_usecase_service),
):
    """
    Get all usecases
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(user.role, org_member.role if org_member else None, TargetEnum.USECASE, ActionTypeEnum.READ)

        # validate if user is org member or not

        config_manager = ConfigManager.get_instance()
        org = await config_manager.org_service.get_org_by_id(org_id, db)
        
        usecases = await usecase_service.get_usecases(db, user, org)
        return usecases
    except Exception as e:
        logger.error(f"Error in get_usecases: {e}")
        raise e


@router.get("/{usecase_id}", response_model=Usecase)
async def get_usecase_by_id(
    org_id: UUID,
    usecase_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    usecase_service: UsecaseService = Depends(get_usecase_service),
):
    """
    Get usecase by id
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(user.role, org_member.role if org_member else None, TargetEnum.USECASE, ActionTypeEnum.READ)

        # validate if user is org member or not

        config_manager = ConfigManager.get_instance()
        org = await config_manager.org_service.get_org_by_id(org_id, db)
        usecase = await usecase_service.get_usecase_by_id(usecase_id, db)
        validate_org_usecase(org, usecase)
        return usecase
    except Exception as e:
        logger.error(f"Error in get_usecase_by_id: {e}")
        raise e


@router.post("", response_model=Usecase)
async def create_usecase(
    org_id: UUID,
    usecase: CreateUsecaseRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    usecase_service: UsecaseService = Depends(get_usecase_service),
):
    """
    Create usecase
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(user.role, org_member.role if org_member else None, TargetEnum.USECASE, ActionTypeEnum.CREATE)

        # validate if user is org member or not

        config_manager = ConfigManager.get_instance()
        org = await config_manager.org_service.get_org_by_id(org_id, db)
        usecase = await usecase_service.create_usecase(db, user, org, usecase)
        return usecase
    except Exception as e:
        logger.error(f"Error in create_usecase: {e}")
        raise e


@router.put("/{usecase_id}", response_model=Usecase)
async def update_usecase(
    org_id: UUID,
    usecase_id: UUID,
    update_data: UpdateUsecaseRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    usecase_service: UsecaseService = Depends(get_usecase_service),
):
    """
    Update usecase
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(user.role, org_member.role if org_member else None, TargetEnum.USECASE, ActionTypeEnum.UPDATE)

        # validate if user is org member or not

        config_manager = ConfigManager.get_instance()
        org = await config_manager.org_service.get_org_by_id(org_id, db)
        usecase = await usecase_service.get_usecase_by_id(usecase_id, db)

        validate_org_usecase(org, usecase)

        usecase = await usecase_service.update_usecase(db, user, org, usecase, update_data)
        return usecase
    except Exception as e:
        logger.error(f"Error in update_usecase: {e}")
        raise e


@router.delete("/{usecase_id}", response_model=EmptyResponse)
async def delete_usecase(
    org_id: UUID,
    usecase_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    usecase_service: UsecaseService = Depends(get_usecase_service),
):
    """
    Delete usecase
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(user.role, org_member.role if org_member else None, TargetEnum.USECASE, ActionTypeEnum.DELETE)

        # validate if user is org member or not

        config_manager = ConfigManager.get_instance()
        org = await config_manager.org_service.get_org_by_id(org_id, db)
        usecase = await usecase_service.get_usecase_by_id(usecase_id, db)

        validate_org_usecase(org, usecase)

        await usecase_service.delete_usecase(db, user, org, usecase)
        return EmptyResponse(message="Usecase deleted successfully")
    except Exception as e:
        logger.error(f"Error in delete_usecase: {e}")
        raise e
