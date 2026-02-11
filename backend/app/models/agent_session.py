import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AgentSession(Base):
    __tablename__ = "agent_sessions"

    perspective_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("perspectives.id", ondelete="CASCADE"), nullable=False
    )
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    model_used: Mapped[str] = mapped_column(
        String(50), default="claude-haiku-4-5-20251001", server_default="claude-haiku-4-5-20251001",
    )
    system_prompt_version: Mapped[str] = mapped_column(String(20), default="v1", server_default="v1")
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    cost_cents: Mapped[float] = mapped_column(Numeric(10, 4), default=0, server_default="0")
    request_payload: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    response_payload: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    duration_ms: Mapped[int | None] = mapped_column(Integer)

    # agent_sessions only has created_at in DDL, but Base adds updated_at too — acceptable

    __table_args__ = (
        CheckConstraint(
            "agent_name IN ('lyra','mira','dex','rex','vela','koda','halo','nova','axiom')",
            name="agent_name_check",
        ),
        CheckConstraint("input_tokens >= 0", name="input_tokens_nonneg"),
        CheckConstraint("output_tokens >= 0", name="output_tokens_nonneg"),
        Index("idx_agent_sessions_perspective", "perspective_id"),
        Index("idx_agent_sessions_agent", "agent_name", "created_at"),
        Index("idx_agent_sessions_cost", "created_at", "cost_cents"),
    )
