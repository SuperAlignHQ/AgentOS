from typing import List
from uuid import UUID,uuid4
from fastapi import APIRouter, Depends, HTTPException,status
from sqlmodel import Session, select
from models.models import Organization
from database import get_session

router=APIRouter()

#Creating a New Organization
@router.post("/",response_model=Organization,status_code=status.HTTP_201_CREATED)
def create_organization(request:Organization):
    try:
        with get_session() as session:
            session.add(request)
            session.commit()
            session.refresh(request)
            return request
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to Create Organization: {str(e)}"
        )
    
#Listing all Organizations    
@router.get("/",response_model=List[Organization])
def get_all_organizations(session:Session=Depends(get_session)):
    return session.exec(select(Organization)).all()


#Listing a Particular Organization With its id        
@router.get("/{org_id}", response_model=Organization)
def get_organization(
    org_id: UUID,
    session: Session = Depends(get_session),
):
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return org


#Updating or Patching the Organization Field name
@router.put("/{org_id}", response_model=Organization)
def update_organization(
    org_id: UUID,
    request: Organization,
    session: Session = Depends(get_session),
    #current_user: User = Depends(get_current_user),
):
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    #  if current_user.role not in ["app_admin", "org_admin"] or (
    #      current_user.role != "app_admin" and current_user.org_id != org_id
    # ):
    #     raise HTTPException(status_code=403, detail="Not authorized")

    org.name = request.name
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


#Deleting a particular Organization
@router.delete("/{org_id}")
def delete_organization(
    org_id: UUID,
    session: Session = Depends(get_session),
    #current_user: User = Depends(get_current_user),
):
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # if current_user.role != "app_admin":
    #     raise HTTPException(status_code=403, detail="Only App Admin can delete organizations")

    session.delete(org)
    session.commit()
    return {"detail": "Organization deleted successfully"}
