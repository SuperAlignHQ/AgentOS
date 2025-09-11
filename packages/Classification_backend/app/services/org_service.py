from datetime import datetime, timezone
from typing import List
from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.exception_handler import BadRequestException, NotFoundException
from app.core.logging_config import logger
from app.db.models import ActionTypeEnum, AuditLog, Org, OrgMember, Role, RoleType, TargetEnum, User
from app.schemas.org_schema import AddOrgMemberRequest, CreateOrgRequest, GetOrgMembersResponse, OrgMemberResponse, UpdateMemberRequest, UpdateOrgRequest
from app.schemas.util import EmptyResponse, PaginationQuery
from app.services.user_service import APP_ADMIN, ORG_ADMIN


class OrgService:
    """
    Org service class
    """

    _instance = None
    # org_repo: OrgRepo

    def __init__(self) -> None:
        if OrgService._instance is not None:
            raise RuntimeError("Use get_instance to get an instance of Org Service")

        # self.org_repo = OrgRepo.get_instance()

    @classmethod
    def get_instance(cls):
        """
        Get instance of OrgService
        """
        if not cls._instance:
            cls._instance = cls()

        return cls._instance

    async def get_org_by_id(self, org_id: UUID, db: AsyncSession) -> Org:
        """
        Get org by id
        """
        try:
            org = await db.get(Org, org_id)
            if not org:
                raise NotFoundException(f"Org with id {org_id} not found")
            return org
        except Exception as e:
            logger.error(f"Error in get_org_by_id: {e}")
            raise e

    async def get_all_orgs(self, db: AsyncSession) -> List[Org]:
        """
        Get all orgs
        """
        try:
            orgs = await db.exec(select(Org))
            return orgs.all()
        except Exception as e:
            logger.error(f"Error in get_all_orgs: {e}")
            raise e

    async def create_org(self, db: AsyncSession, org: CreateOrgRequest, user: User) -> Org:
        """
        Create an org
        """
        try:
            org_model = Org(
                name=org.name,
                created_by=user.user_id,
                updated_by=user.user_id
            )
            db.add(org_model)
            await db.commit()
            await db.refresh(org_model)

            role = await db.exec(select(Role).where(Role.name == ORG_ADMIN))
            # add current user as org admin
            org_member = OrgMember(
                org_id=org_model.org_id,
                user_id=user.user_id,
                role_id=role.first().role_id,
                created_by=user.user_id,
                updated_by=user.user_id
            )
            db.add(org_member)
            await db.commit()
            await db.refresh(org_member)

            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.CREATE,
                    title=f"Organisation '{org_model.name}' created",
                    target_name=TargetEnum.ORG,
                    org_id=None,
                    actor_id=user.user_id,
                    target_id=org_model.org_id,
                )
            )
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.CREATE,
                    title=f"User '{user.user_id}' added as admin to organisation '{org_model.name}'",
                    target_name=TargetEnum.ORG_MEMBER,
                    org_id=org_model.org_id,
                    actor_id=user.user_id,
                    target_id=org_member.org_member_id,
                )
            )
            return org_model
        except Exception as e:
            logger.error(f"Error in create_org: {e}")
            raise e

    async def update_org(self, db: AsyncSession, org_id: UUID, org: UpdateOrgRequest, user: User) -> Org:
        """
        Update an org
        """
        try:
            org_db = await self.get_org_by_id(org_id, db)
            old_name = org_db.name
            org_db.name = org.name
            org_db.updated_by = user.user_id
            org_db.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(org_db)

            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.UPDATE,
                    title=f"Organisation name updated from '{old_name}' to '{org_db.name}'",
                    target_name=TargetEnum.ORG,
                    org_id=org_db.org_id,
                    actor_id=user.user_id,
                    target_id=org_db.org_id,
                )
            )

            return org_db
        except Exception as e:
            logger.error(f"Error in update_org: {e}")
            raise e

    async def delete_org(self, db: AsyncSession, org_id: UUID, user: User) -> EmptyResponse:
        """
        Delete an org
        """
        try:
            org_db = await self.get_org_by_id(org_id, db)

            #remove all org_members
            await db.exec(delete(OrgMember).where(OrgMember.org_id == org_db.org_id))
            # await db.commit()
            await db.delete(org_db)
            await db.commit()

            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.DELETE,
                    title=f"Organisation member removed and organisation '{org_db.name}' deleted",
                    target_name=TargetEnum.ORG,
                    org_id=org_db.org_id,
                    actor_id=user.user_id,
                    target_id=org_db.org_id,
                )
            )
            return EmptyResponse(message="Organisation deleted successfully")
        except Exception as e:
            logger.error(f"Error in delete_org: {e}")
            raise e

    
    async def get_org_members(self, db: AsyncSession, org: Org, pagination: PaginationQuery) -> GetOrgMembersResponse:
        """
        Get all members of an organisation
        """
        try:
            query = select(OrgMember).where(OrgMember.org_id == org.org_id)
            query = query.options(
                joinedload(OrgMember.user),
                joinedload(OrgMember.role),
                joinedload(OrgMember.org),
            )
            query = query.offset((pagination.page - 1) * pagination.page_size)
            query = query.limit(pagination.page_size)

            result = await db.exec(query)
            org_members = result.all()

            total = await db.exec(select(func.count()).select_from(OrgMember).where(OrgMember.org_id == org.org_id))
            total = total.first()

            org_member_responses = [OrgMemberResponse.from_member(org_member) for org_member in org_members]
            return GetOrgMembersResponse(
                org_members=org_member_responses,
                total=total
            )

        except Exception as e:
            logger.error(f"Error in get_org_members: {e}")


    async def add_org_member(self, db: AsyncSession, org: Org, request_data: AddOrgMemberRequest, user: User) -> EmptyResponse:
        """
        Add a member to an organisation
        """
        try:
            user_db = await db.get(User, request_data.user_id)
            if not user_db:
                raise NotFoundException(f"User with id {request_data.user_id} not found")

            org_member_db = await db.exec(select(OrgMember).where(OrgMember.org_id == org.org_id, OrgMember.user_id == request_data.user_id))
            if org_member_db.first():
                raise NotFoundException(f"User with id {request_data.user_id} is already a member of the organisation")

            role = await db.exec(select(Role).where(Role.name == request_data.role))
            role = role.first()
            if not role:
                raise NotFoundException(f"Role {request_data.role} not found")

            org_member = OrgMember(
                org_id=org.org_id,
                user_id=request_data.user_id,
                role_id=role.role_id,
                created_by=user.user_id,
                updated_by=user.user_id
            )
            db.add(org_member)
            await db.commit()
            await db.refresh(org_member)

            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.CREATE,
                    title=f"User '{user_db.user_id}' added as '{role.name}' to organisation '{org.name}'",
                    target_name=TargetEnum.ORG_MEMBER,
                    org_id=org.org_id,
                    actor_id=user.user_id,
                    target_id=org_member.org_member_id,
                )
            )

            return EmptyResponse(message="User added to organisation successfully")
        except Exception as e:
            logger.error(f"Error in add_org_member: {e}")
            raise e

    async def remove_org_member(self, db: AsyncSession, org: Org, user_id: UUID, user: User) -> EmptyResponse:
        """
        Remove a member from an organisation
        """
        try:
            # TODO : need to check if user is trying to delete itself and we know only org admin can delete org member (and app admin also) then he should not be the only org admin

            delete_user = await db.get(User, user_id)
            if not delete_user:
                raise NotFoundException(f"User with id {user_id} not found")

            org_member_db = await db.exec(select(OrgMember).where(OrgMember.org_id == org.org_id, OrgMember.user_id == user_id))
            if not org_member_db.first():
                raise NotFoundException(f"User with id {user_id} is not a member of the organisation")
            
            await db.delete(org_member_db.first())
            await db.commit()

            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.DELETE,
                    title=f"User '{delete_user.user_id}' removed from organisation '{org.name}'",
                    target_name=TargetEnum.ORG_MEMBER,
                    org_id=org.org_id,
                    actor_id=user.user_id,
                    target_id=org_member_db.first().org_member_id,
                )
            )
            
            return EmptyResponse(message="User removed from organisation successfully")
        except Exception as e:
            logger.error(f"Error in remove_org_member: {e}")
            raise e


    async def update_org_member(self, db: AsyncSession, org: Org, user_id: UUID, request_data: UpdateMemberRequest, user: User) -> EmptyResponse:
        """
        Update an org member
        """
        try:
            #check if user to be updated is member of organisation or not
            org_member_db = await db.exec(select(OrgMember).where(OrgMember.org_id == org.org_id, OrgMember.user_id == user_id))
            org_member_db = org_member_db.first()
            if not org_member_db:
                raise NotFoundException(f"User with id {user_id} is not a member of the organisation")

            # check if user is updating self except app admin, app admin can update self
            if user.role.name != APP_ADMIN and user.user_id == user_id:
                raise BadRequestException("User cannot update self")
            
            if request_data.role:
                role = await db.exec(select(Role).where(Role.name == request_data.role))
                role = role.first()
                if not role:
                    raise NotFoundException(f"Role {request_data.role} not found")

                if role.type != RoleType.ORG:
                    raise BadRequestException(f"Role {request_data.role} is not an org role")

                if org_member_db.role.role_id == role.role_id:
                    raise BadRequestException(f"Member is already assigned to role '{role.name}'")

                # check if member is org_admin and role is changed then atleast one other org_admin should exist
                if org_member_db.role.name == ORG_ADMIN:
                    subq = (select(Role.role_id).where(Role.name == ORG_ADMIN).scalar_subquery())

                    member = await db.exec(select(OrgMember).where(OrgMember.org_id == org.org_id, OrgMember.org_member_id != org_member_db.org_member_id, OrgMember.role_id == subq))
                    member = member.first()

                    if not member:
                        raise BadRequestException("Atleast one org admin should exist")

                org_member_db.role_id = role.role_id
                org_member_db.updated_by = user.user_id
                org_member_db.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(org_member_db)

            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.UPDATE,
                    title=f"User '{user.user_id}' updated role to '{request_data.role}' for user '{user_id}' in organisation '{org.name}'",
                    target_name=TargetEnum.ORG_MEMBER,
                    org_id=org.org_id,
                    actor_id=user.user_id,
                    target_id=org_member_db.org_member_id,
                )
            )
            
            return EmptyResponse(message="User updated successfully")
        except Exception as e:
            logger.error(f"Error in update_org_member: {e}")
            raise e