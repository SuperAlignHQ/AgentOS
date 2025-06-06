from sqlmodel import SQLModel, create_engine,Session
from app.models.models import (
    Organization, User, Workflow, Document,
    Policy, DocumentPolicyInference, Audit,
    Role, DocumentTypeMaster
)

DATABASE_URL = "postgresql://postgres:password@localhost:5432/superalign"

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_all_tables():
    SQLModel.metadata.drop_all(bind=engine)

def get_session():
    return Session(engine)