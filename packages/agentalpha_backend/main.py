from fastapi import FastAPI
from database import create_db_and_tables,drop_all_tables
from routers import auth, documentTypes, organizations,workflows,documents,org_policies,policy_applications,global_policies

app=FastAPI()


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
app.include_router(policy_applications.router, prefix="/organizations/{org_id}/workflows/{workflow_id}/policies", tags=["Policy Applications"])
app.include_router(workflows.router, prefix="/organizations/{org_id}/workflows", tags=["Workflows"])
app.include_router(documentTypes.router, prefix="/organizations/{org_id}/workflows/{workflow_id}", tags=["DocumentTypes"])
app.include_router(documents.router, prefix="/organizations/{org_id}/workflows/{workflow_id}", tags=["Documents"])
app.include_router(global_policies.router, prefix="/policies", tags=["Policies"])
app.include_router(org_policies.router,prefix="/organizations",tags=["Org Policies"])



@app.get('/create')
def home():
    create_db_and_tables()
    return {"Created Successfully"}

@app.get("/drop")
def delete_database():
    drop_all_tables()
    return{"Deleted Successfully"}
