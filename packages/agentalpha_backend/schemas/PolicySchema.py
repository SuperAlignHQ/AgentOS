from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class PolicyRead(BaseModel):
    id:UUID
    name:str
    result: Optional[bool] = None
    created_at: datetime
    deleted_at:Optional[datetime]=None
    created_by: UUID

class PolicyListNames(BaseModel):
    policies_list:list[str]