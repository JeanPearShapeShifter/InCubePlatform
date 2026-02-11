import math
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.common import PaginationMeta
from app.schemas.goal import GoalCreate, GoalListResponse, GoalResponse
from app.services import goal as goal_service

router = APIRouter()


@router.post("/goals", response_model=GoalResponse, status_code=201)
async def create_goal(
    data: GoalCreate,
    current_user: User = Depends(require_role("editor")),
    db: AsyncSession = Depends(get_db),
) -> GoalResponse:
    goal = await goal_service.create_goal(db, current_user.organization_id, current_user.id, data)
    return GoalResponse.model_validate(goal)


@router.get("/goals", response_model=GoalListResponse)
async def list_goals(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    type: str | None = Query(None, pattern="^(predefined|custom)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GoalListResponse:
    goals, total = await goal_service.list_goals(db, current_user.organization_id, page, per_page, type)
    return GoalListResponse(
        goals=[GoalResponse.model_validate(g) for g in goals],
        pagination=PaginationMeta(
            page=page, per_page=per_page, total=total, total_pages=math.ceil(total / per_page) if total else 0
        ),
    )


@router.get("/goals/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GoalResponse:
    goal = await goal_service.get_goal(db, current_user.organization_id, goal_id)
    return GoalResponse.model_validate(goal)
