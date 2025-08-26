from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

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
        
        query = select(AuditLog).where(AuditLog.org_id == org.org_id or AuditLog.org_id == None)
        query = query.offset((pagination.page - 1) * pagination.page_size)
        query = query.limit(pagination.page_size)
        result = await db.exec(query)
        audit_logs = result.all()

        total = await db.exec(select(func.count()).select_from(AuditLog).where(AuditLog.org_id == org.org_id or AuditLog.org_id == None))
        return GetAuditLogsResponse(
            audit_logs=[AuditLogResponse.from_audit_log(audit_log) for audit_log in audit_logs],
            total=total.first(),
        )

    async def create_audit_log(
        self,
        db: AsyncSession,
        audit_log: AuditLog,
    ) -> None:
        """
        Create audit log
        """
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
