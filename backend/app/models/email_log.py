import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import EmailTemplate


class EmailLog(Base):
    __tablename__ = "email_log"

    perspective_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("perspectives.id", ondelete="CASCADE"), nullable=False
    )
    sent_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    recipient_email: Mapped[str] = mapped_column(String(320), nullable=False)
    recipient_type: Mapped[str] = mapped_column(String(50), default="stakeholder", server_default="stakeholder")
    template_type: Mapped[str] = mapped_column(
        SAEnum(
            EmailTemplate, values_callable=lambda x: [e.value for e in x],
            name="email_template", create_constraint=False, native_enum=True,
        ),
        nullable=False,
    )
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body_preview: Mapped[str | None] = mapped_column(Text)
    resend_message_id: Mapped[str | None] = mapped_column(String(100))
    delivery_status: Mapped[str] = mapped_column(String(20), default="sent", server_default="sent")
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "delivery_status IN ('sent', 'delivered', 'bounced', 'failed')",
            name="delivery_status_check",
        ),
        Index("idx_email_log_perspective", "perspective_id"),
    )
