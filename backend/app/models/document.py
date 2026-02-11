import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    perspective_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("perspectives.id", ondelete="CASCADE"), nullable=False
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    minio_key: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)

    # documents only has created_at in DDL, but Base adds updated_at — acceptable

    __table_args__ = (
        CheckConstraint("file_size > 0", name="file_size_positive"),
        Index("idx_documents_perspective", "perspective_id"),
    )
