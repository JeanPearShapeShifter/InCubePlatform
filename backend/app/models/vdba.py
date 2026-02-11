import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Vdba(Base):
    __tablename__ = "vdbas"

    journey_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("journeys.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    bank_instance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bank_instances.id"), nullable=False
    )
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    export_url: Mapped[str | None] = mapped_column(String(1000))
    export_format: Mapped[str | None] = mapped_column(String(10), default="pdf", server_default="pdf")
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")

    __table_args__ = (
        CheckConstraint("export_format IN ('pdf', 'docx', 'json')", name="export_format_check"),
        Index("idx_vdbas_organization", "organization_id"),
        Index("idx_vdbas_journey", "journey_id"),
    )
