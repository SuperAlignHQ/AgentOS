from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class DocumentTypeInput(BaseModel):
    type:str
    no_of_fields:int
    fields_list:Optional[dict]=None

class DocumentTypeUpdateInput(BaseModel):
    type:Optional[str]=None
    no_of_fields:Optional[int]=None
    fields_list:Optional[dict]=None


class DocumentTypeRead(BaseModel):
    id:UUID
    type:str
    no_of_fields:int
    fields_list:Optional[dict]=None

    class Config:
        orm_mode=True


