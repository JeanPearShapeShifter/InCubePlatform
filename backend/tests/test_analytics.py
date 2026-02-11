import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.errors import NotFoundError
from app.schemas.analytics import DashboardStats, JourneyAnalytics
from app.services import analytics as analytics_service


def _make_journey_ns(**kwargs) -> SimpleNamespace:
    defaults = {
        "id": uuid.uuid4(),
        "goal_id": uuid.uuid4(),
        "organization_id": uuid.uuid4(),
        "status": "active",
        "perspectives_completed": 0,
        "total_cost_cents": 0,
        "completed_at": None,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_vdba_ns(**kwargs) -> SimpleNamespace:
    defaults = {
        "id": uuid.uuid4(),
        "journey_id": uuid.uuid4(),
        "organization_id": uuid.uuid4(),
        "title": "Test VDBA",
        "description": "",
        "bank_instance_id": uuid.uuid4(),
        "published_at": datetime.now(UTC),
        "export_url": None,
        "export_format": "json",
        "version": 1,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_db_mock() -> MagicMock:
    db = MagicMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock()
    db.delete = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_get_journey_analytics():
    """Journey analytics should return correct counts and cost."""
    db = _make_db_mock()
    org_id = uuid.uuid4()
    journey_id = uuid.uuid4()
    journey = _make_journey_ns(id=journey_id, organization_id=org_id)

    # Mock: journey lookup, completed count, cost+session count
    journey_result = MagicMock()
    journey_result.scalar_one_or_none.return_value = journey

    completed_result = MagicMock()
    completed_result.scalar_one.return_value = 7

    cost_result = MagicMock()
    cost_result.one.return_value = (150, 25)  # cost_cents, sessions_count

    db.execute = AsyncMock(side_effect=[journey_result, completed_result, cost_result])

    analytics = await analytics_service.get_journey_analytics(db, journey_id, org_id)

    assert isinstance(analytics, JourneyAnalytics)
    assert analytics.journey_id == journey_id
    assert analytics.perspectives_completed == 7
    assert analytics.perspectives_total == 12
    assert analytics.progress_pct == pytest.approx(58.3, abs=0.1)
    assert analytics.total_cost_cents == 150
    assert analytics.agent_sessions_count == 25


@pytest.mark.asyncio
async def test_get_journey_analytics_not_found():
    """Journey analytics should raise NotFoundError for missing journey."""
    db = _make_db_mock()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(NotFoundError, match="Journey not found"):
        await analytics_service.get_journey_analytics(db, uuid.uuid4(), uuid.uuid4())


@pytest.mark.asyncio
async def test_get_journey_analytics_zero_sessions():
    """Journey analytics should handle zero agent sessions gracefully."""
    db = _make_db_mock()
    org_id = uuid.uuid4()
    journey_id = uuid.uuid4()
    journey = _make_journey_ns(id=journey_id, organization_id=org_id)

    journey_result = MagicMock()
    journey_result.scalar_one_or_none.return_value = journey

    completed_result = MagicMock()
    completed_result.scalar_one.return_value = 0

    cost_result = MagicMock()
    cost_result.one.return_value = (0, 0)

    db.execute = AsyncMock(side_effect=[journey_result, completed_result, cost_result])

    analytics = await analytics_service.get_journey_analytics(db, journey_id, org_id)

    assert analytics.perspectives_completed == 0
    assert analytics.progress_pct == 0.0
    assert analytics.total_cost_cents == 0
    assert analytics.agent_sessions_count == 0


@pytest.mark.asyncio
async def test_get_journey_analytics_all_completed():
    """Journey analytics should show 100% when all perspectives are done."""
    db = _make_db_mock()
    org_id = uuid.uuid4()
    journey_id = uuid.uuid4()
    journey = _make_journey_ns(id=journey_id, organization_id=org_id)

    journey_result = MagicMock()
    journey_result.scalar_one_or_none.return_value = journey

    completed_result = MagicMock()
    completed_result.scalar_one.return_value = 12

    cost_result = MagicMock()
    cost_result.one.return_value = (500, 108)

    db.execute = AsyncMock(side_effect=[journey_result, completed_result, cost_result])

    analytics = await analytics_service.get_journey_analytics(db, journey_id, org_id)

    assert analytics.perspectives_completed == 12
    assert analytics.progress_pct == 100.0


@pytest.mark.asyncio
async def test_get_dashboard_stats():
    """Dashboard stats should aggregate correctly across all org data."""
    db = _make_db_mock()
    org_id = uuid.uuid4()
    vdbas = [_make_vdba_ns(organization_id=org_id) for _ in range(2)]

    # Mock sequence: total_journeys, active, completed, vdba_count, cost_sum,
    #               vibes_count, emails_count, recent_vdbas
    total_j = MagicMock()
    total_j.scalar_one.return_value = 5

    active_j = MagicMock()
    active_j.scalar_one.return_value = 3

    completed_j = MagicMock()
    completed_j.scalar_one.return_value = 2

    vdba_count = MagicMock()
    vdba_count.scalar_one.return_value = 2

    cost_sum = MagicMock()
    cost_sum.scalar_one.return_value = 1000

    vibes = MagicMock()
    vibes.scalar_one.return_value = 10

    emails = MagicMock()
    emails.scalar_one.return_value = 15

    recent = MagicMock()
    recent.scalars.return_value.all.return_value = vdbas

    db.execute = AsyncMock(
        side_effect=[total_j, active_j, completed_j, vdba_count, cost_sum, vibes, emails, recent]
    )

    stats = await analytics_service.get_dashboard_stats(db, org_id)

    assert isinstance(stats, DashboardStats)
    assert stats.total_journeys == 5
    assert stats.active_journeys == 3
    assert stats.completed_journeys == 2
    assert stats.total_vdbas == 2
    assert stats.total_cost_cents == 1000
    assert stats.total_vibes == 10
    assert stats.total_emails == 15
    assert len(stats.recent_vdbas) == 2


@pytest.mark.asyncio
async def test_get_dashboard_stats_empty_org():
    """Dashboard stats should handle an org with no data."""
    db = _make_db_mock()
    org_id = uuid.uuid4()

    results = []
    for val in [0, 0, 0, 0, 0, 0, 0]:
        m = MagicMock()
        m.scalar_one.return_value = val
        results.append(m)

    # Empty recent VDBAs
    recent = MagicMock()
    recent.scalars.return_value.all.return_value = []
    results.append(recent)

    db.execute = AsyncMock(side_effect=results)

    stats = await analytics_service.get_dashboard_stats(db, org_id)

    assert stats.total_journeys == 0
    assert stats.active_journeys == 0
    assert stats.completed_journeys == 0
    assert stats.total_vdbas == 0
    assert stats.total_cost_cents == 0
    assert stats.total_vibes == 0
    assert stats.total_emails == 0
    assert stats.recent_vdbas == []


@pytest.mark.asyncio
async def test_journey_analytics_schema():
    """JourneyAnalytics schema should validate correctly."""
    data = JourneyAnalytics(
        journey_id=uuid.uuid4(),
        perspectives_completed=6,
        progress_pct=50.0,
        total_cost_cents=200,
        agent_sessions_count=12,
    )
    assert data.perspectives_total == 12
    assert data.progress_pct == 50.0


@pytest.mark.asyncio
async def test_dashboard_stats_schema():
    """DashboardStats schema should validate correctly."""
    data = DashboardStats(
        total_journeys=5,
        active_journeys=3,
        completed_journeys=2,
        total_vdbas=1,
        total_cost_cents=500,
        total_vibes=10,
        total_emails=8,
        recent_vdbas=[],
    )
    assert data.total_journeys == 5
    assert data.recent_vdbas == []
