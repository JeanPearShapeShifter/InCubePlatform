from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.common import ResponseEnvelope
from app.schemas.settings import (
    SettingsResponse,
    SettingUpdate,
    UsageBreakdownResponse,
    UsageSummaryResponse,
)
from app.services import settings as settings_service
from app.services import usage as usage_service

router = APIRouter(prefix="/settings")


@router.get("", response_model=ResponseEnvelope[SettingsResponse])
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = await settings_service.get_settings(db, current_user.organization_id)
    return ResponseEnvelope(data=data)


@router.put("", response_model=ResponseEnvelope[SettingsResponse])
async def update_setting(
    body: SettingUpdate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    await settings_service.update_setting(db, current_user.organization_id, body.key, body.value)
    data = await settings_service.get_settings(db, current_user.organization_id)
    return ResponseEnvelope(data=data)


@router.get("/usage", response_model=ResponseEnvelope[UsageSummaryResponse])
async def get_usage_summary(
    start: date | None = Query(None),
    end: date | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = await usage_service.get_usage_summary(db, current_user.organization_id, start, end)
    return ResponseEnvelope(data=data)


@router.get("/usage/breakdown", response_model=ResponseEnvelope[UsageBreakdownResponse])
async def get_usage_breakdown(
    group_by: str = Query("service", pattern="^(service|model|endpoint)$"),
    start: date | None = Query(None),
    end: date | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = await usage_service.get_usage_breakdown(db, current_user.organization_id, group_by, start, end)
    return ResponseEnvelope(data=data)
