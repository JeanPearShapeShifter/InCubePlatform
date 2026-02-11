import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.models.bank_instance import BankInstance
from app.models.enums import BankType, JourneyStatus, PerspectiveStatus
from app.models.journey import Journey
from app.models.perspective import Perspective
from app.models.vdba import Vdba
from app.schemas.vdba import VdbaCreate
from app.services.notify import notify_vdba_published


async def publish_journey(
    db: AsyncSession,
    journey_id: uuid.UUID,
    org_id: uuid.UUID,
    body: VdbaCreate,
    user_id: uuid.UUID | None = None,
) -> Vdba:
    """Publish a journey as a VDBA.

    Verifies that the journey belongs to the org, all 12 perspectives are completed,
    and creates a Vdba record linked to the most recent film_reel bank instance.
    """
    # Verify journey belongs to org
    result = await db.execute(
        select(Journey).where(Journey.id == journey_id, Journey.organization_id == org_id)
    )
    journey = result.scalar_one_or_none()
    if not journey:
        raise NotFoundError("Journey not found")

    # Verify all 12 perspectives are completed
    count_result = await db.execute(
        select(func.count())
        .select_from(Perspective)
        .where(
            Perspective.journey_id == journey_id,
            Perspective.status == PerspectiveStatus.COMPLETED.value,
        )
    )
    completed_count = count_result.scalar_one()
    if completed_count < 12:
        raise ValidationError(
            f"Cannot publish: only {completed_count}/12 perspectives completed"
        )

    # Get the most recent film_reel bank instance for this journey
    bank_result = await db.execute(
        select(BankInstance)
        .join(Perspective, BankInstance.perspective_id == Perspective.id)
        .where(
            Perspective.journey_id == journey_id,
            BankInstance.type == BankType.FILM_REEL.value,
        )
        .order_by(BankInstance.created_at.desc())
        .limit(1)
    )
    bank_instance = bank_result.scalar_one_or_none()
    if not bank_instance:
        # Fall back to any bank instance if no film_reel exists
        fallback_result = await db.execute(
            select(BankInstance)
            .join(Perspective, BankInstance.perspective_id == Perspective.id)
            .where(Perspective.journey_id == journey_id)
            .order_by(BankInstance.created_at.desc())
            .limit(1)
        )
        bank_instance = fallback_result.scalar_one_or_none()
        if not bank_instance:
            raise ValidationError("No bank instances found for this journey")

    # Determine version (increment from latest VDBA for this journey)
    version_result = await db.execute(
        select(func.coalesce(func.max(Vdba.version), 0))
        .where(Vdba.journey_id == journey_id)
    )
    next_version = version_result.scalar_one() + 1

    # Create VDBA record
    vdba = Vdba(
        journey_id=journey_id,
        organization_id=org_id,
        title=body.title,
        description=body.description,
        bank_instance_id=bank_instance.id,
        export_format=body.export_format,
        version=next_version,
        published_at=datetime.now(UTC),
    )
    db.add(vdba)

    # Mark journey as completed
    journey.status = JourneyStatus.COMPLETED.value
    journey.completed_at = datetime.now(UTC)
    journey.perspectives_completed = 12

    await db.flush()

    if user_id:
        await notify_vdba_published(db, org_id, user_id, body.title)

    return vdba


async def list_vdbas(
    db: AsyncSession,
    org_id: uuid.UUID,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Vdba], int]:
    """List VDBAs for an organization with pagination."""
    base = select(Vdba).where(Vdba.organization_id == org_id)

    total_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = total_result.scalar_one()

    offset = (page - 1) * per_page
    result = await db.execute(
        base.order_by(Vdba.published_at.desc()).offset(offset).limit(per_page)
    )
    vdbas = list(result.scalars().all())
    return vdbas, total


async def get_vdba(
    db: AsyncSession,
    vdba_id: uuid.UUID,
    org_id: uuid.UUID,
) -> Vdba:
    """Get a single VDBA by ID, scoped to the organization."""
    result = await db.execute(
        select(Vdba).where(Vdba.id == vdba_id, Vdba.organization_id == org_id)
    )
    vdba = result.scalar_one_or_none()
    if not vdba:
        raise NotFoundError("VDBA not found")
    return vdba
