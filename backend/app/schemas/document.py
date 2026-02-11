import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=500)
    file_type: str = Field(min_length=1, max_length=50)
    minio_key: str = Field(min_length=1, max_length=1000)
    file_size: int = Field(gt=0)


class DocumentResponse(BaseModel):
    id: uuid.UUID
    perspective_id: uuid.UUID
    filename: str
    file_type: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
