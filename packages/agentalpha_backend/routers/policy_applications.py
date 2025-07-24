from typing import List
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends, HTTPException,status
from sqlmodel import Session
from database import get_session
from models.models import Organization, Policy, Status, Workflow,PolicyMaster,OrganizationPolicyMap,PolicyListJson
from utils.auth_utils import get_current_user, get_current_user_by_id, is_authorised
from schemas.PolicySchema import PolicyRead,PolicyListNames
from datetime import datetime
from schemas.PolicyMasterSchema import PolicyMasterRead

router=APIRouter()

#apply all polices specific to the organization
@router.post("",response_model=list[PolicyRead])
def apply_all_policies(org_id:UUID,workflow_id:UUID,token:str,session:Session=Depends(get_session)):
    try:
        current_user_id=get_current_user(token)

        current_user=get_current_user_by_id(session,current_user_id)  

        orgId=session.get(Organization,org_id)

        if not orgId:
            raise HTTPException(status_code=Status.HTTP_404_NOT_FOUND,detail="Organization not found to create Org_Specific_policy")
        
        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        if workflow.org_id != org_id:
            raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization")
        
        if not is_authorised(current_user,["Org Admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view Organization  policies."
            )
        
        org_policy_map = session.get(OrganizationPolicyMap, org_id)

        if not org_policy_map or not org_policy_map.list_of_policy_master_types:
            raise HTTPException(404, "No org-specific policies found")

        policies = org_policy_map.list_of_policy_master_types
        
        if workflow.policies_list is None:
            workflow.policies_list = []

        policy_list=[]
        for name in policies:
            #Appplying policy validation results and add result field at this instance result field is empty
            new_policy=Policy(
                id=uuid4(),
                name=name,
                created_at=datetime.utcnow(),
                created_by=current_user_id,
                workflow_id=workflow_id
            )
            policy_list.append(new_policy)
            session.add(new_policy)

            policy_json=PolicyListJson(
                name=new_policy.name,
                id=str(new_policy.id),
                result=None
            )
            
            updated = False
            for existing_policy in workflow.policies_list:
                    if existing_policy['id'] == new_policy.id:
                        existing_policy.update(policy_json.dict())  # Update the policy
                        updated = True
                        break
            if not updated:
                workflow.policies_list.append(policy_json.dict())  # Append if not updated
            session.add(workflow)
        session.commit()
        
        return policy_list
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= f"Failed to apply organization Specific policies {str(e)}"
        )

#apply a specific policy
@router.post("/{policy_id}",response_model=PolicyRead)
def apply_specific_policy_to_workflow(
    org_id: UUID,
    workflow_id: UUID,
    policy_id: UUID,
    token: str,
    session: Session = Depends(get_session)
):
    # 1. Auth: get current user
    current_user_id = get_current_user(token)
    current_user = get_current_user_by_id(session, current_user_id)

    # 2. Validate org
    organization = session.get(Organization, org_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    # 3. Validate workflow
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization")

    # 4. Validate policy
    policy_master = session.get(PolicyMaster, policy_id)
    if not policy_master:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # 5. Authorisation
    if not is_authorised(current_user, ["Org Admin", "Member"]):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to apply policies to this workflow."
        )

    # 6. Add policy to workflow.policies_list
    if workflow.policies_list is None:
        workflow.policies_list = []

    
    policy=Policy(
        id=uuid4(),
        name=policy_master.name,
        created_at=datetime.utcnow(),
        created_by=current_user_id,
        workflow_id=workflow_id,
    )
    policy_json=PolicyListJson(
                name=policy.name,
                id=str(policy.id),
                result=None
            )
            
    updated = False
    for existing_policy in workflow.policies_list:
            if existing_policy['id'] == policy.id:
                existing_policy.update(policy_json.dict())  # Update the policy
                updated = True
                break
    if not updated:
        workflow.policies_list.append(policy_json.dict())  # Append if not updated

    # 8. Save all
    session.add(workflow)
    session.add(policy)
    session.commit()
    session.refresh(workflow)

    return policy

        
@router.get("",response_model=List[PolicyListJson])
def list_policies_for_workflow( org_id: UUID, workflow_id: UUID, token: str, session: Session = Depends(get_session)):
    # Authenticate
    current_user_id = get_current_user(token)
    current_user = get_current_user_by_id(session, current_user_id)

    # Check org exists
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(404, detail="Organization not found")

    # Check workflow exists
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(400, detail="Workflow does not belong to this organization")

    # Authorize
    if not is_authorised(current_user, ["Org Admin", "Member"]):
        raise HTTPException(403, detail="Not authorized to view workflow policies")

    # Get policies_list
    if not workflow.policies_list:
        return []

    # Defensive check
    if not isinstance(workflow.policies_list, list):
        raise HTTPException(500, detail="Workflow policies_list field is not a list in the database")

    # Fetch full PolicyMaster objects
    
    return workflow.policies_list


@router.get("/{policy_id}",response_model=PolicyMasterRead)
def get_specific_policy_for_workflow( org_id: UUID,workflow_id: UUID,policy_id: UUID,token: str,session: Session = Depends(get_session)):
    # Authenticate
    current_user_id = get_current_user(token)
    current_user = get_current_user_by_id(session, current_user_id)

    #  Validate org exists
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(404, detail="Organization not found")

    # Validate workflow exists
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, detail="Workflow not found")

    # Check workflow belongs to org
    if workflow.org_id != org_id:
        raise HTTPException(400, detail="Workflow does not belong to the specified organization")

    # Authorize
    if not is_authorised(current_user, ["Org Admin", "Member"]):
        raise HTTPException(403, detail="You are not authorized to view policies for this workflow")

    #  ensure policies_list is valid
    if not workflow.policies_list or not isinstance(workflow.policies_list, list):
        raise HTTPException(404, detail="No policies applied to this workflow")

    #  Check if policy_name is in the applied list
    
    policy_master=session.get(PolicyMaster,policy_id)
    
    if not any(existing_policy['name'] == policy_master.name for existing_policy in workflow.policies_list):
        raise HTTPException(404, detail=f"Policy '{policy_master.name}' is not applied to this workflow")

    return policy_master


#Deleting specific policy from the workflows
@router.delete("/{policy_id}", response_model=PolicyRead)
def remove_specific_policy_from_workflow(org_id: UUID,workflow_id: UUID,policy_id: UUID,token: str,session: Session = Depends(get_session)):
    try:
        # 1. Auth: Get the current user
        current_user_id = get_current_user(token)
        current_user = get_current_user_by_id(session, current_user_id)

        # 2. Validate org
        organization = session.get(Organization, org_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        # 3. Validate workflow
        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        if workflow.org_id != org_id:
            raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization")

        # 4. Validate if the current user is authorized
        if not is_authorised(current_user, ["Org Admin", "Admin member"]):
            raise HTTPException(status_code=403, detail="You are not authorized to remove policies from this workflow.")
        
        # 5. Remove the policy from the Policy table (if necessary)
        policy_master=session.get(PolicyMaster,policy_id)
        policy = session.query(Policy).filter(Policy.name == policy_master.name, Policy.workflow_id == workflow_id).first()

        if not policy:
            raise HTTPException(status_code=404, detail=f"Policy '{policy_master.name}' not found in this workflow.")
    
        policy.deleted_at=datetime.utcnow()
        session.add(policy)

       

        # 7. Remove the policy from the workflow.policies_list
        workflow.policies_list = [policy for policy in workflow.policies_list if policy['name'] != policy_master.name]

        
        # 8. Commit the changes to the database
        session.add(workflow)
        session.commit()

        # 9. Return the removed policy details
        return policy

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to remove the policy from the workflow: {str(e)}"
        )

@router.delete("", response_model=List[PolicyRead])
def remove_all_policies_from_workflow(org_id: UUID,workflow_id: UUID,token: str,session: Session = Depends(get_session)):
    try:
        # 1. Auth: Get the current user
        current_user_id = get_current_user(token)
        current_user = get_current_user_by_id(session, current_user_id)
        print(f"helloo iam debugging line --------------------------------------------------------------------")

        # 2. Validate org
        organization = session.get(Organization, org_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        # 3. Validate workflow
        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        if workflow.org_id != org_id:
            raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization")

        # 4. Authorize: Check if the user is an Org Admin or Admin member of the workflow
        if not is_authorised(current_user, ["Org Admin", "Admin member"]):
            raise HTTPException(status_code=403, detail="You are not authorized to remove policies from this workflow.")

        # 5. Retrieve all policy ids from the workflow's policies_list
        policy_ids_to_remove = []
        for policy in workflow.policies_list:
            try:
                print(f"Policy ID (before UUID conversion): {policy['id']}")  # Debugging print
                policy_ids_to_remove.append(UUID(policy['id']))
            except ValueError as e:
                print(f"Error converting policy ID to UUID: {policy['id']}, Error: {e}")
                raise HTTPException(status_code=400, detail=f"Invalid UUID format for policy ID: {policy['id']}")

        if not policy_ids_to_remove:
            raise HTTPException(status_code=404, detail="No policies are applied to this workflow.")

        # 6. Soft delete the policies (set deleted_at)
        policies_to_remove = session.query(Policy).filter(Policy.id.in_(policy_ids_to_remove)).all()

        if not policies_to_remove:
            raise HTTPException(status_code=404, detail="Policies not found in the system.")

        # Update the policies to mark them as deleted (soft delete)
        for policy in policies_to_remove:
            policy.deleted_at = datetime.utcnow()
            session.add(policy)

        # 7. Remove policies from the workflow's policies_list
        workflow.policies_list = None  # Remove all policies from the list

        # 8. Commit the changes to the database
        session.add(workflow)
        session.commit()

        # Return the list of policies that were removed (optional)
        return policies_to_remove

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to remove policies from the workflow: {str(e)}"
        )
