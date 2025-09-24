from sqlmodel import col, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exception_handler import DatabaseException
from app.core.logging_config import logger
from app.db.models import AuditLog, Org
from app.schemas.audit_schema import AuditLogResponse, GetAuditLogsResponse
from app.schemas.util import PaginationQuery


class AuditService:
    _instance = None
    # audit_repo: AuditRepo

    def __init__(self) -> None:
        if AuditService._instance is not None:
            raise RuntimeError("Use get_instance to get an instance of AuditService")

        # self.audit_repo = AuditRepo.get_instance()

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()

        return cls._instance

    async def get_audit_logs(
        self,
        db: AsyncSession,
        org: Org,
        pagination: PaginationQuery,
    ) -> GetAuditLogsResponse:
        """
        Get audit logs for an organisation
        """
        try:
            query = select(AuditLog).where(
                or_(
                    AuditLog.org_id == org.org_id,
                    col(AuditLog.org_id).is_(None)
                )
            )
            query = query.offset((pagination.page - 1) * pagination.page_size)
            query = query.limit(pagination.page_size)
            result = await db.exec(query)
            audit_logs = result.all()

            total = await db.exec(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.org_id == org.org_id or AuditLog.org_id is None)
            )
            return GetAuditLogsResponse(
                audit_logs=[
                    AuditLogResponse.from_audit_log(audit_log)
                    for audit_log in audit_logs
                ],
                total=total.first(),
            )
        except Exception as e:
            logger.error(f"Error in get_audit_logs: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")

    async def create_audit_log(
        self,
        db: AsyncSession,
        audit_log: AuditLog,
    ) -> None:
        """
        Create audit log
        """
        try:
            db.add(audit_log)
            await db.commit()
            await db.refresh(audit_log)
        except Exception as e:
            logger.error(f"Error in create_audit_log: {str(e)}", exc_info=True)
            await db.rollback()
            raise DatabaseException(f"{str(e)}")
