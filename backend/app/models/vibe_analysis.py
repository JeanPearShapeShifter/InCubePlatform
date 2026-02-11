import uuid

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class VibeAnalysis(Base):
    __tablename__ = "vibe_analyses"

    vibe_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vibe_sessions.id", ondelete="CASCADE"), nullable=False
    )
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(50), default="post_vibe", server_default="post_vibe")
    content: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    agent_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_sessions.id")
    )

    # vibe_analyses only has created_at in DDL, but Base adds updated_at — acceptable

    __table_args__ = (
        UniqueConstraint("vibe_session_id", "agent_name", "analysis_type", name="uq_vibe_analyses_session_agent_type"),
        Index("idx_vibe_analyses_session", "vibe_session_id"),
    )
