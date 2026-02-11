import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.bank import BankCreate, BankInstanceResponse, BankTimelineResponse
from app.services import bank as bank_service

router = APIRouter()


@router.post("/perspectives/{perspective_id}/bank", response_model=BankInstanceResponse, status_code=201)
async def create_bank_instance(
    perspective_id: uuid.UUID,
    data: BankCreate,
    db: AsyncSession = Depends(get_db),
) -> BankInstanceResponse:
    bank = await bank_service.create_bank_instance(db, perspective_id, data.synopsis)
    return BankInstanceResponse.model_validate(bank)


@router.get("/journeys/{journey_id}/bank", response_model=BankTimelineResponse)
async def get_bank_timeline(
    journey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BankTimelineResponse:
    instances = await bank_service.get_bank_timeline(db, journey_id)
    return BankTimelineResponse(bank_instances=[BankInstanceResponse.model_validate(b) for b in instances])


@router.get("/bank/{bank_id}", response_model=BankInstanceResponse)
async def get_bank_instance(
    bank_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BankInstanceResponse:
    bank = await bank_service.get_bank_instance(db, bank_id)
    return BankInstanceResponse.model_validate(bank)
