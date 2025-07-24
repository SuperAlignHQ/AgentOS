from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from models.models import PolicyListJson,DocumentListJson

class PolicyMasterInput(BaseModel):
    name: str
    description: str
    policy_function: str
    list_of_documents: Optional[DocumentListJson]=None
    variables: Optional[dict]=None

class PolicyMasterUpdateInput(BaseModel):
    name: Optional[str]=None
    description: Optional[str]=None
    policy_function: Optional[str]=None
    list_of_documents: Optional[DocumentListJson]=None
    variables: Optional[dict]=None

class PolicyMasterRead(BaseModel):
    id: UUID
    name: str
    description: str
    type: str
    policy_function: str
    list_of_documents: Optional[DocumentListJson]=None
    variables: Optional[dict]=None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 
