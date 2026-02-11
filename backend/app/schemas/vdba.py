import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class VdbaCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    export_format: str = Field(default="pdf", pattern="^(pdf|docx|json)$")


class VdbaResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    journey_id: uuid.UUID
    bank_instance_id: uuid.UUID
    published_at: datetime
    export_format: str
    version: int

    model_config = {"from_attributes": True}


class VdbaDetailResponse(VdbaResponse):
    export_url: str | None = None
    journey_title: str | None = None


class VdbaListItem(BaseModel):
    id: uuid.UUID
    title: str
    journey_id: uuid.UUID
    published_at: datetime
    export_format: str

    model_config = {"from_attributes": True}
