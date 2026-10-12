from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Numeric, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base

class OfficeMarketMetric(Base):
    __tablename__ = "office_market_metrics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    rent_level: Mapped[str] = mapped_column(String(30), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    micro_market: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    rent_inr_per_sqft_per_month: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "rent_level IN ('city_average', 'micro_market')",
            name="valid_rent_level"
        ),
        CheckConstraint(
            "rent_inr_per_sqft_per_month > 0",
            name="valid_rent"
        ),
        CheckConstraint(
            "(rent_level = 'city_average' AND micro_market IS NULL) OR "
            "(rent_level = 'micro_market' AND micro_market IS NOT NULL AND micro_market <> '')",
            name="valid_micro_market"
        ),
        # Partial unique indexes to handle nullable micro_market correctly
        Index(
            "uq_office_city_average",
            "city",
            unique=True,
            postgresql_where=(rent_level == "city_average")
        ),
        Index(
            "uq_office_micro_market",
            "city",
            "micro_market",
            unique=True,
            postgresql_where=(rent_level == "micro_market")
        ),
        # Query optimization indexes
        Index("idx_office_rents_city", "city"),
        Index("idx_office_rents_level", "rent_level"),
        Index("idx_office_rents_city_level", "city", "rent_level"),
    )

    def __repr__(self) -> str:
        return f"<OfficeMarketMetric(id={self.id}, city='{self.city}', rent_level='{self.rent_level}', micro_market='{self.micro_market}', rent={self.rent_inr_per_sqft_per_month})>"
