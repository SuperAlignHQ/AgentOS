from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config_manager import ConfigManager
from app.core.exception_handler import (
    BadRequestException,
    DatabaseException,
    NotFoundException,
    ValidationException,
)
from app.core.logging_config import logger
from app.core.util import (
    authorize_user,
    get_current_user,
    get_db_session,
    validate_org_member,
)
from app.db.models import ActionTypeEnum, Org, TargetEnum, User
from app.schemas.org_schema import (
    AddOrgMemberRequest,
    CreateOrgRequest,
    GetOrgMembersResponse,
    OrgMemberResponse,
    UpdateMemberRequest,
    UpdateOrgRequest,
)
from app.schemas.util import EmptyResponse, PaginationQuery
from app.services.org_service import OrgService


router = APIRouter(prefix="/org", tags=["Organisation"])


def get_org_service() -> OrgService:
    return ConfigManager.get_instance().org_service


@router.get("", response_model=List[Org])
async def get_orgs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    org_service: OrgService = Depends(get_org_service),
):
    """
    Get all organisations
    """
    try:
        authorize_user(user.role, None, TargetEnum.ORG, ActionTypeEnum.READ)

        return await org_service.get_all_orgs(db)
    except (ValidationException, BadRequestException) as e:
        logger.error(f"Error in get_orgs: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in get_orgs: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to retrieve organizations: {str(e)}")


@router.get("/{org_id}", response_model=Org)
async def get_org(
    org_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    org_service: OrgService = Depends(get_org_service),
):
    """
    Get an organisation by id
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(
            user.role,
            org_member.role if org_member else None,
            TargetEnum.ORG,
            ActionTypeEnum.READ,
        )

        return await org_service.get_org_by_id(org_id, db)
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in get_org: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in get_org: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to retrieve organization: {str(e)}")


@router.post("", response_model=Org)
async def create_org(
    request_data: CreateOrgRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    org_service: OrgService = Depends(get_org_service),
):
    """
    Create an organisation
    """
    try:
        # Validate input data
        if not request_data.name:
            raise BadRequestException("Organization name is required")

        authorize_user(user.role, None, TargetEnum.ORG, ActionTypeEnum.CREATE)

        return await org_service.create_org(db, request_data, user)
    except (ValidationException, BadRequestException) as e:
        logger.error(f"Error in create_org: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in create_org: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to create organization: {str(e)}")


@router.put("/{org_id}", response_model=Org)
async def update_org(
    org_id: UUID,
    request_data: UpdateOrgRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    org_service: OrgService = Depends(get_org_service),
):
    """
    Update an organisation
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(
            user.role,
            org_member.role if org_member else None,
            TargetEnum.ORG,
            ActionTypeEnum.UPDATE,
        )

        return await org_service.update_org(db, org_id, request_data, user)
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in update_org: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in update_org: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to update organization: {str(e)}")


@router.delete("/{org_id}", response_model=EmptyResponse)
async def delete_org(
    org_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    org_service: OrgService = Depends(get_org_service),
):
    """
    Delete an organisation
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(
            user.role,
            org_member.role if org_member else None,
            TargetEnum.ORG,
            ActionTypeEnum.DELETE,
        )

        return await org_service.delete_org(db, org_id, user)
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in delete_org: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in delete_org: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to delete organization: {str(e)}")


@router.get(
    "/{org_id}/members",
    response_model=GetOrgMembersResponse,
    description="Get all members of an organisation",
)
async def get_org_members(
    org_id: UUID,
    pagination: PaginationQuery = Depends(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    org_service: OrgService = Depends(get_org_service),
):
    """
    Get all members of an organisation
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(
            user.role,
            org_member.role if org_member else None,
            TargetEnum.ORG,
            ActionTypeEnum.READ,
        )

        org = await org_service.get_org_by_id(org_id, db)

        return await org_service.get_org_members(db, org, pagination)
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in get_org_members: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in get_org_members: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to retrieve organization members: {str(e)}")


@router.post(
    "/{org_id}/members",
    response_model=EmptyResponse,
    description="Add a member to an organisation",
)
async def add_org_member(
    org_id: UUID,
    request_data: AddOrgMemberRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    org_service: OrgService = Depends(get_org_service),
):
    """
    Add a member to an organisation
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(
            user.role,
            org_member.role if org_member else None,
            TargetEnum.ORG,
            ActionTypeEnum.UPDATE,
        )

        org = await org_service.get_org_by_id(org_id, db)

        return await org_service.add_org_member(db, org, request_data, user)
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in add_org_member: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in add_org_member: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to add organization member: {str(e)}")


# TODO: Add update org member (basically role of org member)
# in this if the role to be updated is not of org type then return error
@router.put("/{org_id}/members/{user_id}", response_model=EmptyResponse)
async def update_org_member(
    org_id: UUID,
    user_id: UUID,
    request_data: UpdateMemberRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    org_service: OrgService = Depends(get_org_service),
) -> EmptyResponse:
    """
    Update an org member
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(
            user.role,
            org_member.role if org_member else None,
            TargetEnum.ORG,
            ActionTypeEnum.UPDATE,
        )

        org = await org_service.get_org_by_id(org_id, db)
        return await org_service.update_org_member(db, org, user_id, request_data, user)
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in update_org_member: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in update_org_member: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to update organization member: {str(e)}")


@router.delete(
    "/{org_id}/members/{user_id}",
    response_model=EmptyResponse,
    description="Remove a member from an organisation",
)
async def remove_org_member(
    org_id: UUID,
    user_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    org_service: OrgService = Depends(get_org_service),
):
    """
    Remove a member from an organisation
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(
            user.role,
            org_member.role if org_member else None,
            TargetEnum.ORG,
            ActionTypeEnum.UPDATE,
        )

        org = await org_service.get_org_by_id(org_id, db)
        return await org_service.remove_org_member(db, org, user_id, user)
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in remove_org_member: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in remove_org_member: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to remove organization member: {str(e)}")
