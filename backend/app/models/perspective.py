import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import DimensionType, PerspectiveStatus, PhaseType


class Perspective(Base):
    __tablename__ = "perspectives"

    journey_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("journeys.id", ondelete="CASCADE"), nullable=False
    )
    dimension: Mapped[str] = mapped_column(
        SAEnum(
            DimensionType, values_callable=lambda x: [e.value for e in x],
            name="dimension_type", create_constraint=False, native_enum=True,
        ),
        nullable=False,
    )
    phase: Mapped[str] = mapped_column(
        SAEnum(
            PhaseType, values_callable=lambda x: [e.value for e in x],
            name="phase_type", create_constraint=False, native_enum=True,
        ),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        SAEnum(
            PerspectiveStatus, values_callable=lambda x: [e.value for e in x],
            name="perspective_status", create_constraint=False, native_enum=True,
        ),
        default="locked",
        server_default="locked",
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("journey_id", "dimension", "phase", name="uq_perspectives_journey_dimension_phase"),
        Index("idx_perspectives_journey", "journey_id"),
        Index("idx_perspectives_status", "journey_id", "status"),
    )
