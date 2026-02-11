import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ChallengeResolution, ChallengeSeverity


class AxiomChallenge(Base):
    __tablename__ = "axiom_challenges"

    perspective_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("perspectives.id", ondelete="CASCADE"), nullable=False
    )
    challenge_text: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        SAEnum(
            ChallengeSeverity, values_callable=lambda x: [e.value for e in x],
            name="challenge_severity", create_constraint=False, native_enum=True,
        ),
        nullable=False,
    )
    targeted_agents: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, server_default="{}")
    evidence_needed: Mapped[str] = mapped_column(Text, default="", server_default="")
    resolution: Mapped[str | None] = mapped_column(
        SAEnum(
            ChallengeResolution, values_callable=lambda x: [e.value for e in x],
            name="challenge_resolution", create_constraint=False, native_enum=True,
        ),
    )
    resolution_text: Mapped[str | None] = mapped_column(Text)
    agent_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_sessions.id")
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_axiom_challenges_perspective", "perspective_id"),
        Index("idx_axiom_challenges_unresolved", "perspective_id", postgresql_where="resolution IS NULL"),
    )
