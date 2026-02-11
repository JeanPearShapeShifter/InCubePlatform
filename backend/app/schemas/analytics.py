import uuid

from pydantic import BaseModel

from app.schemas.vdba import VdbaListItem


class JourneyAnalytics(BaseModel):
    journey_id: uuid.UUID
    perspectives_completed: int
    perspectives_total: int = 12
    progress_pct: float  # 0-100
    total_cost_cents: int
    agent_sessions_count: int


class DashboardStats(BaseModel):
    total_journeys: int
    active_journeys: int
    completed_journeys: int
    total_vdbas: int
    total_cost_cents: int
    total_vibes: int
    total_emails: int
    recent_vdbas: list[VdbaListItem]
