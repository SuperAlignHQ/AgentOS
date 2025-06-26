from datetime import datetime
from fastapi import APIRouter, HTTPException, Path, Depends, status
from sqlmodel import select, Session
from uuid import UUID, uuid4
from typing import List

from models.models import Workflow
from database import get_session
from schemas.WorkFlowSchema import WorkFlowInput,WorkFlowRead

router = APIRouter()


@router.post("/", response_model=WorkFlowRead, status_code=status.HTTP_201_CREATED)
def create_workflow(org_id: UUID, request: WorkFlowInput, session: Session = Depends(get_session)):
    try:
        workflow=Workflow(
            id=uuid4(),
            name=request.name,
            documents_list=request.documents_list,
            policies_list=request.policies_list,
            org_id=org_id,
            status=request.status,
            created_at=datetime.utcnow(),
        )
        
        session.add(workflow)
        session.commit()
        session.refresh(workflow)
        return workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating workflow: {str(e)}")


@router.get("/", response_model=List[WorkFlowRead])
def list_workflows(org_id: UUID, session: Session = Depends(get_session)):
    workflows = session.exec(select(Workflow).where(Workflow.org_id == org_id)).all()
    if workflows is None or len(workflows) == 0:
        raise HTTPException(status_code=404, detail="No workflows found for this organization")
    return workflows


@router.get("/{workflow_id}", response_model=WorkFlowRead)
def get_workflow(org_id: UUID, workflow_id: UUID, session: Session = Depends(get_session)):
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(status_code=400, detail="Workflow does not belong to this organization")
    return workflow


@router.put("/{workflow_id}", response_model=WorkFlowRead)
def update_workflow(org_id: UUID, workflow_id: UUID, request: WorkFlowInput, session: Session = Depends(get_session)):
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(status_code=400, detail="Workflow does not belong to this organization")

    try:
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workflow, field, value)
        
        workflow.updated_at=datetime.utcnow()
        
        session.add(workflow)
        session.commit()
        session.refresh(workflow)
        return workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating workflow: {str(e)}")



@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(org_id: UUID, workflow_id: UUID, session: Session = Depends(get_session)):
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(status_code=400, detail="Workflow does not belong to this organization")

    try:
        session.delete(workflow)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting workflow: {str(e)}")
