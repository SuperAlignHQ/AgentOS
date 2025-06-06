from sqlmodel import SQLModel, create_engine
from app.models.models import (
    Organization, User, Workflow, Document,
    Policy, DocumentPolicyInference, Audit,
    Role, DocumentTypeMaster
)
DATABASE_URL = "postgresql://postgres:password@localhost:5432/superalign"
engine = create_engine(DATABASE_URL, echo=True)

SQLModel.metadata.create_all(engine)
