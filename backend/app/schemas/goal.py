import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import PaginationMeta


class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str = ""
    type: str = Field(default="custom", pattern="^(predefined|custom)$")


class GoalResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    type: str
    organization_id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class GoalListResponse(BaseModel):
    goals: list[GoalResponse]
    pagination: PaginationMeta
