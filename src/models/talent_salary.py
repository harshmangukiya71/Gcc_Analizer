from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import BigInteger, Text, String, Integer, Numeric, Date, DateTime, func, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base

class TalentSalaryBenchmark(Base):
    __tablename__ = "talent_salary_benchmarks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    city: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Nullable for national benchmarks
    gcc_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sector: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    job_family: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    job_title: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experience_min_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    experience_max_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    seniority_level: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    salary_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    salary_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    compensation_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    salary_period: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_year: Mapped[int] = mapped_column(Integer, nullable=False)
    sample_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_level: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_verified_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_talent_salary_city_job_seniority", "city", "job_family", "seniority_level"),
        CheckConstraint("salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max", name="chk_salary_min_max"),
        CheckConstraint("experience_min_years IS NULL OR experience_max_years IS NULL OR experience_min_years <= experience_max_years", name="chk_exp_min_max"),
    )

    def __repr__(self) -> str:
        return f"<TalentSalaryBenchmark(id={self.id}, job_title='{self.job_title}', city='{self.city}')>"
