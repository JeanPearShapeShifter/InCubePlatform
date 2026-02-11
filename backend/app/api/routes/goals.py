import math
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.common import PaginationMeta
from app.schemas.goal import GoalCreate, GoalListResponse, GoalResponse
from app.services import goal as goal_service

router = APIRouter()


@router.post("/goals", response_model=GoalResponse, status_code=201)
async def create_goal(
    data: GoalCreate,
    # TODO: replace with get_current_user dependency
    org_id: uuid.UUID = Query(...),
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
) -> GoalResponse:
    goal = await goal_service.create_goal(db, org_id, user_id, data)
    return GoalResponse.model_validate(goal)


@router.get("/goals", response_model=GoalListResponse)
async def list_goals(
    # TODO: replace with get_current_user dependency
    org_id: uuid.UUID = Query(...),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    type: str | None = Query(None, pattern="^(predefined|custom)$"),
    db: AsyncSession = Depends(get_db),
) -> GoalListResponse:
    goals, total = await goal_service.list_goals(db, org_id, page, per_page, type)
    return GoalListResponse(
        goals=[GoalResponse.model_validate(g) for g in goals],
        pagination=PaginationMeta(
            page=page, per_page=per_page, total=total, total_pages=math.ceil(total / per_page) if total else 0
        ),
    )


@router.get("/goals/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: uuid.UUID,
    # TODO: replace with get_current_user dependency
    org_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
) -> GoalResponse:
    goal = await goal_service.get_goal(db, org_id, goal_id)
    return GoalResponse.model_validate(goal)
