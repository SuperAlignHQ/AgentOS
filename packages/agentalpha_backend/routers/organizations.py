from datetime import datetime
from typing import List
from uuid import UUID,uuid4
from fastapi import APIRouter, Depends, HTTPException,status
from sqlmodel import Session, select, update
from models.models import Document, Organization, Workflow
from database import get_session
from schemas.OrganizationSchema import OrganizationRead,OrganizationRequest

router=APIRouter()

#Creating a New Organization
@router.post("/",response_model=OrganizationRead,status_code=status.HTTP_201_CREATED)
def create_organization(request:OrganizationRequest,session:Session=Depends(get_session)):
    try:
        organization=Organization(
            id=uuid4(),
            name=request.name
        )
        session.add(organization)
        session.commit()
        session.refresh(organization)
        return organization
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to Create Organization: {str(e)}"
        )
    
#Listing all Organizations    
@router.get("/",response_model=List[OrganizationRead])
def get_all_organizations(session:Session=Depends(get_session)):
    return session.exec(select(Organization)).all()


#Listing a Particular Organization With its id        
@router.get("/{org_id}", response_model=OrganizationRead)
def get_organization(
    org_id: UUID,
    session: Session = Depends(get_session),
):
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return org


#Updating or Patching the Organization Field name
@router.put("/{org_id}", response_model=OrganizationRead)
def update_organization(
    org_id: UUID,
    request: OrganizationRequest,
    session: Session = Depends(get_session),
):
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    #  if current_user.role not in ["app_admin", "org_admin"] or (
    #      current_user.role != "app_admin" and current_user.org_id != org_id
    # ):
    #     raise HTTPException(status_code=403, detail="Not authorized")
    for field, value in request.dict(exclude_unset=True).items():
        setattr(org,field,value)

    session.add(org)
    session.commit()
    session.refresh(org)
    return org

@router.delete("/{org_id}")
def delete_organization(
    org_id: UUID,
    session: Session = Depends(get_session),
    # current_user: User = Depends(get_current_user),
):
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Optional RBAC check
    # if current_user.role != "app_admin":
    #     raise HTTPException(status_code=403, detail="Only App Admin can delete organizations")

    session.delete(org)
    session.commit()

    return {"detail": "Organization and all related workflows/documents hard deleted successfully"}
