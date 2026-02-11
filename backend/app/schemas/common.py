from pydantic import BaseModel


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class ResponseEnvelope[T](BaseModel):
    status: str = "success"
    data: T
    meta: dict = {}
