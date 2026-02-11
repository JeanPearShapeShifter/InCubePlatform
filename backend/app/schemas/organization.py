import uuid
from datetime import datetime

from pydantic import BaseModel


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    logo_url: str | None
    monthly_budget_cents: int
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationUpdate(BaseModel):
    name: str | None = None
    logo_url: str | None = None
    monthly_budget_cents: int | None = None
