from fastapi import Query
from pydantic import BaseModel


class PaginationQuery(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(10, ge=1)


class EmptyResponse(BaseModel):
    message: str = "Success"
    status_code: int = 200