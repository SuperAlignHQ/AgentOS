from fastapi import APIRouter,HTTPException,status,Depends
from sqlmodel import select,Session
from uuid import UUID, uuid4
from typing import List
from schemas.DocumentTypeSchema import DocumentTypeInput,DocumentTypeRead,DocumentTypeUpdateInput
from models.models import DocumentTypeMaster,Organization,Workflow
from database import get_session

router=APIRouter()


@router.post('/document-types', response_model=DocumentTypeRead, status_code=status.HTTP_201_CREATED)
def create_document_master_type(org_id: UUID,workflow_id: UUID,request: DocumentTypeInput,session: Session = Depends(get_session)):
    # ✅ 1. Validate Organization exists
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # ✅ 2. Validate Workflow exists and belongs to the organization
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization")

    # ✅ 3. Check for duplicate document type
    existing = session.exec(
        select(DocumentTypeMaster).where(DocumentTypeMaster.type == request.type)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Document type with this type already exists"
        )

    # ✅ 4. Create and persist new DocumentTypeMaster
    document_type = DocumentTypeMaster(
        id=uuid4(),
        type=request.type,
        no_of_fields=request.no_of_fields,
        fields_list=request.fields_list
    )

    session.add(document_type)
    session.commit()
    session.refresh(document_type)

    return document_type



@router.get("/document-types", response_model=List[DocumentTypeRead])
def list_document_types(org_id: UUID, workflow_id: UUID, session: Session = Depends(get_session)):
    
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    #Validate Workflow exists and belongs to the organization
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization")

    document_types = session.exec(select(DocumentTypeMaster)).all()
    return document_types


@router.get("/document-types/{doc_type_id}", response_model=DocumentTypeRead)
def get_document_type(org_id: UUID, workflow_id: UUID, doc_type_id: UUID, session: Session = Depends(get_session)):
    
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Validate Workflow exists and belongs to the organization
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization")


    document_type = session.get(DocumentTypeMaster, doc_type_id)
    if not document_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    return document_type

@router.put("/document-types/{doc_type_id}", response_model=DocumentTypeRead)
def update_document_type(org_id: UUID, workflow_id: UUID, doc_type_id: UUID, updated_data: DocumentTypeUpdateInput, session: Session = Depends(get_session)):
    
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    #  Validate Workflow exists and belongs to the organization
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization") 
    

    document_type = session.get(DocumentTypeMaster, doc_type_id)
    if not document_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    
    if updated_data.type and updated_data.type != document_type.type:
        existing = session.exec(
            select(DocumentTypeMaster).where(DocumentTypeMaster.type == updated_data.type)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Document type with this type already exists")

    updated_fields = updated_data.dict(exclude_unset=True)
    for key, value in updated_fields.items():
        setattr(document_type, key, value)
    
    session.add(document_type)
    session.commit()
    session.refresh(document_type)
    return document_type

@router.delete("/{doc_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_type(org_id: UUID, workflow_id: UUID, doc_type_id: UUID, session: Session = Depends(get_session)):
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    #  Validate Workflow exists and belongs to the organization
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization") 
    
    document_type = session.get(DocumentTypeMaster, doc_type_id)
    if not document_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    session.delete(document_type)
    session.commit()
    return {"detail": "Document type deleted"}
