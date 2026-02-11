import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class VibeSession(Base):
    __tablename__ = "vibe_sessions"

    perspective_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("perspectives.id", ondelete="CASCADE"), nullable=False
    )
    conducted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    audio_minio_key: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    transcript_text: Mapped[str | None] = mapped_column(Text)
    transcript_minio_key: Mapped[str | None] = mapped_column(String(1000))
    transcription_cost_cents: Mapped[float] = mapped_column(Numeric(10, 4), default=0, server_default="0")
    status: Mapped[str] = mapped_column(String(20), default="transcribing", server_default="transcribing")

    # vibe_sessions only has created_at in DDL, but Base adds updated_at — acceptable

    __table_args__ = (
        CheckConstraint("duration_seconds > 0", name="duration_seconds_positive"),
        CheckConstraint(
            "status IN ('transcribing', 'analyzing', 'complete', 'failed')",
            name="vibe_status_check",
        ),
        Index("idx_vibe_sessions_perspective", "perspective_id"),
    )
