from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class DocumentInput(BaseModel):
    format:str
    category:str
    name:str
    url:str
    ocr_result:Optional[dict]=None

class DocumentUpdateInput(BaseModel):
    format:Optional[str]=None
    category:Optional[str]=None
    name:Optional[str]=None
    url:Optional[str]=None
    ocr_result:Optional[dict]=None


class DocumentRead(BaseModel):
    id:UUID
    format:str
    type:str
    category:str
    name:str
    url:str
    ocr_result:Optional[dict]=None
    workflow_id:UUID
    created_at:datetime
    updated_at:Optional[datetime]=None
    deleted_at:Optional[datetime]=None



