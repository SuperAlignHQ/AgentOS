from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel

from app.db.models import Org, OrgMember
from app.schemas.user_schema import UserResponse


class CreateOrgRequest(BaseModel):
    name: str


class UpdateOrgRequest(BaseModel):
    name: str


class OrgMemberResponse(BaseModel):
    member_id: UUID
    org: Org
    user: UserResponse
    member_role: str
    created_at: datetime
    created_by: UUID

    @classmethod
    def from_member(cls, org_member: OrgMember):
        return cls(
            member_id=org_member.org_member_id,
            org=org_member.org,
            member_role=org_member.role.name,
            user=UserResponse.from_user(org_member.user),
            created_at=org_member.created_at,
            created_by=org_member.created_by,
        )


class GetOrgMembersResponse(BaseModel):
    org_members: List[OrgMemberResponse]
    total: int


class AddOrgMemberRequest(BaseModel):
    user_id: UUID
    role: str = "underwriter"  # TODO: Add role enum


class UpdateMemberRequest(BaseModel):
    role: str # TODO: Add role enum
