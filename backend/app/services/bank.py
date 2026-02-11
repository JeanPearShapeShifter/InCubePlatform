import uuid
from typing import Any

from sqlalchemy import func, select
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
    db: AsyncSession,
    perspective_id: uuid.UUID,
    synopsis: str,
    agent_assessments: dict[str, Any] | None = None,
    decision_audit: list[dict] | None = None,
) -> BankInstance:
    """Create a bank instance for a completed perspective.

    Optionally accepts agent_assessments and decision_audit from the boomerang flow.
    """
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
        agent_assessments=agent_assessments or {},
        decision_audit=decision_audit or [],
    )
    db.add(bank)
    await db.flush()
    return bank


async def populate_bank_stats(db: AsyncSession, bank_id: uuid.UUID) -> BankInstance:
    """Populate document/vibe/email counts for a bank instance from its perspective's data."""
    result = await db.execute(select(BankInstance).where(BankInstance.id == bank_id))
    bank = result.scalar_one_or_none()
    if not bank:
        raise NotFoundError("Bank instance not found")

    # Count documents for this perspective
    from app.models.document import Document

    doc_count_result = await db.execute(
        select(func.count()).select_from(Document).where(Document.perspective_id == bank.perspective_id)
    )
    bank.documents_count = doc_count_result.scalar() or 0

    # Count vibes for this perspective
    from app.models.vibe_session import VibeSession

    vibe_count_result = await db.execute(
        select(func.count()).select_from(VibeSession).where(VibeSession.perspective_id == bank.perspective_id)
    )
    bank.vibes_count = vibe_count_result.scalar() or 0

    await db.flush()
    return bank


async def create_published_vdba(
    db: AsyncSession,
    journey_id: uuid.UUID,
    title: str,
    description: str,
) -> BankInstance:
    """Create a published VDBA bank instance for a journey.

    Requires at least one completed perspective in the journey. Uses the first
    completed perspective as the anchor.
    """
    result = await db.execute(
        select(Perspective)
        .where(Perspective.journey_id == journey_id, Perspective.status == PerspectiveStatus.COMPLETED.value)
        .order_by(Perspective.completed_at.desc())
        .limit(1)
    )
    perspective = result.scalar_one_or_none()
    if not perspective:
        raise ValidationError("Journey must have at least one completed perspective to publish a VDBA")

    bank = BankInstance(
        perspective_id=perspective.id,
        type=BankType.PUBLISHED.value,
        synopsis=f"{title}\n\n{description}",
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
