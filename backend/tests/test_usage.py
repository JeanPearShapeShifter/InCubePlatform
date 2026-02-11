import uuid
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.settings import DailyUsage, UsageBreakdownResponse, UsageEntry, UsageSummaryResponse
from app.services import usage as usage_service


def _make_db_mock() -> MagicMock:
    db = MagicMock()
    db.execute = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_get_usage_summary():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    totals_result = MagicMock()
    totals_result.one.return_value = SimpleNamespace(
        total_cost=150.5, total_in=10000, total_out=5000, total_calls=25
    )

    daily_result = MagicMock()
    daily_result.all.return_value = [
        SimpleNamespace(day=date(2025, 1, 1), cost=50.0, t_in=3000, t_out=1500),
        SimpleNamespace(day=date(2025, 1, 2), cost=100.5, t_in=7000, t_out=3500),
    ]

    db.execute = AsyncMock(side_effect=[totals_result, daily_result])

    summary = await usage_service.get_usage_summary(
        db, org_id, start_date=date(2025, 1, 1), end_date=date(2025, 1, 31)
    )
    assert isinstance(summary, UsageSummaryResponse)
    assert summary.total_cost_cents == 150.5
    assert summary.total_tokens_in == 10000
    assert summary.total_tokens_out == 5000
    assert summary.total_calls == 25
    assert len(summary.by_date) == 2
    assert summary.by_date[0].date == date(2025, 1, 1)


@pytest.mark.asyncio
async def test_get_usage_summary_defaults_date_range():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    totals_result = MagicMock()
    totals_result.one.return_value = SimpleNamespace(
        total_cost=0, total_in=0, total_out=0, total_calls=0
    )
    daily_result = MagicMock()
    daily_result.all.return_value = []

    db.execute = AsyncMock(side_effect=[totals_result, daily_result])

    summary = await usage_service.get_usage_summary(db, org_id)
    assert summary.total_cost_cents == 0
    assert summary.total_calls == 0
    assert summary.by_date == []


@pytest.mark.asyncio
async def test_get_usage_breakdown_by_service():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    result = MagicMock()
    result.all.return_value = [
        SimpleNamespace(name="claude", cost=120.0, t_in=8000, t_out=4000, calls=20),
        SimpleNamespace(name="whisper", cost=30.5, t_in=2000, t_out=1000, calls=5),
    ]
    db.execute = AsyncMock(return_value=result)

    breakdown = await usage_service.get_usage_breakdown(
        db, org_id, group_by="service", start_date=date(2025, 1, 1), end_date=date(2025, 1, 31)
    )
    assert isinstance(breakdown, UsageBreakdownResponse)
    assert len(breakdown.breakdown) == 2
    assert breakdown.breakdown[0].name == "claude"
    assert breakdown.breakdown[0].cost_cents == 120.0
    assert breakdown.breakdown[0].call_count == 20


@pytest.mark.asyncio
async def test_get_usage_breakdown_by_model():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    result = MagicMock()
    result.all.return_value = [
        SimpleNamespace(name="claude-haiku-4-5-20251001", cost=80.0, t_in=6000, t_out=3000, calls=15),
    ]
    db.execute = AsyncMock(return_value=result)

    breakdown = await usage_service.get_usage_breakdown(db, org_id, group_by="model")
    assert len(breakdown.breakdown) == 1
    assert breakdown.breakdown[0].name == "claude-haiku-4-5-20251001"


@pytest.mark.asyncio
async def test_get_usage_breakdown_empty():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    result = MagicMock()
    result.all.return_value = []
    db.execute = AsyncMock(return_value=result)

    breakdown = await usage_service.get_usage_breakdown(db, org_id, group_by="service")
    assert breakdown.breakdown == []


def test_daily_usage_schema():
    d = DailyUsage(date=date(2025, 1, 1), cost_cents=50.0, tokens_in=1000, tokens_out=500)
    assert d.date == date(2025, 1, 1)
    assert d.cost_cents == 50.0


def test_usage_entry_schema():
    e = UsageEntry(name="claude", cost_cents=100.0, tokens_in=5000, tokens_out=2500, call_count=10)
    assert e.name == "claude"
    assert e.call_count == 10


def test_usage_summary_response_schema():
    s = UsageSummaryResponse(
        total_cost_cents=200.0,
        total_tokens_in=15000,
        total_tokens_out=7500,
        total_calls=30,
        by_date=[],
    )
    assert s.total_calls == 30
