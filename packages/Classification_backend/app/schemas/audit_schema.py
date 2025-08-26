from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from app.db.models import AuditLog


class AuditLogResponse(BaseModel):
    audit_id: UUID
    title: str
    org_id: Optional[UUID] = None
    actor: UUID
    action: str
    resource: str
    resource_id: Optional[UUID] = None
    created_at: datetime

    @classmethod
    def from_audit_log(cls, audit_log: AuditLog):
        return cls(
            audit_id=audit_log.audit_log_id,
            title=audit_log.title,
            org_id=audit_log.org_id,
            actor=audit_log.actor_id,
            action=audit_log.change_type,
            resource=audit_log.target_name,
            resource_id=audit_log.target_id,
            created_at=audit_log.created_at,
        )


class GetAuditLogsResponse(BaseModel):
    audit_logs: List[AuditLogResponse]
    total: int