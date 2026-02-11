import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.bank import BankCreate, BankInstanceDetail, BankInstanceResponse, BankTimelineResponse
from app.services import bank as bank_service

router = APIRouter()


@router.post("/perspectives/{perspective_id}/bank", response_model=BankInstanceResponse, status_code=201)
async def create_bank_instance(
    perspective_id: uuid.UUID,
    data: BankCreate,
    db: AsyncSession = Depends(get_db),
) -> BankInstanceResponse:
    # Convert typed schemas to dicts for JSONB storage
    agent_assessments = (
        {k: v.model_dump() for k, v in data.agent_assessments.items()} if data.agent_assessments else None
    )
    decision_audit = [entry.model_dump() for entry in data.decision_audit] if data.decision_audit else None

    bank = await bank_service.create_bank_instance(
        db,
        perspective_id,
        data.synopsis,
        agent_assessments=agent_assessments,
        decision_audit=decision_audit,
    )
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


@router.get("/bank/{bank_id}/detail", response_model=BankInstanceDetail)
async def get_bank_instance_detail(
    bank_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BankInstanceDetail:
    bank = await bank_service.get_bank_instance(db, bank_id)
    return BankInstanceDetail.model_validate(bank)
