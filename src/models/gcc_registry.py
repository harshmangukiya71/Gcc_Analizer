from datetime import datetime, date
from typing import Optional
from sqlalchemy import BigInteger, Text, Date, DateTime, func, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base

class GCCRegistry(Base):
    __tablename__ = "gcc_registry"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    website: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_hq_country: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    city_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Retains source value if differed
    sector: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    india_headcount: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Preserves values like 1,000+ and 200–500
    key_roles_hired: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Preserves exact source text
    gcc_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_name: Mapped[Optional[str]] = mapped_column(Text, default="GCC Journal India", nullable=True)
    last_verified_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_gcc_registry_city", "city"),
        Index("idx_gcc_registry_sector", "sector"),
        Index("idx_gcc_registry_company_name", "company_name"),
        Index("idx_gcc_registry_city_sector", "city", "sector"),
        UniqueConstraint("company_name", "city", name="uq_gcc_registry_company_city"),
    )

    def __repr__(self) -> str:
        return f"<GCCRegistry(id={self.id}, company_name='{self.company_name}', city='{self.city}')>"
