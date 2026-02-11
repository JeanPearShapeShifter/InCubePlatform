import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.models.bank_instance import BankInstance
from app.models.enums import BankType, DimensionType, PerspectiveStatus, PhaseType
from app.models.perspective import Perspective


def _determine_bank_type(dimension: str, phase: str) -> str:
    """Auto-determine bank type from dimension and phase."""
    if phase != PhaseType.SUMMARIZE.value:
        return BankType.BANKABLE.value
    if dimension in (DimensionType.ARCHITECTURE.value, DimensionType.DESIGN.value):
        return BankType.FILM.value
    # Engineering Summarize
    return BankType.FILM_REEL.value


async def create_bank_instance(
    db: AsyncSession, perspective_id: uuid.UUID, synopsis: str
) -> BankInstance:
    # Get perspective and validate it's completed
    result = await db.execute(select(Perspective).where(Perspective.id == perspective_id))
    perspective = result.scalar_one_or_none()
    if not perspective:
        raise NotFoundError("Perspective not found")
    if perspective.status != PerspectiveStatus.COMPLETED.value:
        raise ValidationError("Perspective must be completed before banking")

    bank_type = _determine_bank_type(perspective.dimension, perspective.phase)
    bank = BankInstance(
        perspective_id=perspective_id,
        type=bank_type,
        synopsis=synopsis,
    )
    db.add(bank)
    await db.flush()
    return bank


async def get_bank_timeline(db: AsyncSession, journey_id: uuid.UUID) -> list[BankInstance]:
    result = await db.execute(
        select(BankInstance)
        .join(Perspective, BankInstance.perspective_id == Perspective.id)
        .where(Perspective.journey_id == journey_id)
        .order_by(BankInstance.created_at)
    )
    return list(result.scalars().all())


async def get_bank_instance(db: AsyncSession, bank_id: uuid.UUID) -> BankInstance:
    result = await db.execute(select(BankInstance).where(BankInstance.id == bank_id))
    bank = result.scalar_one_or_none()
    if not bank:
        raise NotFoundError("Bank instance not found")
    return bank
