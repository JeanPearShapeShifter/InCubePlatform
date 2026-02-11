import math
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.bank import BankInstanceResponse
from app.schemas.common import PaginationMeta
from app.schemas.journey import (
    JourneyCreate,
    JourneyDetailResponse,
    JourneyListResponse,
    JourneyResponse,
    JourneyStatusUpdate,
)
from app.schemas.perspective import PerspectiveResponse
from app.services import journey as journey_service

router = APIRouter()


@router.post("/journeys", response_model=JourneyResponse, status_code=201)
async def create_journey(
    data: JourneyCreate,
    # TODO: replace with get_current_user dependency
    org_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
) -> JourneyResponse:
    journey = await journey_service.create_journey(db, org_id, data.goal_id)
    return JourneyResponse.model_validate(journey)


@router.get("/journeys", response_model=JourneyListResponse)
async def list_journeys(
    # TODO: replace with get_current_user dependency
    org_id: uuid.UUID = Query(...),
    status: str | None = Query(None, pattern="^(active|completed|archived)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> JourneyListResponse:
    journeys, total = await journey_service.list_journeys(db, org_id, status, page, per_page)
    return JourneyListResponse(
        journeys=[JourneyResponse.model_validate(j) for j in journeys],
        pagination=PaginationMeta(
            page=page, per_page=per_page, total=total, total_pages=math.ceil(total / per_page) if total else 0
        ),
    )


@router.get("/journeys/{journey_id}", response_model=JourneyDetailResponse)
async def get_journey(
    journey_id: uuid.UUID,
    # TODO: replace with get_current_user dependency
    org_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
) -> JourneyDetailResponse:
    data = await journey_service.get_journey(db, org_id, journey_id)
    journey = data["journey"]
    return JourneyDetailResponse(
        id=journey.id,
        goal_id=journey.goal_id,
        organization_id=journey.organization_id,
        status=journey.status,
        perspectives_completed=journey.perspectives_completed,
        total_cost_cents=journey.total_cost_cents,
        created_at=journey.created_at,
        completed_at=journey.completed_at,
        perspectives=[PerspectiveResponse.model_validate(p) for p in data["perspectives"]],
        bank_instances=[BankInstanceResponse.model_validate(b) for b in data["bank_instances"]],
    )


@router.patch("/journeys/{journey_id}/status", response_model=JourneyResponse)
async def update_journey_status(
    journey_id: uuid.UUID,
    data: JourneyStatusUpdate,
    # TODO: replace with get_current_user dependency
    org_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
) -> JourneyResponse:
    journey = await journey_service.update_journey_status(db, org_id, journey_id, data.status)
    return JourneyResponse.model_validate(journey)
