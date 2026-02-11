import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import JourneyStatus


class Journey(Base):
    __tablename__ = "journeys"

    goal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        SAEnum(
            JourneyStatus, values_callable=lambda x: [e.value for e in x],
            name="journey_status", create_constraint=False, native_enum=True,
        ),
        default="active",
        server_default="active",
    )
    perspectives_completed: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    total_cost_cents: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("perspectives_completed BETWEEN 0 AND 12", name="perspectives_completed_range"),
        Index("idx_journeys_organization", "organization_id"),
        Index("idx_journeys_status", "organization_id", "status"),
    )
