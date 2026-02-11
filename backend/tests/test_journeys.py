import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.errors import NotFoundError, ValidationError
from app.models.enums import DimensionType, PerspectiveStatus, PhaseType
from app.models.perspective import Perspective
from app.services import journey as journey_service
from app.services import perspective as perspective_service


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


def _make_perspective_ns(**kwargs) -> SimpleNamespace:
    defaults = {
        "id": uuid.uuid4(),
        "journey_id": uuid.uuid4(),
        "dimension": DimensionType.ARCHITECTURE.value,
        "phase": PhaseType.GENERATE.value,
        "status": PerspectiveStatus.PENDING.value,
        "started_at": None,
        "completed_at": None,
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
async def test_create_journey_creates_12_perspectives():
    """Journey creation should add 12 perspective objects to the session."""
    db = _make_db_mock()
    org_id = uuid.uuid4()
    goal_id = uuid.uuid4()

    journey = await journey_service.create_journey(db, org_id, goal_id)
    assert journey.goal_id == goal_id
    assert journey.organization_id == org_id

    # 1 journey + 12 perspectives = 13 add calls
    assert db.add.call_count == 13
    assert db.flush.await_count == 2


@pytest.mark.asyncio
async def test_create_journey_perspective_statuses():
    """Generate phase perspectives should be pending, others locked."""
    db = _make_db_mock()
    added_objects = []
    db.add.side_effect = lambda obj: added_objects.append(obj)

    await journey_service.create_journey(db, uuid.uuid4(), uuid.uuid4())

    perspectives = [obj for obj in added_objects if isinstance(obj, Perspective)]
    assert len(perspectives) == 12

    for p in perspectives:
        if p.phase == PhaseType.GENERATE.value:
            assert p.status == PerspectiveStatus.PENDING.value
        else:
            assert p.status == PerspectiveStatus.LOCKED.value


@pytest.mark.asyncio
async def test_create_journey_covers_all_dimensions_and_phases():
    """Journey must create perspectives for all 3 dimensions x 4 phases."""
    db = _make_db_mock()
    added_objects = []
    db.add.side_effect = lambda obj: added_objects.append(obj)

    await journey_service.create_journey(db, uuid.uuid4(), uuid.uuid4())

    perspectives = [obj for obj in added_objects if isinstance(obj, Perspective)]
    combos = {(p.dimension, p.phase) for p in perspectives}
    expected = {(d.value, p.value) for d in DimensionType for p in PhaseType}
    assert combos == expected


@pytest.mark.asyncio
async def test_get_journey_not_found():
    db = _make_db_mock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(NotFoundError):
        await journey_service.get_journey(db, uuid.uuid4(), uuid.uuid4())


@pytest.mark.asyncio
async def test_update_journey_status_archived():
    db = _make_db_mock()
    org_id = uuid.uuid4()
    journey_id = uuid.uuid4()
    journey = _make_journey_ns(id=journey_id, organization_id=org_id)

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = journey
    db.execute = AsyncMock(return_value=result_mock)

    updated = await journey_service.update_journey_status(db, org_id, journey_id, "archived")
    assert updated.status == "archived"


@pytest.mark.asyncio
async def test_update_journey_status_completed_fails_without_perspectives():
    db = _make_db_mock()
    org_id = uuid.uuid4()
    journey_id = uuid.uuid4()
    journey = _make_journey_ns(id=journey_id, organization_id=org_id)

    journey_result = MagicMock()
    journey_result.scalar_one_or_none.return_value = journey
    count_result = MagicMock()
    count_result.scalar_one.return_value = 5

    db.execute = AsyncMock(side_effect=[journey_result, count_result])

    with pytest.raises(ValidationError, match="only 5/12"):
        await journey_service.update_journey_status(db, org_id, journey_id, "completed")


@pytest.mark.asyncio
async def test_perspective_status_to_in_progress():
    db = _make_db_mock()
    perspective = _make_perspective_ns(status=PerspectiveStatus.PENDING.value)

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = perspective
    db.execute = AsyncMock(return_value=result_mock)

    updated = await perspective_service.update_perspective_status(db, perspective.id, "in_progress")
    assert updated.status == PerspectiveStatus.IN_PROGRESS.value
    assert updated.started_at is not None


@pytest.mark.asyncio
async def test_perspective_status_invalid_transition():
    db = _make_db_mock()
    perspective = _make_perspective_ns(status=PerspectiveStatus.LOCKED.value)

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = perspective
    db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(ValidationError, match="must be pending"):
        await perspective_service.update_perspective_status(db, perspective.id, "in_progress")


@pytest.mark.asyncio
async def test_perspective_status_completed_from_pending_fails():
    db = _make_db_mock()
    perspective = _make_perspective_ns(status=PerspectiveStatus.PENDING.value)

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = perspective
    db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(ValidationError, match="must be in_progress"):
        await perspective_service.update_perspective_status(db, perspective.id, "completed")


@pytest.mark.asyncio
async def test_bank_type_determination():
    from app.services.bank import _determine_bank_type

    assert _determine_bank_type("architecture", "generate") == "bankable"
    assert _determine_bank_type("design", "review") == "bankable"
    assert _determine_bank_type("engineering", "validate") == "bankable"

    assert _determine_bank_type("architecture", "summarize") == "film"
    assert _determine_bank_type("design", "summarize") == "film"

    assert _determine_bank_type("engineering", "summarize") == "film_reel"
