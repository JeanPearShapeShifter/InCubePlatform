import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.analytics import DashboardStats, JourneyAnalytics
from app.schemas.common import ResponseEnvelope
from app.services import analytics as analytics_service

router = APIRouter(prefix="/analytics")


@router.get("/journeys/{journey_id}")
async def get_journey_analytics(
    journey_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[JourneyAnalytics]:
    analytics = await analytics_service.get_journey_analytics(
        db, journey_id, current_user.organization_id
    )
    return ResponseEnvelope(data=analytics)


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[DashboardStats]:
    stats = await analytics_service.get_dashboard_stats(
        db, current_user.organization_id
    )
    return ResponseEnvelope(data=stats)
