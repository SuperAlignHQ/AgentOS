from sqlmodel import Integer, SQLModel, Field, Relationship
from sqlalchemy import (
    Column,
    Enum as SqlEnum,
    TIMESTAMP,
    String,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as SqlUUID
from typing import List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from app.core.exception_handler import ValidationException


class ApplicationStatus(str, Enum):
    APPROVED = "approved"
    DECLINED = "declined"
    REVIEW = "needs_review"


class UnderwriterStatus(str, Enum):
    APPROVED = "approved"
    DECLINED = "declined"
    SUSPEND = "suspended"
    PENDING = "pending"


class FileFormat(str, Enum):
    PDF = "pdf"

    @classmethod
    def get_file_format(cls, ext: str) -> "FileFormat":
        try:
            return cls(ext)
        except ValueError:
            raise ValidationException(f"Invalid file format: {ext}")


class ActivityStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ActionTypeEnum(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"
    ADD = "add"
    LINK = "link"


class TargetEnum(str, Enum):
    USECASE = "usecase"
    APPLICATION = "application"
    ORG = "org"
    DOCUMENT_TYPE = "document_type"
    DOCUMENT = "document"
    CONFIG = "config"
    APPLICATION_TYPE = "application_type"
    ORG_MEMBER = "org_member"
    USER = "user"
    AUDIT = "audit"


class TargetTableEnum(str, Enum):
    USER = "user"
    APPLICATION_TYPE = "application_type"
    DOCUMENT = "document"
    ORG = "org"
    APPLICATION = "application"
    DOCUMENT_TYPE = "document_type"
    USECASE = "usecase"
    CONFIG = "application_type_document_type_association"
    ORG_MEMBER = "org_member"


class RoleType(str, Enum):
    ORG = "org"
    APP = "app"


class Org(SQLModel, table=True):
    __tablename__ = "org"
    org_id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(SqlUUID(as_uuid=True), unique=True, primary_key=True),
    )
    name: str = Field(max_length=255, sa_column=Column(String(255), unique=True))
    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    created_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
        )
    )
    updated_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
        )
    )
    usecases: List["Usecase"] = Relationship(
        back_populates="org",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
            "lazy": "selectin",
        },
    )


class OrgMember(SQLModel, table=True):
    __tablename__ = "org_member"
    org_member_id: UUID = Field(
        default_factory=uuid4, sa_column=Column(SqlUUID(as_uuid=True), primary_key=True)
    )
    org_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("org.org_id"), nullable=False
        )
    )
    user_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True),
            ForeignKey("user.user_id"),
            nullable=False,
        )
    )
    role_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("role.role_id"), nullable=False
        )
    )
    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    created_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
        )
    )
    updated_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
        )
    )
    org: Org = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
        }
    )
    user: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "OrgMember.user_id == User.user_id",
            "foreign_keys": "OrgMember.user_id",
            "lazy": "joined",
        }
    )
    role: "Role" = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
        }
    )


class Usecase(SQLModel, table=True):
    __tablename__ = "usecase"
    usecase_id: UUID = Field(
        default_factory=uuid4, sa_column=Column(SqlUUID(as_uuid=True), primary_key=True)
    )
    name: str = Field(
        max_length=255, sa_column=Column(String(255), unique=True, nullable=False)
    )
    org_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("org.org_id"), nullable=False
        )
    )
    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    created_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
        )
    )
    updated_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
        )
    )
    applications: List["Application"] = Relationship(
        back_populates="usecase",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
            "lazy": "selectin",
        },
    )
    org: Org = Relationship(back_populates="usecases", sa_relationship_kwargs={"lazy": "joined"})


class Role(SQLModel, table=True):
    __tablename__ = "role"
    role_id: UUID = Field(
        default_factory=uuid4, sa_column=Column(SqlUUID(as_uuid=True), primary_key=True)
    )
    name: str = Field(max_length=20, sa_column=Column(String(20), nullable=False, unique=True))
    permissions: Dict[str, Any] = Field(default=dict(), sa_column=Column(JSONB))
    type: RoleType = Field(sa_column=Column(SqlEnum(RoleType)))

    users: List["User"] = Relationship(back_populates="role", sa_relationship_kwargs={"lazy": "selectin"})


class User(SQLModel, table=True):
    __tablename__ = "user"
    user_id: UUID = Field(
        default_factory=uuid4, sa_column=Column(SqlUUID(as_uuid=True), primary_key=True)
    )
    name: str = Field(max_length=255, sa_column=Column(String(255)))
    role_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("role.role_id"), nullable=False
        )
    )
    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )

    role: Role = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
        }
    )


class Application(SQLModel, table=True):
    __tablename__ = "application"
    application_id: UUID = Field(
        default_factory=uuid4, sa_column=Column(SqlUUID(as_uuid=True), primary_key=True)
    )
    # name: str = Field(max_length=255, sa_column=Column(String(255)))
    # org_id: UUID = Field(foreign_key="org.id", sa_column=Column(SqlUUID(as_uuid=True)), nullable=False)
    status: ApplicationStatus = Field(
        default=ApplicationStatus.REVIEW, sa_column=SqlEnum(ApplicationStatus)
    )
    underwriting_application_id: str = Field(
        max_length=10, sa_column=Column(String(10), unique=True)
    )
    application_type_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True),
            ForeignKey("application_type.application_type_id"),
            nullable=False,
        )
    )
    usecase_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("usecase.usecase_id"), nullable=False
        )
    )
    underwriter_status: UnderwriterStatus = Field(
        default=UnderwriterStatus.PENDING, sa_column=SqlEnum(UnderwriterStatus)
    )
    underwriter_review: str = Field(max_length=2048, sa_column=Column(String(2048)))
    document_result: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    created_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
        )
    )
    updated_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
        )
    )

    usecase: Usecase = Relationship(back_populates="applications", sa_relationship_kwargs={"lazy": "joined"})
    application_type: "ApplicationType" = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    creator: "User" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Application.created_by == User.user_id", "lazy": "joined"}
    )
    updator: "User" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Application.updated_by == User.user_id", "lazy": "joined"}
    )


class ApplicationType(SQLModel, table=True):
    __tablename__ = "application_type"
    application_type_id: UUID = Field(
        default_factory=uuid4, sa_column=Column(SqlUUID(as_uuid=True), primary_key=True)
    )
    application_type_code: str = Field(
        max_length=50, sa_column=Column(String(50), nullable=False)
    )
    org_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("org.org_id"), nullable=False
        )
    )
    # name: str = Field(max_length=255, sa_column=Column(String(255)), nullable=False, unique=True)
    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    created_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
        )
    )
    updated_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
        )
    )

    document_type_associations: List["ApplicationTypeDocumentTypeAssociation"] = (
        Relationship(
            back_populates="application_type",
            sa_relationship_kwargs={"cascade": "all ,delete-orphan", "lazy": "selectin"},
        )
    )


class Document(SQLModel, table=True):
    __tablename__ = "document"
    document_id: UUID = Field(
        default_factory=uuid4, sa_column=Column(SqlUUID(as_uuid=True), primary_key=True)
    )
    document_type_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True),
            ForeignKey("document_type.document_type_id"),
            nullable=False,
        )
    )
    application_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True),
            ForeignKey("application.application_id"),
            nullable=False,
        )
    )
    format: FileFormat = Field(sa_column=SqlEnum(FileFormat))
    original_file_name: str = Field(
        max_length=50, sa_column=Column(String(50), nullable=False)
    )
    url: str = Field(sa_column=Column(String()))
    size: int = Field(sa_column=Column(Integer, nullable=False))
    # name: str = Field(max_length=255, sa_column=Column(String(255)))
    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    created_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
        )
    )
    updated_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
        )
    )


class DocumentType(SQLModel, table=True):
    __tablename__ = "document_type"
    document_type_id: UUID = Field(
        default_factory=uuid4, sa_column=Column(SqlUUID(as_uuid=True), primary_key=True)
    )
    name: str = Field(max_length=255, sa_column=Column(String(255), nullable=False))
    category: str = Field(max_length=200, sa_column=Column(String(200), nullable=False))

    application_associations: List["ApplicationTypeDocumentTypeAssociation"] = (
        Relationship(sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"})
    )


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"
    audit_log_id: UUID = Field(
        default_factory=uuid4, sa_column=Column(SqlUUID(as_uuid=True), primary_key=True)
    )
    change_type: ActionTypeEnum = Field(sa_column=SqlEnum(ActionTypeEnum))
    title: str = Field(sa_column=Column(String(1000)), max_length=1000)
    target_name: TargetEnum = Field(sa_column=SqlEnum(TargetEnum))
    org_id: UUID = Field(sa_column=Column(SqlUUID(as_uuid=True)))
    actor_id: UUID = Field(sa_column=Column(SqlUUID(as_uuid=True), nullable=False))
    target_id: UUID = Field(sa_column=Column(SqlUUID(as_uuid=True)))
    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )


class ApplicationTypeDocumentTypeAssociation(SQLModel, table=True):
    __tablename__ = "application_type_document_type_association"
    application_type_document_type_association_id: UUID = Field(
        default_factory=uuid4, sa_column=Column(SqlUUID(as_uuid=True), primary_key=True)
    )
    application_type_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True),
            ForeignKey("application_type.application_type_id"),
            nullable=False,
        )
    )
    document_type_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True),
            ForeignKey("document_type.document_type_id"),
            nullable=False,
        )
    )
    usecase_id: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True), ForeignKey("usecase.usecase_id"), nullable=False
        )
    )
    is_optional: bool = Field(default=False, nullable=False)
    # status: ActivityStatus = Field(nullable=False, default=ActivityStatus.ACTIVE, sa_column=SqlEnum(ActivityStatus))
    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(TIMESTAMP(timezone=True))
    )
    created_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True),
            ForeignKey("user.user_id"),
            nullable=False,
        )
    )
    updated_by: UUID = Field(
        sa_column=Column(
            SqlUUID(as_uuid=True),
            ForeignKey("user.user_id"),
            nullable=False,
        )
    )

    application_type: ApplicationType = Relationship(
        back_populates="document_type_associations",
        sa_relationship_kwargs={
            "lazy": "joined"
        }
    )
    document_type: DocumentType = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined"
        }
    )

    def to_dict(self) -> dict:
        """
        Convert the association to a dictionary.

        Returns:
            dict: A dictionary representation of the association.
        """
        return {
            "id": self.application_type_document_type_association_id,
            "document_type": self.document_type.name,
            "document_category": self.document_type.category,
            "is_optional": self.is_optional,
        }
