import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import GoalType


class Goal(Base):
    __tablename__ = "goals"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    type: Mapped[str] = mapped_column(
        SAEnum(
            GoalType, values_callable=lambda x: [e.value for e in x],
            name="goal_type", create_constraint=False, native_enum=True,
        ),
        default="custom",
        server_default="custom",
    )

    __table_args__ = (
        Index("idx_goals_organization", "organization_id"),
    )
