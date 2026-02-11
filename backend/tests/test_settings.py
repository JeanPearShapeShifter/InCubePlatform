import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.errors import ValidationError
from app.schemas.settings import (
    ALLOWED_SETTINGS,
    SettingsResponse,
    SettingUpdate,
)
from app.services import settings as settings_service


def _make_setting(key: str, value: dict, **kwargs) -> SimpleNamespace:
    defaults = {
        "id": uuid.uuid4(),
        "organization_id": uuid.uuid4(),
        "key": key,
        "value": value,
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
    return db


@pytest.mark.asyncio
async def test_get_settings_returns_defaults():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result_mock)

    settings = await settings_service.get_settings(db, org_id)
    assert isinstance(settings, SettingsResponse)
    assert settings.default_model == "claude-haiku-4-5-20251001"
    assert settings.theme == "space"
    assert settings.export_format == "pdf"
    assert settings.voice_provider == "whisper"
    assert settings.monthly_budget_cents == 0


@pytest.mark.asyncio
async def test_get_settings_with_overrides():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    rows = [
        _make_setting("theme", {"value": "forest"}, organization_id=org_id),
        _make_setting("default_model", {"value": "claude-sonnet-4-5-20250929"}, organization_id=org_id),
    ]
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = rows
    db.execute = AsyncMock(return_value=result_mock)

    settings = await settings_service.get_settings(db, org_id)
    assert settings.theme == "forest"
    assert settings.default_model == "claude-sonnet-4-5-20250929"
    assert settings.export_format == "pdf"  # still default


@pytest.mark.asyncio
async def test_update_setting_creates_new():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    setting = await settings_service.update_setting(db, org_id, "theme", "forest")
    assert setting.key == "theme"
    assert setting.value == {"value": "forest"}
    db.add.assert_called_once()
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_setting_updates_existing():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    existing = _make_setting("theme", {"value": "space"}, organization_id=org_id)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = existing
    db.execute = AsyncMock(return_value=result_mock)

    setting = await settings_service.update_setting(db, org_id, "theme", "blackhole")
    assert setting.value == {"value": "blackhole"}
    db.add.assert_not_called()
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_setting_rejects_unknown_key():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    with pytest.raises(ValidationError, match="Unknown setting key"):
        await settings_service.update_setting(db, org_id, "unknown_key", "value")


@pytest.mark.asyncio
async def test_update_setting_validates_model():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    with pytest.raises(ValidationError, match="Invalid model"):
        await settings_service.update_setting(db, org_id, "default_model", "gpt-4")


@pytest.mark.asyncio
async def test_update_setting_validates_theme():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    with pytest.raises(ValidationError, match="Invalid theme"):
        await settings_service.update_setting(db, org_id, "theme", "ocean")


@pytest.mark.asyncio
async def test_update_setting_validates_export_format():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    with pytest.raises(ValidationError, match="Invalid export format"):
        await settings_service.update_setting(db, org_id, "export_format", "xlsx")


@pytest.mark.asyncio
async def test_update_setting_validates_voice_provider():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    with pytest.raises(ValidationError, match="Invalid voice provider"):
        await settings_service.update_setting(db, org_id, "voice_provider", "google")


@pytest.mark.asyncio
async def test_update_setting_validates_budget_negative():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    with pytest.raises(ValidationError, match="non-negative"):
        await settings_service.update_setting(db, org_id, "monthly_budget_cents", -100)


@pytest.mark.asyncio
async def test_update_setting_validates_thresholds():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    with pytest.raises(ValidationError, match="thresholds"):
        await settings_service.update_setting(db, org_id, "budget_alert_thresholds", [50, 150])


@pytest.mark.asyncio
async def test_update_setting_validates_type_mismatch():
    db = _make_db_mock()
    org_id = uuid.uuid4()

    with pytest.raises(ValidationError, match="must be a string"):
        await settings_service.update_setting(db, org_id, "theme", 123)


def test_setting_update_schema():
    data = SettingUpdate(key="theme", value="forest")
    assert data.key == "theme"
    assert data.value == "forest"


def test_settings_response_defaults():
    resp = SettingsResponse()
    assert resp.default_model == "claude-haiku-4-5-20251001"
    assert resp.budget_alert_thresholds == [50, 80, 100]


def test_allowed_settings_keys():
    assert "default_model" in ALLOWED_SETTINGS
    assert "voice_provider" in ALLOWED_SETTINGS
    assert "theme" in ALLOWED_SETTINGS
    assert "export_format" in ALLOWED_SETTINGS
    assert "monthly_budget_cents" in ALLOWED_SETTINGS
    assert "budget_alert_thresholds" in ALLOWED_SETTINGS
