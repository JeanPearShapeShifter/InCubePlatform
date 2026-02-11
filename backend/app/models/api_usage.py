import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ApiService


class ApiUsage(Base):
    __tablename__ = "api_usage"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    service: Mapped[str] = mapped_column(
        SAEnum(
            ApiService, values_callable=lambda x: [e.value for e in x],
            name="api_service", create_constraint=False, native_enum=True,
        ),
        nullable=False,
    )
    model_name: Mapped[str | None] = mapped_column(String(50))
    tokens_in: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    tokens_out: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    cost_cents: Mapped[float] = mapped_column(Numeric(10, 4), default=0, server_default="0")
    endpoint: Mapped[str | None] = mapped_column(String(200))

    __table_args__ = (
        Index("idx_api_usage_org_date", "organization_id", "created_at"),
        Index("idx_api_usage_service", "service", "created_at"),
    )
