"""Edge-case tests: VDBA publish validation, notification CRUD, export fallback."""

import json
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.export import _generate_docx, _generate_json, _generate_pdf

# ── VDBA publish with incomplete journey ────────────────────────────────


@pytest.mark.asyncio
async def test_vdba_publish_incomplete_journey():
    """Publishing a VDBA should fail if fewer than 12 perspectives are completed."""
    from app.core.errors import ValidationError
    from app.schemas.vdba import VdbaCreate
    from app.services.vdba import publish_journey

    db = AsyncMock()

    # Mock: journey found
    journey_mock = MagicMock()
    journey_mock.id = uuid.uuid4()
    journey_result = MagicMock()
    journey_result.scalar_one_or_none.return_value = journey_mock

    # Mock: only 5 perspectives completed (not 12)
    count_result = MagicMock()
    count_result.scalar_one.return_value = 5

    db.execute = AsyncMock(side_effect=[journey_result, count_result])

    body = VdbaCreate(title="Test VDBA", description="desc", export_format="json")
    fake_org_id = uuid.uuid4()

    with pytest.raises(ValidationError, match="only 5/12 perspectives completed"):
        await publish_journey(db, journey_mock.id, fake_org_id, body)


# ── Notification creation and read marking ──────────────────────────────


@pytest.mark.asyncio
async def test_notification_create():
    """create_notification should add a notification to the session."""
    from app.services.notification import create_notification

    db = AsyncMock()

    notif = await create_notification(
        db, user_id=uuid.uuid4(), org_id=uuid.uuid4(), title="Test", body="Hello"
    )

    db.add.assert_called_once()
    db.flush.assert_called_once()
    assert notif.title == "Test"
    assert notif.body == "Hello"
    assert notif.read_at is None


@pytest.mark.asyncio
async def test_notification_mark_read():
    """mark_read should set read_at on the notification."""
    from app.services.notification import mark_read

    mock_notif = MagicMock()
    mock_notif.read_at = None

    result = MagicMock()
    result.scalar_one_or_none.return_value = mock_notif

    db = AsyncMock()
    db.execute = AsyncMock(return_value=result)

    notif_id = uuid.uuid4()
    user_id = uuid.uuid4()
    await mark_read(db, notification_id=notif_id, user_id=user_id)

    assert mock_notif.read_at is not None
    assert isinstance(mock_notif.read_at, datetime)


@pytest.mark.asyncio
async def test_notification_mark_read_not_found():
    """mark_read should raise NotFoundError for missing notification."""
    from app.core.errors import NotFoundError
    from app.services.notification import mark_read

    result = MagicMock()
    result.scalar_one_or_none.return_value = None

    db = AsyncMock()
    db.execute = AsyncMock(return_value=result)

    with pytest.raises(NotFoundError, match="Notification not found"):
        await mark_read(db, notification_id=uuid.uuid4(), user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_notification_unread_count():
    """get_unread_count should return count of unread notifications."""
    from app.services.notification import get_unread_count

    result = MagicMock()
    result.scalar_one.return_value = 7

    db = AsyncMock()
    db.execute = AsyncMock(return_value=result)

    count = await get_unread_count(db, user_id=uuid.uuid4())
    assert count == 7


# ── Export format fallback ──────────────────────────────────────────────

SAMPLE_EXPORT_DATA = {
    "vdba": {
        "id": "abc123",
        "title": "Test VDBA",
        "description": "A test",
        "published_at": "2026-01-01T00:00:00",
        "export_format": "json",
        "version": 1,
    },
    "perspectives": [],
    "bank_instances": [],
}


def test_json_export_produces_valid_json():
    file_bytes, content_type, extension = _generate_json(SAMPLE_EXPORT_DATA)
    assert content_type == "application/json"
    assert extension == "json"
    parsed = json.loads(file_bytes.decode("utf-8"))
    assert parsed["vdba"]["title"] == "Test VDBA"


def test_pdf_fallback_when_reportlab_missing():
    """When reportlab is not importable, _generate_pdf should fall back to JSON."""
    with patch.dict("sys.modules", {"reportlab": None, "reportlab.lib.pagesizes": None,
                                     "reportlab.lib.styles": None, "reportlab.platypus": None}):
        file_bytes, content_type, extension = _generate_pdf(SAMPLE_EXPORT_DATA)
        # Should fall back to JSON
        assert extension == "json"
        assert content_type == "application/json"
        parsed = json.loads(file_bytes.decode("utf-8"))
        assert parsed["vdba"]["title"] == "Test VDBA"


def test_docx_fallback_when_python_docx_missing():
    """When python-docx is not importable, _generate_docx should fall back to JSON."""
    with patch.dict("sys.modules", {"docx": None}):
        file_bytes, content_type, extension = _generate_docx(SAMPLE_EXPORT_DATA)
        # Should fall back to JSON
        assert extension == "json"
        assert content_type == "application/json"
        parsed = json.loads(file_bytes.decode("utf-8"))
        assert parsed["vdba"]["title"] == "Test VDBA"
