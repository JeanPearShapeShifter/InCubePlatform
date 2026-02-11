import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        SAEnum(
            UserRole, values_callable=lambda x: [e.value for e in x],
            name="user_role", create_constraint=False, native_enum=True,
        ),
        default="editor",
        server_default="editor",
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_users_organization", "organization_id"),
        Index("idx_users_email", "email"),
    )
