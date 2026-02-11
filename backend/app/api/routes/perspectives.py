import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.perspective import PerspectiveResponse, PerspectiveStatusUpdate
from app.services import perspective as perspective_service

router = APIRouter()


@router.get("/journeys/{journey_id}/perspectives", response_model=list[PerspectiveResponse])
async def list_perspectives(
    journey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[PerspectiveResponse]:
    perspectives = await perspective_service.list_perspectives(db, journey_id)
    return [PerspectiveResponse.model_validate(p) for p in perspectives]


@router.get("/perspectives/{perspective_id}", response_model=PerspectiveResponse)
async def get_perspective(
    perspective_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PerspectiveResponse:
    perspective = await perspective_service.get_perspective(db, perspective_id)
    return PerspectiveResponse.model_validate(perspective)


@router.patch("/perspectives/{perspective_id}/status", response_model=PerspectiveResponse)
async def update_perspective_status(
    perspective_id: uuid.UUID,
    data: PerspectiveStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> PerspectiveResponse:
    perspective = await perspective_service.update_perspective_status(db, perspective_id, data.status)
    return PerspectiveResponse.model_validate(perspective)
