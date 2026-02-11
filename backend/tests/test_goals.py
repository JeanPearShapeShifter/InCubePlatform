import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.errors import NotFoundError
from app.schemas.goal import GoalCreate
from app.services import goal as goal_service


def _make_goal(**kwargs) -> SimpleNamespace:
    """Create a Goal-like object with sensible defaults for testing."""
    defaults = {
        "id": uuid.uuid4(),
        "organization_id": uuid.uuid4(),
        "created_by": uuid.uuid4(),
        "title": "Test Goal",
        "description": "A test goal",
        "type": "custom",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_db_mock() -> MagicMock:
    """Create a mock db session where add() is sync and flush()/execute() are async."""
    db = MagicMock()
    db.add = MagicMock()  # sync
    db.flush = AsyncMock()
    db.execute = AsyncMock()
    db.delete = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_create_goal_service():
    db = _make_db_mock()
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    data = GoalCreate(title="My Goal", description="desc", type="custom")

    goal = await goal_service.create_goal(db, org_id, user_id, data)
    assert goal.title == "My Goal"
    assert goal.description == "desc"
    assert goal.type == "custom"
    assert goal.organization_id == org_id
    assert goal.created_by == user_id
    db.add.assert_called_once()
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_goals_service():
    db = _make_db_mock()
    org_id = uuid.uuid4()
    goals = [_make_goal(organization_id=org_id) for _ in range(3)]

    count_result = MagicMock()
    count_result.scalar_one.return_value = 3

    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = goals

    db.execute = AsyncMock(side_effect=[count_result, list_result])

    result_goals, total = await goal_service.list_goals(db, org_id, page=1, per_page=20)
    assert total == 3
    assert len(result_goals) == 3


@pytest.mark.asyncio
async def test_get_goal_service_found():
    db = _make_db_mock()
    org_id = uuid.uuid4()
    goal_id = uuid.uuid4()
    goal = _make_goal(id=goal_id, organization_id=org_id)

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = goal
    db.execute = AsyncMock(return_value=result_mock)

    found = await goal_service.get_goal(db, org_id, goal_id)
    assert found.id == goal_id


@pytest.mark.asyncio
async def test_get_goal_service_not_found():
    db = _make_db_mock()
    org_id = uuid.uuid4()
    goal_id = uuid.uuid4()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(NotFoundError):
        await goal_service.get_goal(db, org_id, goal_id)


@pytest.mark.asyncio
async def test_goal_create_schema_validation():
    data = GoalCreate(title="Test", type="custom")
    assert data.title == "Test"
    assert data.type == "custom"
    assert data.description == ""

    with pytest.raises(Exception):
        GoalCreate(title="Test", type="invalid")

    with pytest.raises(Exception):
        GoalCreate(title="", type="custom")


@pytest.mark.asyncio
async def test_goal_create_predefined_type():
    data = GoalCreate(title="Predefined Goal", type="predefined")
    assert data.type == "predefined"
