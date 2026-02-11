from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    logo_url: Mapped[str | None] = mapped_column(String(500))
    monthly_budget_cents: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    __table_args__ = (
        Index("idx_organizations_slug", "slug"),
    )
