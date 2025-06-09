from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, Column
from typing import Optional, List
from uuid import UUID,uuid4
from datetime import datetime


# Organizations Table
class Organization(SQLModel, table=True):
    __tablename__ = "organizations"
    id: UUID = Field(default_factory=uuid4, primary_key=True,unique=True)
    name: str = Field(max_length=255)

    workflows: List["Workflow"] = Relationship(back_populates="organization")


#  Users Table
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    role: str = Field(max_length=20, foreign_key="roles.name")
    name: str = Field(max_length=255)
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = Field(default=None)
    updated_by: Optional[UUID] = Field(default=None)
    
    role_obj: Optional["Role"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})

    created_documents: List["Document"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "[Document.created_by]"}
    )
    updated_documents: List["Document"] = Relationship(
        back_populates="updater",
        sa_relationship_kwargs={"foreign_keys": "[Document.updated_by]"}
    )
    created_policies: List["Policy"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "[Policy.created_by]"}
     )
    updated_policies: List["Policy"] = Relationship(
        back_populates="updater",
        sa_relationship_kwargs={"foreign_keys": "[Policy.updated_by]"}
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
    org_id: UUID = Field(foreign_key="organizations.id")
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = Field(default=None,foreign_key="users.id")
    updated_by: Optional[UUID] = Field(default=None,foreign_key="users.id")

    organization: Optional["Organization"] = Relationship(back_populates="workflows")
    documents: List["Document"] = Relationship(back_populates="workflow")
    policies: List["Policy"] = Relationship(back_populates="workflow")
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
    type: str = Field(max_length=200,foreign_key="document_type_master.type")
    name: str = Field(max_length=50)
    url: str = Field(max_length=2048)
    ocr_result: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = Field(default=None,foreign_key="users.id")
    updated_by: Optional[UUID] = Field(default=None,foreign_key="users.id")
    workflow_id: UUID = Field(foreign_key="workflows.id")

    workflow: Optional["Workflow"] = Relationship(back_populates="documents")
    document_type_master:Optional["DocumentTypeMaster"]=Relationship(back_populates="documents")
    creator: Optional["User"] = Relationship(
        back_populates="created_documents",
        sa_relationship_kwargs={"foreign_keys": "[Document.created_by]"}
    )
    updater: Optional["User"] = Relationship(
        back_populates="updated_documents",
        sa_relationship_kwargs={"foreign_keys": "[Document.updated_by]"}
    )


#  Policy Table
class Policy(SQLModel, table=True):
    __tablename__ = "policies"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=200)
    result: Optional[bool] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = Field(default=None,foreign_key="users.id")
    updated_by: Optional[UUID] = Field(default=None,foreign_key="users.id")
    workflow_id: UUID = Field(foreign_key="workflows.id")

    workflow: Optional["Workflow"] = Relationship(back_populates="policies")
    creator: Optional["User"] = Relationship(
        back_populates="created_policies",
        sa_relationship_kwargs={"foreign_keys": "[Policy.created_by]"}
    )
    updater: Optional["User"] = Relationship(
        back_populates="updated_policies",
        sa_relationship_kwargs={"foreign_keys": "[Policy.updated_by]"}
    )

   

#  DocumentPolicyInference Table
class DocumentPolicyInference(SQLModel, table=True):
    __tablename__ = "document_policy_inference"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    document_type: str = Field(max_length=200,foreign_key="document_type_master.type")
    policy_name: str = Field(max_length=200)

    document_type_master:Optional["DocumentTypeMaster"]=Relationship(back_populates="document_policy_inferences")

    
    

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
    workflow_id: UUID = Field(default=None)

   

# Role Table
class Role(SQLModel, table=True):
    __tablename__ = "roles"
    name: str = Field(primary_key=True, max_length=20)
    permissions: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    user: Optional["User"] = Relationship(back_populates="role_obj")

#  DocumentTypeMaster Table
class DocumentTypeMaster(SQLModel, table=True):
    __tablename__ = "document_type_master"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    type: str = Field(max_length=200,unique=True)
    no_of_fields: int
    fields_list: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    documents:List["Document"]=Relationship(back_populates="document_type_master")
    document_policy_inferences:List["DocumentPolicyInference"]=Relationship(back_populates="document_type_master")



 