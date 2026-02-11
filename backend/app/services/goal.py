import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.goal import Goal
from app.schemas.goal import GoalCreate


async def create_goal(db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: GoalCreate) -> Goal:
    goal = Goal(
        organization_id=org_id,
        created_by=user_id,
        title=data.title,
        description=data.description,
        type=data.type,
    )
    db.add(goal)
    await db.flush()
    return goal


async def list_goals(
    db: AsyncSession, org_id: uuid.UUID, page: int = 1, per_page: int = 20, type_filter: str | None = None
) -> tuple[list[Goal], int]:
    base = select(Goal).where(Goal.organization_id == org_id)
    if type_filter:
        base = base.where(Goal.type == type_filter)

    total_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = total_result.scalar_one()

    offset = (page - 1) * per_page
    result = await db.execute(base.order_by(Goal.created_at.desc()).offset(offset).limit(per_page))
    goals = list(result.scalars().all())
    return goals, total


async def get_goal(db: AsyncSession, org_id: uuid.UUID, goal_id: uuid.UUID) -> Goal:
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.organization_id == org_id))
    goal = result.scalar_one_or_none()
    if not goal:
        raise NotFoundError("Goal not found")
    return goal
