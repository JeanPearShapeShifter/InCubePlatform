import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    token_type: Mapped[str] = mapped_column(String(20), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # auth_tokens has only created_at, no updated_at in DDL — but our Base provides both.
    # We keep the Base columns as-is for consistency.

    __table_args__ = (
        CheckConstraint("token_type IN ('email_verify', 'password_reset')", name="token_type_check"),
        Index("idx_auth_tokens_hash", "token_hash", postgresql_where="used_at IS NULL"),
    )
