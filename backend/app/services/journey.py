import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.models.bank_instance import BankInstance
from app.models.enums import DimensionType, PerspectiveStatus, PhaseType
from app.models.journey import Journey
from app.models.perspective import Perspective


async def create_journey(db: AsyncSession, org_id: uuid.UUID, goal_id: uuid.UUID) -> Journey:
    journey = Journey(goal_id=goal_id, organization_id=org_id)
    db.add(journey)
    await db.flush()

    # Auto-create 12 perspectives: 3 dimensions x 4 phases
    for dimension in DimensionType:
        for phase in PhaseType:
            status = PerspectiveStatus.PENDING if phase == PhaseType.GENERATE else PerspectiveStatus.LOCKED
            perspective = Perspective(
                journey_id=journey.id,
                dimension=dimension.value,
                phase=phase.value,
                status=status.value,
            )
            db.add(perspective)

    await db.flush()
    return journey


async def list_journeys(
    db: AsyncSession,
    org_id: uuid.UUID,
    status_filter: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Journey], int]:
    base = select(Journey).where(Journey.organization_id == org_id)
    if status_filter:
        base = base.where(Journey.status == status_filter)

    total_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = total_result.scalar_one()

    offset = (page - 1) * per_page
    result = await db.execute(base.order_by(Journey.created_at.desc()).offset(offset).limit(per_page))
    journeys = list(result.scalars().all())
    return journeys, total


async def get_journey(db: AsyncSession, org_id: uuid.UUID, journey_id: uuid.UUID) -> dict:
    result = await db.execute(select(Journey).where(Journey.id == journey_id, Journey.organization_id == org_id))
    journey = result.scalar_one_or_none()
    if not journey:
        raise NotFoundError("Journey not found")

    persp_result = await db.execute(
        select(Perspective)
        .where(Perspective.journey_id == journey_id)
        .order_by(Perspective.dimension, Perspective.phase)
    )
    perspectives = list(persp_result.scalars().all())

    bank_result = await db.execute(
        select(BankInstance)
        .join(Perspective, BankInstance.perspective_id == Perspective.id)
        .where(Perspective.journey_id == journey_id)
        .order_by(BankInstance.created_at)
    )
    bank_instances = list(bank_result.scalars().all())

    return {"journey": journey, "perspectives": perspectives, "bank_instances": bank_instances}


async def delete_journey(db: AsyncSession, org_id: uuid.UUID, journey_id: uuid.UUID) -> None:
    result = await db.execute(select(Journey).where(Journey.id == journey_id, Journey.organization_id == org_id))
    journey = result.scalar_one_or_none()
    if not journey:
        raise NotFoundError("Journey not found")
    await db.delete(journey)
    await db.flush()


async def update_journey_status(
    db: AsyncSession, org_id: uuid.UUID, journey_id: uuid.UUID, new_status: str
) -> Journey:
    result = await db.execute(select(Journey).where(Journey.id == journey_id, Journey.organization_id == org_id))
    journey = result.scalar_one_or_none()
    if not journey:
        raise NotFoundError("Journey not found")

    if new_status == "completed":
        # Check all 12 perspectives are completed
        count_result = await db.execute(
            select(func.count())
            .select_from(Perspective)
            .where(Perspective.journey_id == journey_id, Perspective.status == PerspectiveStatus.COMPLETED.value)
        )
        completed_count = count_result.scalar_one()
        if completed_count < 12:
            raise ValidationError(f"Cannot complete journey: only {completed_count}/12 perspectives completed")
        journey.status = "completed"
        journey.completed_at = datetime.now(UTC)
        journey.perspectives_completed = 12
    elif new_status == "archived":
        journey.status = "archived"
    else:
        raise ValidationError(f"Invalid status transition: {new_status}")

    await db.flush()
    return journey
