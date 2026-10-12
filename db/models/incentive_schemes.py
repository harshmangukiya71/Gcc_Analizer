from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import BigInteger, Text, String, Numeric, Date, DateTime, func, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
try:
    from .base import Base
except ImportError:
    from src.models.base import Base

class IncentiveScheme(Base):
    __tablename__ = "incentive_schemes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    policy_name: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    state_or_ut: Mapped[str] = mapped_column(Text, nullable=False)
    gcc_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    incentive_category: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    benefit_description: Mapped[str] = mapped_column(Text, nullable=False)
    incentive_formula: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    maximum_benefit: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    eligibility_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    application_deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    policy_status: Mapped[str] = mapped_column(Text, nullable=False)  # Active, Expired, Proposed
    official_source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_verified_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_incentive_state_status", "state_or_ut", "policy_status"),
        CheckConstraint("effective_from IS NULL OR effective_until IS NULL OR effective_from <= effective_until", name="chk_effective_dates"),
    )

    def __repr__(self) -> str:
        return f"<IncentiveScheme(id={self.id}, policy_name='{self.policy_name}', state='{self.state_or_ut}')>"
