import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PerspectiveResponse(BaseModel):
    id: uuid.UUID
    journey_id: uuid.UUID
    dimension: str
    phase: str
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PerspectiveStatusUpdate(BaseModel):
    status: str = Field(pattern="^(in_progress|completed)$")
