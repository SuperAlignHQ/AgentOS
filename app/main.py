from fastapi import FastAPI
from app.database import create_db_and_tables,drop_all_tables
from app.routers import auth, documentTypes, organizations,workflows,policies,users,documents

app=FastAPI()


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
app.include_router(workflows.router, prefix="/organizations/{org_id}/workflows", tags=["Workflows"])
app.include_router(documentTypes.router, prefix="/organizations/{org_id}/workflows/{workflow_id}", tags=["DocumentTypes"])
app.include_router(documents.router, prefix="/organizations/{org_id}/workflows/{workflow_id}", tags=["Documents"])
app.include_router(policies.router, prefix="/policies", tags=["Policies"])
app.include_router(users.router, prefix="/organizations/{org_id}/users", tags=["Users"])


@app.get('/create')
def home():
    create_db_and_tables()
    return {"Created Successfully"}

@app.get("/drop")
def delete_database():
    drop_all_tables()
    return{"Deleted Successfully"}
