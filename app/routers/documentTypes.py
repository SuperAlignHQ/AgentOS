from fastapi import APIRouter,HTTPException,status,Depends
from sqlmodel import select,Session
from uuid import UUID
from typing import List


from app.models.models import DocumentTypeMaster
from app.database import get_session

router=APIRouter()


@router.post('/document-types',status_code=status.HTTP_201_CREATED)
def create_document_master_type(org_id:UUID,workflow_id:UUID,document_type:DocumentTypeMaster,session=Depends(get_session)):
    existing = session.exec(select(DocumentTypeMaster).where(DocumentTypeMaster.type == document_type.type)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Document type with this type already exists")
    session.add(document_type)
    session.commit()
    session.refresh(document_type)
    return document_type

@router.get("/document-types", response_model=List[DocumentTypeMaster])
def list_document_types(org_id: UUID, workflow_id: UUID, session: Session = Depends(get_session)):
    document_types = session.exec(select(DocumentTypeMaster)).all()
    return document_types


@router.get("/document-types/{doc_type_id}", response_model=DocumentTypeMaster)
def get_document_type(org_id: UUID, workflow_id: UUID, doc_type_id: UUID, session: Session = Depends(get_session)):
    document_type = session.get(DocumentTypeMaster, doc_type_id)
    if not document_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    return document_type

@router.put("/document-types/{doc_type_id}", response_model=DocumentTypeMaster)
def update_document_type(org_id: UUID, workflow_id: UUID, doc_type_id: UUID, updated_data: DocumentTypeMaster, session: Session = Depends(get_session)):
    document_type = session.get(DocumentTypeMaster, doc_type_id)
    if not document_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    updated_fields = updated_data.dict(exclude_unset=True)
    for key, value in updated_fields.items():
        setattr(document_type, key, value)
    session.add(document_type)
    session.commit()
    session.refresh(document_type)
    return document_type

@router.delete("/{doc_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_type(org_id: UUID, workflow_id: UUID, doc_type_id: UUID, session: Session = Depends(get_session)):
    document_type = session.get(DocumentTypeMaster, doc_type_id)
    if not document_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    session.delete(document_type)
    session.commit()
    return {"detail": "Document type deleted"}
