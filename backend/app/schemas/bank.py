import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BankCreate(BaseModel):
    synopsis: str = Field(min_length=1, max_length=5000)


class BankInstanceResponse(BaseModel):
    id: uuid.UUID
    perspective_id: uuid.UUID
    type: str
    synopsis: str
    decision_audit: list[Any]
    agent_assessments: dict[str, Any]
    documents_count: int
    vibes_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BankTimelineResponse(BaseModel):
    bank_instances: list[BankInstanceResponse]
