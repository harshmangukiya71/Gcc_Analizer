from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import BigInteger, Text, String, Integer, Numeric, Date, DateTime, func, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
try:
    from .base import Base
except ImportError:
    from src.models.base import Base

class GCCExpansionEvent(Base):
    __tablename__ = "gcc_expansion_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    state_or_ut: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)  # New Center, Expansion, R&D Hub
    sector: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    announcement_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expected_opening_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    announced_investment: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 2), nullable=True)
    investment_currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    announced_jobs: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    actual_jobs_created: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    event_status: Mapped[str] = mapped_column(Text, nullable=False)  # announced, planned, hiring, opened, delayed, cancelled, unverified
    source_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_level: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_verified_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_expansion_city_status", "city", "event_status"),
        CheckConstraint("announced_jobs IS NULL OR announced_jobs >= 0", name="chk_announced_jobs_positive"),
        CheckConstraint("actual_jobs_created IS NULL OR actual_jobs_created >= 0", name="chk_actual_jobs_positive"),
        CheckConstraint("announced_investment IS NULL OR announced_investment >= 0", name="chk_investment_positive"),
    )

    def __repr__(self) -> str:
        return f"<GCCExpansionEvent(id={self.id}, company_name='{self.company_name}', city='{self.city}', status='{self.event_status}')>"
