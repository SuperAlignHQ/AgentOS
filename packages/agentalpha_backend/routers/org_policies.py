from datetime import datetime
from typing import List
from fastapi import APIRouter,status,Depends,HTTPException
from schemas.PolicyMasterSchema import PolicyMasterInput,PolicyMasterRead,PolicyMasterUpdateInput
from models.models import PolicyMaster,User,Audit,Organization,OrganizationPolicyMap,PolicyType
from sqlmodel import Session, select
from database import get_session
from utils.auth_utils import get_current_user,is_authorised,get_current_user_by_id
from uuid import UUID,uuid4

router=APIRouter()


#Creating a new org_specific Policy

@router.post("/{org_id}/policies",response_model=PolicyMasterRead,status_code=status.HTTP_201_CREATED)
def create_org_specific_policy(request:PolicyMasterInput,org_id:UUID,token:str,session:Session=Depends(get_session)):
    try:
        current_user_id=get_current_user(token)

        current_user=get_current_user_by_id(session,current_user_id)  

        orgId=session.get(Organization,org_id)

        if not orgId:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Organization not found to create Org_Specific_policy")
        
        if not is_authorised(current_user,["Org Admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view Organization  policies."
            )
            

        
        new_policy = PolicyMaster(
                   id=uuid4(),
                   name=request.name,
                   description=request.description,
                   type=PolicyType.ORG,  # Enforced internally
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
        print(request,"before debug")


        org_policy_map=session.get(OrganizationPolicyMap,org_id)
        if org_policy_map:
            org_policy_map.list_of_policy_master_types.append(str(new_policy.name))
        else:
            org_policy_map=OrganizationPolicyMap(
                org_id=org_id,
                list_of_policy_master_types=[str(new_policy.name)]
            )
        session.add(org_policy_map)
        session.commit()
        session.refresh(org_policy_map)

        audit = Audit(
            id=uuid4(),
            created_at=datetime.utcnow(),
            type="POLICY_MASTER_CREATION",
            message=f"Org policy master '{new_policy.name}' created by '{current_user.name}'",
            priority="HIGH",               # Use "LOW", "MEDIUM", "HIGH" 
            action_needed=False,
            assigned_to=current_user.id,             # Can set to current_user.id or approver id if needed
            workflow_id=None 
               )
        session.add(audit)
        session.commit()
        session.refresh(audit)
        print(request,"Seeing the debug for the request")

        return new_policy
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create the Org_specific Policy Master :{str(e)}"
        )

@router.get("/{org_id}/policies",response_model=List[PolicyMasterRead])
def get_all_OrgSpecific_policies(org_id:UUID,token:str,session:Session=Depends(get_session)):
    try:
        current_user_id = get_current_user(token)
        current_user = get_current_user_by_id(session, current_user_id)

        # Step 2: Authorize user (App Admin or Org Admin)
        if not is_authorised(current_user, ["Org Admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view Organization  policies."
            )

        # Step 3: Fetch and return global policies
        org_policies = session.exec(
            select(PolicyMaster).where(PolicyMaster.type == PolicyType.ORG)
        ).all()

        return org_policies  
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Policies not found  {str(e)}"
        ) 

@router.get("/{org_id}/policies/{org_policy_id}",response_model=PolicyMasterRead)
def get_specific_organization_policy(org_id:UUID,org_policy_id:UUID,token:str,session:Session=Depends(get_session)):

    try:
        current_user_id = get_current_user(token)
        current_user = get_current_user_by_id(session, current_user_id)

        orgId=session.get(Organization,org_id)

        if not orgId:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Organization not found")
        

        if not is_authorised(current_user, ["Org Admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view Organization  policies."
            )
        
        #Checking whether the organization id is associated or not
        org_policy_map = session.get(OrganizationPolicyMap, org_id)

        if not org_policy_map or str(org_policy_id) not in org_policy_map.list_of_policy_master_types:
            raise HTTPException(status_code=404, detail="Policy not associated with this organization")
        
        #Fetching the policy with the org_policy_id
        policy = session.get(PolicyMaster, org_policy_id)
        if not policy or policy.type != PolicyType.ORG:
             raise HTTPException(status_code=404, detail="Organization-specific policy not found")
        
        return policy
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Error while fetching {str(e)}"

        )
        

@router.put("/{org_id}/policies/{org_policy_id}", response_model=PolicyMasterRead)
def update_org_policy(org_id: UUID,org_policy_id: UUID, token: str,updated_data: PolicyMasterUpdateInput,session:Session = Depends(get_session)):
    
    current_user_id = get_current_user(token)
    current_user = get_current_user_by_id(session, current_user_id)

    if not is_authorised(current_user, ["Org Admin"]):
        raise HTTPException(status_code=403, detail="Unauthorized access")

    # Check if organization exists
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Get the policy
    policy = session.get(PolicyMaster, org_policy_id)
    if not policy or policy.type != PolicyType.ORG:
        raise HTTPException(status_code=404, detail="Organization-specific policy not found")

    # Ensure this policy is associated with the org
    org_policy_map = session.get(OrganizationPolicyMap, org_id)
    if not org_policy_map or str(policy.name) not in org_policy_map.list_of_policy_master_types:
        raise HTTPException(status_code=404, detail="Policy not associated with this organization")

    # Update fields dynamically
    for field, value in updated_data.dict(exclude_unset=True).items():
        setattr(policy, field, value)

    policy.updated_at = datetime.utcnow()
    policy.updated_by = current_user.id

    session.add(policy)
    session.commit()
    session.refresh(policy)
    return policy


       


@router.delete("/{org_id}/policies/{org_policy_id}", response_model=dict)
def delete_org_policy(
    org_id: UUID,
    org_policy_id: UUID,
    token: str,
    session: Session = Depends(get_session)
):
    # Authenticate & authorize user
    current_user_id = get_current_user(token)
    current_user = get_current_user_by_id(session, current_user_id)
   
    # Validate organization
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if not is_authorised(current_user, ["Org Admin"]):
        raise HTTPException(status_code=403, detail="Unauthorized access")
   
    # Fetch policy and validate type
    policy = session.get(PolicyMaster, org_policy_id)
    if not policy or policy.type != PolicyType.ORG:
        raise HTTPException(status_code=404, detail="Organization-specific policy not found")

    # Ensure the policy belongs to this org
    org_policy_map = session.get(OrganizationPolicyMap, org_id)
    if not org_policy_map or str(policy.name) not in org_policy_map.list_of_policy_master_types:
        raise HTTPException(status_code=404, detail="Policy not associated with this organization")

    # Remove policy ID from org_policy_map
    org_policy_map.list_of_policy_master_types.remove(str(policy.name))
    session.add(org_policy_map)
    
    policy.deleted_at = datetime.utcnow()
    session.add(policy)


    #session.delete(policy)

    # Commit changes
    session.commit()

    audit = Audit(
            id=uuid4(),
            created_at=datetime.utcnow(),
            type="POLICY_MASTER_DELETION",
            message=f"Org policy master '{policy.name}' deleted by '{current_user.name}'",
            priority="HIGH",               # Use "LOW", "MEDIUM", "HIGH" 
            action_needed=False,
            assigned_to=current_user.id,             # Can set to current_user.id or approver id if needed
            workflow_id=None 
               )
    session.add(audit)
    session.commit()
    session.refresh(audit)

    return {"message": f"Policy '{policy.name}' successfully deleted from organization '{org.name}'."}



        




    
    


    
         





   