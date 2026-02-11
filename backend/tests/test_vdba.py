import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.errors import NotFoundError, ValidationError
from app.models.enums import BankType
from app.schemas.vdba import VdbaCreate, VdbaListItem, VdbaResponse
from app.services import vdba as vdba_service


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


def _make_bank_instance_ns(**kwargs) -> SimpleNamespace:
    defaults = {
        "id": uuid.uuid4(),
        "perspective_id": uuid.uuid4(),
        "type": BankType.FILM_REEL.value,
        "synopsis": "Test synopsis",
        "decision_audit": [],
        "agent_assessments": {},
        "documents_count": 0,
        "vibes_count": 0,
        "emails_sent": 0,
        "feedback_received": 0,
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
        "description": "Test description",
        "bank_instance_id": uuid.uuid4(),
        "published_at": datetime.now(UTC),
        "export_url": None,
        "export_format": "pdf",
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
async def test_publish_journey_success():
    """Publish should succeed when all 12 perspectives are completed."""
    db = _make_db_mock()
    org_id = uuid.uuid4()
    journey_id = uuid.uuid4()
    journey = _make_journey_ns(id=journey_id, organization_id=org_id)
    bank_instance = _make_bank_instance_ns()

    # Mock: journey lookup, completed count, film_reel bank, version count
    journey_result = MagicMock()
    journey_result.scalar_one_or_none.return_value = journey

    count_result = MagicMock()
    count_result.scalar_one.return_value = 12

    bank_result = MagicMock()
    bank_result.scalar_one_or_none.return_value = bank_instance

    version_result = MagicMock()
    version_result.scalar_one.return_value = 0

    db.execute = AsyncMock(
        side_effect=[journey_result, count_result, bank_result, version_result]
    )

    body = VdbaCreate(title="My VDBA", description="desc", export_format="json")
    vdba = await vdba_service.publish_journey(db, journey_id, org_id, body)

    assert vdba.title == "My VDBA"
    assert vdba.description == "desc"
    assert vdba.export_format == "json"
    assert vdba.journey_id == journey_id
    assert vdba.organization_id == org_id
    assert vdba.version == 1
    db.add.assert_called_once()
    db.flush.assert_awaited_once()
    # Journey should be marked as completed
    assert journey.status == "completed"
    assert journey.completed_at is not None
    assert journey.perspectives_completed == 12


@pytest.mark.asyncio
async def test_publish_journey_not_found():
    """Publish should raise NotFoundError if journey doesn't exist."""
    db = _make_db_mock()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    body = VdbaCreate(title="VDBA")
    with pytest.raises(NotFoundError, match="Journey not found"):
        await vdba_service.publish_journey(db, uuid.uuid4(), uuid.uuid4(), body)


@pytest.mark.asyncio
async def test_publish_journey_incomplete_perspectives():
    """Publish should fail if fewer than 12 perspectives are completed."""
    db = _make_db_mock()
    org_id = uuid.uuid4()
    journey_id = uuid.uuid4()
    journey = _make_journey_ns(id=journey_id, organization_id=org_id)

    journey_result = MagicMock()
    journey_result.scalar_one_or_none.return_value = journey

    count_result = MagicMock()
    count_result.scalar_one.return_value = 8

    db.execute = AsyncMock(side_effect=[journey_result, count_result])

    body = VdbaCreate(title="VDBA")
    with pytest.raises(ValidationError, match="only 8/12"):
        await vdba_service.publish_journey(db, journey_id, org_id, body)


@pytest.mark.asyncio
async def test_publish_journey_no_bank_instances():
    """Publish should fail if no bank instances exist for the journey."""
    db = _make_db_mock()
    org_id = uuid.uuid4()
    journey_id = uuid.uuid4()
    journey = _make_journey_ns(id=journey_id, organization_id=org_id)

    journey_result = MagicMock()
    journey_result.scalar_one_or_none.return_value = journey

    count_result = MagicMock()
    count_result.scalar_one.return_value = 12

    # No film_reel found
    bank_result = MagicMock()
    bank_result.scalar_one_or_none.return_value = None

    # No fallback found either
    fallback_result = MagicMock()
    fallback_result.scalar_one_or_none.return_value = None

    db.execute = AsyncMock(
        side_effect=[journey_result, count_result, bank_result, fallback_result]
    )

    body = VdbaCreate(title="VDBA")
    with pytest.raises(ValidationError, match="No bank instances"):
        await vdba_service.publish_journey(db, journey_id, org_id, body)


@pytest.mark.asyncio
async def test_publish_journey_version_increment():
    """Second publish should have version 2."""
    db = _make_db_mock()
    org_id = uuid.uuid4()
    journey_id = uuid.uuid4()
    journey = _make_journey_ns(id=journey_id, organization_id=org_id)
    bank_instance = _make_bank_instance_ns()

    journey_result = MagicMock()
    journey_result.scalar_one_or_none.return_value = journey

    count_result = MagicMock()
    count_result.scalar_one.return_value = 12

    bank_result = MagicMock()
    bank_result.scalar_one_or_none.return_value = bank_instance

    # Existing version is 1
    version_result = MagicMock()
    version_result.scalar_one.return_value = 1

    db.execute = AsyncMock(
        side_effect=[journey_result, count_result, bank_result, version_result]
    )

    body = VdbaCreate(title="VDBA v2")
    vdba = await vdba_service.publish_journey(db, journey_id, org_id, body)
    assert vdba.version == 2


@pytest.mark.asyncio
async def test_list_vdbas():
    """List should return paginated VDBAs for the org."""
    db = _make_db_mock()
    org_id = uuid.uuid4()
    vdbas = [_make_vdba_ns(organization_id=org_id) for _ in range(3)]

    count_result = MagicMock()
    count_result.scalar_one.return_value = 3

    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = vdbas

    db.execute = AsyncMock(side_effect=[count_result, list_result])

    result, total = await vdba_service.list_vdbas(db, org_id, page=1, per_page=20)
    assert total == 3
    assert len(result) == 3


@pytest.mark.asyncio
async def test_get_vdba_found():
    """Get should return a VDBA when it exists."""
    db = _make_db_mock()
    org_id = uuid.uuid4()
    vdba_id = uuid.uuid4()
    vdba = _make_vdba_ns(id=vdba_id, organization_id=org_id)

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = vdba
    db.execute = AsyncMock(return_value=result_mock)

    found = await vdba_service.get_vdba(db, vdba_id, org_id)
    assert found.id == vdba_id


@pytest.mark.asyncio
async def test_get_vdba_not_found():
    """Get should raise NotFoundError when VDBA doesn't exist."""
    db = _make_db_mock()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(NotFoundError, match="VDBA not found"):
        await vdba_service.get_vdba(db, uuid.uuid4(), uuid.uuid4())


@pytest.mark.asyncio
async def test_vdba_create_schema_validation():
    """VdbaCreate schema should validate fields correctly."""
    data = VdbaCreate(title="Test", export_format="json")
    assert data.title == "Test"
    assert data.export_format == "json"
    assert data.description == ""

    # Valid formats
    for fmt in ("pdf", "docx", "json"):
        d = VdbaCreate(title="Test", export_format=fmt)
        assert d.export_format == fmt

    # Invalid format
    with pytest.raises(Exception):
        VdbaCreate(title="Test", export_format="xml")

    # Empty title
    with pytest.raises(Exception):
        VdbaCreate(title="")


@pytest.mark.asyncio
async def test_vdba_response_schema():
    """VdbaResponse should correctly validate from model-like attributes."""
    vdba = _make_vdba_ns()
    response = VdbaResponse.model_validate(vdba)
    assert response.id == vdba.id
    assert response.title == vdba.title
    assert response.version == vdba.version


@pytest.mark.asyncio
async def test_vdba_list_item_schema():
    """VdbaListItem should correctly validate from model-like attributes."""
    vdba = _make_vdba_ns()
    item = VdbaListItem.model_validate(vdba)
    assert item.id == vdba.id
    assert item.title == vdba.title
    assert item.journey_id == vdba.journey_id
