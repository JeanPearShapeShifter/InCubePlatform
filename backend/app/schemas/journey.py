import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import PaginationMeta
from app.schemas.perspective import PerspectiveResponse


class JourneyCreate(BaseModel):
    goal_id: uuid.UUID


class JourneyResponse(BaseModel):
    id: uuid.UUID
    goal_id: uuid.UUID
    organization_id: uuid.UUID
    status: str
    perspectives_completed: int
    total_cost_cents: int
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class JourneyDetailResponse(JourneyResponse):
    perspectives: list[PerspectiveResponse] = []
    bank_instances: list = []


class JourneyStatusUpdate(BaseModel):
    status: str = Field(pattern="^(completed|archived)$")


class JourneyListResponse(BaseModel):
    journeys: list[JourneyResponse]
    pagination: PaginationMeta
