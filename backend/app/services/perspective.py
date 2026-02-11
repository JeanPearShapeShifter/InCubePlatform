import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.models.enums import PerspectiveStatus, PhaseType
from app.models.perspective import Perspective

# Phase ordering for unlocking logic
PHASE_ORDER = [PhaseType.GENERATE, PhaseType.REVIEW, PhaseType.VALIDATE, PhaseType.SUMMARIZE]


async def list_perspectives(db: AsyncSession, journey_id: uuid.UUID) -> list[Perspective]:
    result = await db.execute(
        select(Perspective)
        .where(Perspective.journey_id == journey_id)
        .order_by(Perspective.dimension, Perspective.phase)
    )
    return list(result.scalars().all())


async def get_perspective(db: AsyncSession, perspective_id: uuid.UUID) -> Perspective:
    result = await db.execute(select(Perspective).where(Perspective.id == perspective_id))
    perspective = result.scalar_one_or_none()
    if not perspective:
        raise NotFoundError("Perspective not found")
    return perspective


async def update_perspective_status(
    db: AsyncSession, perspective_id: uuid.UUID, new_status: str
) -> Perspective:
    result = await db.execute(select(Perspective).where(Perspective.id == perspective_id))
    perspective = result.scalar_one_or_none()
    if not perspective:
        raise NotFoundError("Perspective not found")

    current = perspective.status

    if new_status == "in_progress":
        if current != PerspectiveStatus.PENDING.value:
            raise ValidationError(f"Cannot move to in_progress from {current} (must be pending)")
        perspective.status = PerspectiveStatus.IN_PROGRESS.value
        perspective.started_at = datetime.now(UTC)
    elif new_status == "completed":
        if current != PerspectiveStatus.IN_PROGRESS.value:
            raise ValidationError(f"Cannot move to completed from {current} (must be in_progress)")
        perspective.status = PerspectiveStatus.COMPLETED.value
        perspective.completed_at = datetime.now(UTC)

        # Unlock next phase in same dimension if all prior phases are complete
        await _try_unlock_next_phase(db, perspective)
    else:
        raise ValidationError(f"Invalid status: {new_status}")

    await db.flush()
    return perspective


async def _try_unlock_next_phase(db: AsyncSession, completed_perspective: Perspective) -> None:
    """When completing a perspective, unlock the next phase in the same dimension if ready."""
    dimension = completed_perspective.dimension
    journey_id = completed_perspective.journey_id
    current_phase = completed_perspective.phase

    # Find the index of the current phase
    try:
        current_idx = next(i for i, p in enumerate(PHASE_ORDER) if p.value == current_phase)
    except StopIteration:
        return

    # If this is the last phase, nothing to unlock
    if current_idx >= len(PHASE_ORDER) - 1:
        return

    next_phase = PHASE_ORDER[current_idx + 1]

    # Check this specific dimension's current phase is complete
    dim_result = await db.execute(
        select(Perspective).where(
            Perspective.journey_id == journey_id,
            Perspective.dimension == dimension,
            Perspective.phase == current_phase,
            Perspective.status == PerspectiveStatus.COMPLETED.value,
        )
    )
    if not dim_result.scalar_one_or_none():
        return

    # Unlock the next phase for this dimension
    next_result = await db.execute(
        select(Perspective).where(
            Perspective.journey_id == journey_id,
            Perspective.dimension == dimension,
            Perspective.phase == next_phase.value,
            Perspective.status == PerspectiveStatus.LOCKED.value,
        )
    )
    next_perspective = next_result.scalar_one_or_none()
    if next_perspective:
        next_perspective.status = PerspectiveStatus.PENDING.value
