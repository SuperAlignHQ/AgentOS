from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from models.models import Status

class WorkFlowInput(BaseModel):
    name: str
    documents_list: Optional[dict]=None
    policies_list: Optional[dict]=None
    status:Status

class WorkFlowUpdateInput(BaseModel):
    name: Optional[str]=None
    documents_list: Optional[dict]=None
    policies_list: Optional[dict]=None
    status:Optional[Status]=None


class WorkFlowRead(BaseModel):
    id:UUID
    name:str
    documents_list:Optional[dict]=None
    policies_list:Optional[dict]=None
    status:Status
    created_at:datetime
    updated_at:Optional[datetime]=None
    org_id:UUID

    class Config:
        orm_mode=True  
    