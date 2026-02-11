import uuid
from datetime import date, timedelta

from sqlalchemy import cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import Date

from app.models.api_usage import ApiUsage
from app.schemas.settings import DailyUsage, UsageBreakdownResponse, UsageEntry, UsageSummaryResponse


async def get_usage_summary(
    db: AsyncSession,
    org_id: uuid.UUID,
    start_date: date | None = None,
    end_date: date | None = None,
) -> UsageSummaryResponse:
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Totals
    totals_q = select(
        func.coalesce(func.sum(ApiUsage.cost_cents), 0).label("total_cost"),
        func.coalesce(func.sum(ApiUsage.tokens_in), 0).label("total_in"),
        func.coalesce(func.sum(ApiUsage.tokens_out), 0).label("total_out"),
        func.count(ApiUsage.id).label("total_calls"),
    ).where(
        ApiUsage.organization_id == org_id,
        cast(ApiUsage.created_at, Date) >= start_date,
        cast(ApiUsage.created_at, Date) <= end_date,
    )
    totals_result = await db.execute(totals_q)
    totals = totals_result.one()

    # Daily breakdown
    daily_q = (
        select(
            cast(ApiUsage.created_at, Date).label("day"),
            func.sum(ApiUsage.cost_cents).label("cost"),
            func.sum(ApiUsage.tokens_in).label("t_in"),
            func.sum(ApiUsage.tokens_out).label("t_out"),
        )
        .where(
            ApiUsage.organization_id == org_id,
            cast(ApiUsage.created_at, Date) >= start_date,
            cast(ApiUsage.created_at, Date) <= end_date,
        )
        .group_by(cast(ApiUsage.created_at, Date))
        .order_by(cast(ApiUsage.created_at, Date))
    )
    daily_result = await db.execute(daily_q)
    daily_rows = daily_result.all()

    by_date = [
        DailyUsage(date=row.day, cost_cents=float(row.cost), tokens_in=int(row.t_in), tokens_out=int(row.t_out))
        for row in daily_rows
    ]

    return UsageSummaryResponse(
        total_cost_cents=float(totals.total_cost),
        total_tokens_in=int(totals.total_in),
        total_tokens_out=int(totals.total_out),
        total_calls=int(totals.total_calls),
        by_date=by_date,
    )


async def get_usage_breakdown(
    db: AsyncSession,
    org_id: uuid.UUID,
    group_by: str = "service",
    start_date: date | None = None,
    end_date: date | None = None,
) -> UsageBreakdownResponse:
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    if group_by == "service":
        group_col = ApiUsage.service
    elif group_by == "model":
        group_col = ApiUsage.model_name
    elif group_by == "endpoint":
        group_col = ApiUsage.endpoint
    else:
        group_col = ApiUsage.service

    q = (
        select(
            group_col.label("name"),
            func.sum(ApiUsage.cost_cents).label("cost"),
            func.sum(ApiUsage.tokens_in).label("t_in"),
            func.sum(ApiUsage.tokens_out).label("t_out"),
            func.count(ApiUsage.id).label("calls"),
        )
        .where(
            ApiUsage.organization_id == org_id,
            cast(ApiUsage.created_at, Date) >= start_date,
            cast(ApiUsage.created_at, Date) <= end_date,
        )
        .group_by(group_col)
        .order_by(func.sum(ApiUsage.cost_cents).desc())
    )
    result = await db.execute(q)
    rows = result.all()

    breakdown = [
        UsageEntry(
            name=row.name or "unknown",
            cost_cents=float(row.cost),
            tokens_in=int(row.t_in),
            tokens_out=int(row.t_out),
            call_count=int(row.calls),
        )
        for row in rows
    ]

    return UsageBreakdownResponse(breakdown=breakdown)
