import os
import sys
import pytest
import pandas as pd
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.office_market import OfficeMarketMetric

CSV_PATH = "data/raw/GCC_Office_Rents_City_and_MicroMarket.csv"

def test_source_csv_exists_and_row_counts():
    """Verify that source CSV exists and contains exactly 64 records."""
    assert os.path.exists(CSV_PATH), f"CSV file not found at {CSV_PATH}"
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip().lower() for c in df.columns]

    assert len(df) == 64, f"Expected 64 rows, got {len(df)}"
    city_avg_df = df[df["rent_level"] == "city_average"]
    micro_df = df[df["rent_level"] == "micro_market"]

    assert len(city_avg_df) == 7, f"Expected 7 city averages, got {len(city_avg_df)}"
    assert len(micro_df) == 57, f"Expected 57 micro markets, got {len(micro_df)}"

def test_ahmedabad_omitted_from_source():
    """Verify Ahmedabad is omitted from office rent benchmarks as per spec."""
    df = pd.read_csv(CSV_PATH)
    ahmedabad = df[df["city"].str.lower().str.contains("ahmedabad")]
    assert len(ahmedabad) == 0, "Ahmedabad should not be present in the dataset"

def test_micro_market_nullability_rules():
    """Verify city_average has NULL micro_market and micro_market has non-empty string."""
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip().lower() for c in df.columns]

    city_avg = df[df["rent_level"] == "city_average"]
    assert city_avg["micro_market"].isna().all(), "All city_average rows must have NaN micro_market"

    micro = df[df["rent_level"] == "micro_market"]
    assert not micro["micro_market"].isna().any(), "No micro_market rows can have NaN micro_market"
    assert (micro["micro_market"].str.strip() != "").all(), "No micro_market rows can have empty string"

def test_rent_values_positive_and_valid():
    """Verify all rent figures are strictly positive numeric values."""
    df = pd.read_csv(CSV_PATH)
    rents = pd.to_numeric(df["rent_inr_per_sqft_per_month"], errors="coerce")
    assert not rents.isna().any(), "All rent values must be valid numbers"
    assert (rents > 0).all(), "All rent values must be greater than 0"

def test_model_instantiation():
    """Test creating OfficeMarketMetric instances."""
    m1 = OfficeMarketMetric(
        rent_level="city_average",
        city="Bengaluru",
        micro_market=None,
        rent_inr_per_sqft_per_month=Decimal("103.00")
    )
    assert m1.rent_level == "city_average"
    assert m1.micro_market is None
    assert m1.rent_inr_per_sqft_per_month == Decimal("103.00")

    m2 = OfficeMarketMetric(
        rent_level="micro_market",
        city="Bengaluru",
        micro_market="Outer Ring Road",
        rent_inr_per_sqft_per_month=Decimal("110.00")
    )
    assert m2.rent_level == "micro_market"
    assert m2.micro_market == "Outer Ring Road"
