import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import BankType


class BankInstance(Base):
    __tablename__ = "bank_instances"

    perspective_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("perspectives.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(
        SAEnum(
            BankType, values_callable=lambda x: [e.value for e in x],
            name="bank_type", create_constraint=False, native_enum=True,
        ),
        nullable=False,
    )
    synopsis: Mapped[str] = mapped_column(Text, default="", server_default="")
    decision_audit: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    documents_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    vibes_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    emails_sent: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    feedback_received: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    agent_assessments: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")

    # bank_instances only has created_at in DDL, but Base adds updated_at — acceptable

    __table_args__ = (
        CheckConstraint("documents_count >= 0", name="documents_count_nonneg"),
        CheckConstraint("vibes_count >= 0", name="vibes_count_nonneg"),
        CheckConstraint("emails_sent >= 0", name="emails_sent_nonneg"),
        CheckConstraint("feedback_received >= 0", name="feedback_received_nonneg"),
        Index("idx_bank_instances_perspective", "perspective_id"),
        Index("idx_bank_instances_type", "type"),
    )
