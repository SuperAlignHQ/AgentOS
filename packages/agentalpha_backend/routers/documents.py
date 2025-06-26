from datetime import datetime
from fastapi import APIRouter,HTTPException,status,Depends
from sqlmodel import select,Session
from uuid import UUID, uuid4
from models.models import Document, DocumentTypeMaster, Organization, Workflow
from database import get_session
from typing import List
from schemas.DocumentSchema import DocumentInput,DocumentRead,DocumentUpdateInput

router=APIRouter()

@router.post("/document-types/{doc_type_id}/documents",response_model=DocumentRead,status_code=status.HTTP_201_CREATED)
def create_document(org_id:UUID, workflow_id:UUID, doc_type_id:UUID,request:DocumentInput,session:Session=Depends(get_session)):
    try:

        # ✅ Validate organization
        org = session.get(Organization, org_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # ✅ Validate workflow and its org match
        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        if workflow.org_id != org_id:
            raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization")

        # ✅ Validate document type
        document_type = session.get(DocumentTypeMaster, doc_type_id)
        if not document_type:
            raise HTTPException(status_code=404, detail="Document type not found")

        
        document=Document(
            id=uuid4(),
            format=request.format,
            category=request.category,
            name=request.name,
            url=request.url,
            ocr_result=request.ocr_result,
            created_at=datetime.utcnow(),
            workflow_id=workflow_id,
            type=document_type.type,

        )

        session.add(document)
        session.commit()
        session.refresh(document)
        return document
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail= f"Error Document : {str(e)}")
    

@router.get("/documents", response_model=List[DocumentRead])
def list_documents(org_id: UUID, workflow_id: UUID,session:Session=Depends(get_session)):
    # ✅ Validate organization
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # ✅ Validate workflow and its org match
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization")

    documents = session.exec(select(Document).where(Document.workflow_id == workflow_id)).all()
    if not documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents found")
    return documents


@router.get("/documents/{document_id}", response_model=DocumentRead)
def get_document(org_id: UUID, workflow_id: UUID, document_id: UUID,session:Session=Depends(get_session)):
    # ✅ Validate organization
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # ✅ Validate workflow and its org match
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization")

    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    if document.workflow_id!=workflow_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Worflow doesnt belong to this organization")

    return document


@router.put("/documents/{document_id}", response_model=DocumentRead)
def update_document(org_id: UUID, workflow_id: UUID, document_id: UUID, updated_doc: DocumentUpdateInput,session:Session=Depends(get_session)):
    # ✅ Validate organization
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # ✅ Validate workflow and its org match
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.org_id != org_id:
        raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization")

    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    if document.workflow_id!=workflow_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Worflow doesnt belong to this organization")

    for key, value in updated_doc.dict(exclude_unset=True).items():
        setattr(document, key, value)

    document.updated_at = datetime.utcnow()
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(org_id: UUID, workflow_id: UUID, document_id: UUID,session:Session=Depends(get_session)):
    try:
        org = session.get(Organization, org_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        if workflow.org_id != org_id:
            raise HTTPException(status_code=400, detail="Workflow does not belong to the specified organization")
        
        document = session.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
        if document.workflow_id!=workflow_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Worflow doesnt belong to this organization")

        document.deleted_at=datetime.utcnow()
        session.add(document)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete document: {str(e)}")
