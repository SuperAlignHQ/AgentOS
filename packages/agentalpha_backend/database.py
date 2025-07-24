from sqlalchemy import text
from sqlmodel import SQLModel, create_engine,Session
from models.models import (
    Organization, User, Workflow, Document,
    Policy, Audit,
    Role, DocumentTypeMaster, PolicyMaster,OrganizationPolicyMap,DocumentUpdaterLink,
)

DATABASE_URL = "postgresql://postgres:password@localhost:5432/superalign"

engine = create_engine(DATABASE_URL,
                       pool_size=20,
                       max_overflow=30,
                        echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_all_tables():
    '''SQLModel.metadata.reflect(bind=engine)
    SQLModel.metadata.drop_all(bind=engine)'''
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    print("💣 Dropped entire schema and recreated it.")


def get_session():
    return Session(engine)