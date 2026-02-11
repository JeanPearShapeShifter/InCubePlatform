import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.agent_session import AgentSession
from app.models.email_log import EmailLog
from app.models.enums import JourneyStatus, PerspectiveStatus
from app.models.journey import Journey
from app.models.perspective import Perspective
from app.models.vdba import Vdba
from app.models.vibe_session import VibeSession
from app.schemas.analytics import DashboardStats, JourneyAnalytics
from app.schemas.vdba import VdbaListItem


async def get_journey_analytics(
    db: AsyncSession,
    journey_id: uuid.UUID,
    org_id: uuid.UUID,
) -> JourneyAnalytics:
    """Get analytics for a single journey."""
    # Verify journey belongs to org
    journey_result = await db.execute(
        select(Journey).where(Journey.id == journey_id, Journey.organization_id == org_id)
    )
    journey = journey_result.scalar_one_or_none()
    if not journey:
        raise NotFoundError("Journey not found")

    # Count completed perspectives
    completed_result = await db.execute(
        select(func.count())
        .select_from(Perspective)
        .where(
            Perspective.journey_id == journey_id,
            Perspective.status == PerspectiveStatus.COMPLETED.value,
        )
    )
    perspectives_completed = completed_result.scalar_one()

    # Sum costs from agent sessions via perspectives
    cost_result = await db.execute(
        select(
            func.coalesce(func.sum(AgentSession.cost_cents), 0),
            func.count(AgentSession.id),
        )
        .select_from(AgentSession)
        .join(Perspective, AgentSession.perspective_id == Perspective.id)
        .where(Perspective.journey_id == journey_id)
    )
    row = cost_result.one()
    total_cost_cents = int(row[0])
    agent_sessions_count = row[1]

    progress_pct = round((perspectives_completed / 12) * 100, 1)

    return JourneyAnalytics(
        journey_id=journey_id,
        perspectives_completed=perspectives_completed,
        progress_pct=progress_pct,
        total_cost_cents=total_cost_cents,
        agent_sessions_count=agent_sessions_count,
    )


async def get_dashboard_stats(
    db: AsyncSession,
    org_id: uuid.UUID,
) -> DashboardStats:
    """Get aggregated dashboard statistics for an organization."""
    # Count journeys by status
    total_result = await db.execute(
        select(func.count()).select_from(Journey).where(Journey.organization_id == org_id)
    )
    total_journeys = total_result.scalar_one()

    active_result = await db.execute(
        select(func.count())
        .select_from(Journey)
        .where(Journey.organization_id == org_id, Journey.status == JourneyStatus.ACTIVE.value)
    )
    active_journeys = active_result.scalar_one()

    completed_result = await db.execute(
        select(func.count())
        .select_from(Journey)
        .where(Journey.organization_id == org_id, Journey.status == JourneyStatus.COMPLETED.value)
    )
    completed_journeys = completed_result.scalar_one()

    # Count VDBAs
    vdba_result = await db.execute(
        select(func.count()).select_from(Vdba).where(Vdba.organization_id == org_id)
    )
    total_vdbas = vdba_result.scalar_one()

    # Sum costs across all journeys
    cost_result = await db.execute(
        select(func.coalesce(func.sum(Journey.total_cost_cents), 0))
        .where(Journey.organization_id == org_id)
    )
    total_cost_cents = int(cost_result.scalar_one())

    # Count vibe sessions across org journeys
    vibe_result = await db.execute(
        select(func.count())
        .select_from(VibeSession)
        .join(Perspective, VibeSession.perspective_id == Perspective.id)
        .join(Journey, Perspective.journey_id == Journey.id)
        .where(Journey.organization_id == org_id)
    )
    total_vibes = vibe_result.scalar_one()

    # Count email logs across org journeys
    email_result = await db.execute(
        select(func.count())
        .select_from(EmailLog)
        .join(Perspective, EmailLog.perspective_id == Perspective.id)
        .join(Journey, Perspective.journey_id == Journey.id)
        .where(Journey.organization_id == org_id)
    )
    total_emails = email_result.scalar_one()

    # Get last 5 VDBAs
    recent_result = await db.execute(
        select(Vdba)
        .where(Vdba.organization_id == org_id)
        .order_by(Vdba.published_at.desc())
        .limit(5)
    )
    recent_vdbas_raw = list(recent_result.scalars().all())
    recent_vdbas = [VdbaListItem.model_validate(v) for v in recent_vdbas_raw]

    return DashboardStats(
        total_journeys=total_journeys,
        active_journeys=active_journeys,
        completed_journeys=completed_journeys,
        total_vdbas=total_vdbas,
        total_cost_cents=total_cost_cents,
        total_vibes=total_vibes,
        total_emails=total_emails,
        recent_vdbas=recent_vdbas,
    )
