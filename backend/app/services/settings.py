import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ValidationError
from app.models.setting import Setting
from app.schemas.settings import (
    ALLOWED_SETTINGS,
    VALID_EXPORT_FORMATS,
    VALID_MODELS,
    VALID_THEMES,
    VALID_VOICE_PROVIDERS,
    SettingsResponse,
)


def _validate_setting_value(key: str, value: Any) -> None:
    if key not in ALLOWED_SETTINGS:
        raise ValidationError(f"Unknown setting key: {key}")

    expected_type = ALLOWED_SETTINGS[key]
    if expected_type is int and not isinstance(value, int):
        raise ValidationError(f"Setting '{key}' must be an integer")
    if expected_type is str and not isinstance(value, str):
        raise ValidationError(f"Setting '{key}' must be a string")
    if expected_type is list and not isinstance(value, list):
        raise ValidationError(f"Setting '{key}' must be a list")

    if key == "default_model" and value not in VALID_MODELS:
        raise ValidationError(f"Invalid model. Must be one of: {', '.join(VALID_MODELS)}")
    if key == "theme" and value not in VALID_THEMES:
        raise ValidationError(f"Invalid theme. Must be one of: {', '.join(VALID_THEMES)}")
    if key == "export_format" and value not in VALID_EXPORT_FORMATS:
        raise ValidationError(f"Invalid export format. Must be one of: {', '.join(VALID_EXPORT_FORMATS)}")
    if key == "voice_provider" and value not in VALID_VOICE_PROVIDERS:
        raise ValidationError(f"Invalid voice provider. Must be one of: {', '.join(VALID_VOICE_PROVIDERS)}")
    if key == "monthly_budget_cents" and value < 0:
        raise ValidationError("Budget must be non-negative")
    if key == "budget_alert_thresholds":
        if not all(isinstance(t, int) and 0 <= t <= 100 for t in value):
            raise ValidationError("Alert thresholds must be integers between 0 and 100")


async def get_settings(db: AsyncSession, org_id: uuid.UUID) -> SettingsResponse:
    result = await db.execute(select(Setting).where(Setting.organization_id == org_id))
    rows = result.scalars().all()

    defaults = SettingsResponse()
    settings_dict = defaults.model_dump()

    for row in rows:
        if row.key in settings_dict and "value" in row.value:
            settings_dict[row.key] = row.value["value"]

    return SettingsResponse(**settings_dict)


async def update_setting(db: AsyncSession, org_id: uuid.UUID, key: str, value: Any) -> Setting:
    _validate_setting_value(key, value)

    result = await db.execute(
        select(Setting).where(Setting.organization_id == org_id, Setting.key == key)
    )
    setting = result.scalar_one_or_none()

    if setting:
        setting.value = {"value": value}
    else:
        setting = Setting(organization_id=org_id, key=key, value={"value": value})
        db.add(setting)

    await db.flush()
    return setting
