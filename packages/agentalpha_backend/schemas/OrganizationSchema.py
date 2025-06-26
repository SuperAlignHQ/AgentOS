

from uuid import UUID
from pydantic import BaseModel


class OrganizationRequest(BaseModel):
    name:str


class OrganizationRead(BaseModel):
    id:UUID
    name:str

    class Config:
        orm_mode=True