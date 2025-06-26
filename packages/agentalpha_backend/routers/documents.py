from datetime import datetime
from fastapi import APIRouter,HTTPException,status,Depends
from sqlmodel import select,Session
from uuid import UUID
from models.models import Document
from database import get_session
from typing import List

router=APIRouter()

@router.post("/document-types/{doc_type_id}/documents",response_model=Document,status_code=status.HTTP_201_CREATED)
def create_document(org_id:UUID, workflow_id:UUID, doc_type_id:UUID,document:Document,session:Session=Depends(get_session)):
    try:
        session.add(document)
        session.commit()
        session.refresh(document)
        return document
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail= f"Error Document : {str(e)}")
    

@router.get("/documents", response_model=List[Document])
def list_documents(org_id: UUID, workflow_id: UUID,session:Session=Depends(get_session)):
    documents = session.exec(select(Document).where(Document.workflow_id == workflow_id)).all()
    if not documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents found")
    return documents


@router.get("/documents/{document_id}", response_model=Document)
def get_document(org_id: UUID, workflow_id: UUID, document_id: UUID,session:Session=Depends(get_session)):
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.put("/documents/{document_id}", response_model=Document)
def update_document(org_id: UUID, workflow_id: UUID, document_id: UUID, updated_doc: Document,session:Session=Depends(get_session)):
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

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
        document = session.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        session.delete(document)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete document: {str(e)}")
