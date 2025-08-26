from pydantic import BaseModel


class CreateUsecaseRequest(BaseModel):
    name: str


class UpdateUsecaseRequest(BaseModel):
    name: str