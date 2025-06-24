from datetime import datetime
from typing import List
from fastapi import APIRouter, Body,status,Depends,HTTPException
from models.models import PolicyMaster,User,Audit,PolicyType
from schemas.PolicyMasterSchema import PolicyMasterInput,PolicyMasterRead,PolicyMasterUpdateInput

from sqlmodel import Session, select
from database import get_session
from utils.auth_utils import get_current_user,is_authorised,get_current_user_by_id
from uuid import UUID,uuid4
router=APIRouter()

@router.post("/",response_model=PolicyMasterRead,status_code=status.HTTP_201_CREATED)
def create_global_policy(request:PolicyMasterInput, token:str,session:Session= Depends(get_session)):
    try:
        
        current_user_id=get_current_user(token)

        current_user=get_current_user_by_id(session,current_user_id)


        if is_authorised(current_user,["App Admin"]):
            pass

        
        # Set required metadata fields
        new_policy = PolicyMaster(
                   id=uuid4(),
                   name=request.name,
                   description=request.description,
                   type=PolicyType.GLOBAL,  # Enforced internally
                   policy_function=request.policy_function,
                   list_of_documents=request.list_of_documents,
                   variables=request.variables,
                   created_at=datetime.utcnow(),
                   updated_at=datetime.utcnow(),
                   created_by=current_user.id,
                            )
        session.add(new_policy)
        session.commit()
        session.refresh(new_policy)

        # Record to Audit Table
        audit = Audit(
            id=uuid4(),
            created_at=datetime.utcnow(),
            type="POLICY_MASTER_CREATION",
            message=f"Global policy master '{request.name}' created by '{current_user.name}'",
            priority="HIGH",               # Use "LOW", "MEDIUM", "HIGH" as needed
            action_needed=False,
            assigned_to=current_user.id,             # Can set to current_user.id or approver id if needed
            workflow_id=None 
        )
        session.add(audit)
        session.commit()
        session.refresh(audit)

        return new_policy
    

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create global policy master: {str(e)}"
        )
   



@router.get("/global", response_model=List[PolicyMaster])
def list_global_policies(token: str, session: Session = Depends(get_session)):
    try:
        # Step 1: Authenticate and get current user
        current_user_id = get_current_user(token)
        current_user = get_current_user_by_id(session, current_user_id)

        # Step 2: Authorize user (App Admin or Org Admin)
        if not is_authorised(current_user, ["App Admin", "Org Admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view global policies."
            )

        # Step 3: Fetch and return global policies
        global_policies = session.exec(
            select(PolicyMaster).where(PolicyMaster.type == "Global")
        ).all()

        return global_policies

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch global policies: {str(e)}"
        )

    

# GET a specific global policy
@router.get("/global/{global_policy_id}", response_model=PolicyMasterRead)
def get_global_policy(global_policy_id: UUID, token: str, session: Session = Depends(get_session)):
    current_user_id = get_current_user(token)
    current_user = get_current_user_by_id(session, current_user_id)

    if not is_authorised(current_user, ["App Admin", "Org Admin"]):
        raise HTTPException(status_code=403, detail="Unauthorized access")

    policy = session.get(PolicyMaster, global_policy_id)
    if not policy or policy.type != "Global":
        raise HTTPException(status_code=404, detail="Global policy not found")
    
    return policy


# PUT update a global policy
@router.put("/global/{global_policy_id}", response_model=PolicyMasterRead)
def update_global_policy(global_policy_id: UUID, token: str, updated_data: PolicyMasterUpdateInput, session: Session = Depends(get_session)):
    current_user_id = get_current_user(token)
    current_user = get_current_user_by_id(session, current_user_id)

    if not is_authorised(current_user, ["App Admin"]):
        raise HTTPException(status_code=403, detail="Unauthorized access")

    policy = session.get(PolicyMaster, global_policy_id)
    if not policy or policy.type != PolicyType.GLOBAL:
        raise HTTPException(status_code=404, detail="Global policy not found")

    # Update fields
    for field, value in updated_data.dict(exclude_unset=True).items():
        setattr(policy, field, value)
    policy.updated_at = datetime.utcnow()
    policy.updated_by = current_user.id

    session.add(policy)
    session.commit()
    session.refresh(policy)
    return policy


# DELETE a global policy
@router.delete("/global/{global_policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_global_policy(global_policy_id: UUID, token: str, session: Session = Depends(get_session)):
    current_user_id = get_current_user(token)
    current_user = get_current_user_by_id(session, current_user_id)

    if not is_authorised(current_user, ["App Admin"]):
        raise HTTPException(status_code=403, detail="Unauthorized access")

    policy = session.get(PolicyMaster, global_policy_id)
    if not policy or policy.type != "Global":
        raise HTTPException(status_code=404, detail="Global policy not found")

    session.delete(policy)
    session.commit()
    return {"detail":"Deleted succesfully"}






    

