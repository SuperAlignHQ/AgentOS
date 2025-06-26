from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, VARCHAR, Column, ForeignKey
from typing import Optional, List
from uuid import UUID,uuid4
from datetime import datetime
import enum
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


#App Service

class Status(str,enum.Enum):
    PENDING="Pending Approval"
    FLAGGED="Flagged"
    REJECTED="Rejected"


# Organizations Table
class Organization(SQLModel, table=True):
    __tablename__ = "organizations"
    id: UUID = Field(default_factory=uuid4, primary_key=True,unique=True)
    name: str = Field(max_length=255,unique=True)

    workflows: List["Workflow"] = Relationship(back_populates="organization",sa_relationship_kwargs={
        "cascade": "all, delete-orphan",
        "passive_deletes": True
    })


# Role Table
class Role(SQLModel, table=True):
    __tablename__ = "roles"
    name: str = Field(primary_key=True, max_length=20)
    permissions: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    users: List["User"] = Relationship(back_populates="role_obj")


class DocumentUpdaterLink(SQLModel, table=True):
    __tablename__ = "document_updater_link"

    document_id: UUID = Field(foreign_key="documents.id", primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)


#  Users Table
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    role: str = Field(max_length=20, foreign_key="roles.name")
    name: str = Field(max_length=255)
    hashedPassword:str=Field(default=None)
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = Field(default=None,foreign_key="users.id")
    updated_by: Optional[UUID] = Field(default=None,foreign_key="users.id")


     # 🔁 Self-referencing relationships
    creator: Optional["User"] = Relationship(
        back_populates="created_users",
        sa_relationship_kwargs={"foreign_keys": "[User.created_by]","remote_side": "[User.id]"}
    )
    updater: Optional["User"] = Relationship(
        back_populates="updated_users",
        sa_relationship_kwargs={"foreign_keys": "[User.updated_by]","remote_side": "[User.id]"}
    )

    created_users: List["User"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "[User.created_by]"}
    )
    updated_users: List["User"] = Relationship(
        back_populates="updater",
        sa_relationship_kwargs={"foreign_keys": "[User.updated_by]"}
    )


     #Other Table Relationships
    role_obj: Optional["Role"] = Relationship(back_populates="users")

    created_documents: List["Document"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "[Document.created_by]"}
    )
    updated_documents: List["Document"] = Relationship(
        back_populates="updaters",
        link_model=DocumentUpdaterLink
    )

    created_workflows: List["Workflow"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "[Workflow.created_by]"}
    )
    updated_workflows: List["Workflow"] = Relationship(
        back_populates="updater",
        sa_relationship_kwargs={"foreign_keys": "[Workflow.updated_by]"}
    )


   

#  Workflow Table
class Workflow(SQLModel, table=True):
    __tablename__ = "workflows"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    documents_list: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    policies_list: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    org_id: UUID = Field(sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False
        ))
    status:Status
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = Field(default=None,foreign_key="users.id")
    updated_by: Optional[UUID] = Field(default=None,foreign_key="users.id")

    organization: Optional["Organization"] = Relationship(back_populates="workflows")
    documents: List["Document"] = Relationship(back_populates="workflow",sa_relationship_kwargs={
        "passive_deletes": True
    })
    creator: Optional["User"] = Relationship(
        back_populates="created_workflows",
        sa_relationship_kwargs={"foreign_keys": "[Workflow.created_by]"}
    )
    updater: Optional["User"] = Relationship(
        back_populates="updated_workflows",
        sa_relationship_kwargs={"foreign_keys": "[Workflow.updated_by]"}
    )

#  Document Table
class Document(SQLModel, table=True):
    __tablename__ = "documents"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    format: str = Field(max_length=200)
    type: str = Field(max_length=200,sa_column=Column(
        VARCHAR(200),
        ForeignKey("document_type_master.type", ondelete="CASCADE"),
        nullable=False
    ))
    category:str=Field(max_length=200)
    name: str = Field(max_length=50)
    url: str = Field(max_length=2048)
    ocr_result: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = Field(default=None,foreign_key="users.id")
    workflow_id: UUID = Field( sa_column=Column(
          PG_UUID(as_uuid=True),
            ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False
        ))

    
    workflow: Optional["Workflow"] = Relationship(back_populates="documents")
    document_type_master:Optional["DocumentTypeMaster"]=Relationship(back_populates="documents")
    creator: Optional["User"] = Relationship(
        back_populates="created_documents",
        sa_relationship_kwargs={"foreign_keys": "[Document.created_by]"}
    )
    updaters: List["User"] = Relationship(
        back_populates="updated_documents",
        link_model=DocumentUpdaterLink
    )

   

#  Audit Table
class Audit(SQLModel, table=True):
    __tablename__ = "audits"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime
    type: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    priority: str = Field(max_length=20)
    action_needed: bool
    assigned_to: Optional[UUID] = Field(default=None)
    workflow_id: Optional[UUID] = Field(default=None,nullable=True)

   



#DocumentTypeMaster Table
class DocumentTypeMaster(SQLModel, table=True):
    __tablename__ = "document_type_master"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    type: str = Field(max_length=200,unique=True)
    no_of_fields: int
    fields_list: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    documents:List["Document"]=Relationship(back_populates="document_type_master",sa_relationship_kwargs={
        "cascade": "all, delete-orphan",
        "passive_deletes": True
    })



#PolicyService


class PolicyType(str,enum.Enum):
    GLOBAL="Global"
    ORG="Org"



class PolicyMaster(SQLModel,table=True):
    __tablename__="policy_masters"
    id: UUID =Field(default_factory=uuid4,primary_key=True)
    name: str = Field(max_length=200,unique=True)
    description:str= Field(max_length=200)
    type:PolicyType
    policy_function:str=Field(max_length=20)
    list_of_documents:Optional[list] = Field(default=None, sa_column=Column(JSON))
    variables:Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = Field(default=None)
    updated_by: Optional[UUID] = Field(default=None)

    
    policies:List["Policy"]=Relationship(back_populates="policy_master")


    

class Policy(SQLModel, table=True):
    __tablename__ = "policies"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=200,foreign_key="policy_masters.name")
    result: Optional[bool] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = Field(default=None)
    updated_by: Optional[UUID] = Field(default=None)
    workflow_id: Optional[UUID] = Field( default= None)

    
    policy_master:Optional["PolicyMaster"]=Relationship(back_populates="policies")

   

class OrganizationPolicyMap(SQLModel,table=True):
    __tablename__="org_policy_map"
    org_id:UUID =Field(primary_key=True)
    list_of_policy_master_types:List[UUID]=Field(default_factory=list,sa_column=Column(MutableList.as_mutable(JSON)))




 