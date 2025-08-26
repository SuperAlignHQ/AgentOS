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
from app.db.models import ActionTypeEnum, TargetEnum, User
from app.routes.org_router import get_org_service
from app.schemas.audit_schema import GetAuditLogsResponse
from app.schemas.util import PaginationQuery
from app.services.audit_service import AuditService
from app.services.org_service import OrgService


router = APIRouter(prefix="/org/{org_id}/audit", tags=["Audit"])


def get_audit_service():
    return ConfigManager.get_instance().audit_service


@router.get(
    "/",
    response_model=GetAuditLogsResponse,
    description="Get audit logs for an organisation",
)
async def get_audit_logs(
    org_id: UUID,
    pagination: PaginationQuery = Depends(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    org_service: OrgService = Depends(get_org_service),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Get audit logs for an organisation
    """
    try:
        org_member = await validate_org_member(org_id, user, db)
        authorize_user(
            user.role,
            org_member.role if org_member else None,
            TargetEnum.AUDIT,
            ActionTypeEnum.READ,
        )

        org = await org_service.get_org_by_id(org_id, db)
        return await audit_service.get_audit_logs(db, org, pagination)
    except (NotFoundException, ValidationException, BadRequestException) as e:
        logger.error(f"Error in get_audit_logs: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in get_audit_logs: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to retrieve audit logs: {str(e)}")
