import os
import sys
import pandas as pd
from decimal import Decimal, InvalidOperation
from typing import Optional
from sqlalchemy import select, and_

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import get_engine, get_session
from src.models.base import Base
from src.models.office_market import OfficeMarketMetric

def clean_rent_value(val) -> Optional[Decimal]:
    if pd.isna(val):
        return None
    cleaned = str(val).replace(",", "").replace("INR", "").strip()
    try:
        dec = Decimal(cleaned)
        return dec if dec > 0 else None
    except (InvalidOperation, ValueError):
        return None

def import_office_rents(file_path: str = "data/raw/GCC_Office_Rents_City_and_MicroMarket.csv"):
    print("=" * 70)
    print("GCC COMPASS: IMPORTING OFFICE RENT BENCHMARKS INTO POSTGRESQL")
    print("=" * 70)

    # 1. Automatic Schema Verification & Creation
    print("[1/3] Ensuring office_market_metrics table and indexes exist...")
    try:
        engine = get_engine()
        Base.metadata.create_all(engine)
        print("      -> Table and unique indexes verified in PostgreSQL.")
    except Exception as e:
        print(f"[ERROR] Could not connect to PostgreSQL or verify schema: {e}")
        print("Please check DATABASE_URL in .env.")
        sys.exit(1)

    # 2. Locate and Read Source CSV
    if not os.path.exists(file_path):
        fallback = os.path.join(os.path.dirname(__file__), "..", file_path)
        if os.path.exists(fallback):
            file_path = fallback
        else:
            print(f"[ERROR] Source file not found: {file_path}")
            sys.exit(1)

    print(f"[2/3] Reading office rent dataset from: {file_path}")
    df = pd.read_csv(file_path)
    df.columns = [c.strip().lower() for c in df.columns]
    total_rows = len(df)
    print(f"      -> Total rows in dataset: {total_rows}")

    # 3. Transactional Validation and Upsert
    print("[3/3] Processing records transactionally...")
    session = get_session()

    imported_count = 0
    updated_count = 0
    skipped_count = 0
    rejected_count = 0
    validation_errors = []

    try:
        for idx, row in df.iterrows():
            row_num = idx + 2
            raw_level = str(row.get("rent_level", "")).strip().lower()
            raw_city = str(row.get("city", "")).strip()
            raw_mm = row.get("micro_market")
            raw_rent = row.get("rent_inr_per_sqft_per_month")

            # Validate rent_level
            if raw_level not in ("city_average", "micro_market"):
                rejected_count += 1
                validation_errors.append(f"Row {row_num}: Invalid rent_level '{raw_level}'")
                continue

            if not raw_city:
                rejected_count += 1
                validation_errors.append(f"Row {row_num}: Missing city")
                continue

            # Convert empty micro_market to SQL NULL
            if pd.isna(raw_mm) or str(raw_mm).strip() == "" or str(raw_mm).strip().lower() == "nan":
                micro_market = None
            else:
                micro_market = str(raw_mm).strip()

            # Enforce micro_market constraint logic
            if raw_level == "city_average" and micro_market is not None:
                rejected_count += 1
                validation_errors.append(f"Row {row_num}: city_average must have NULL micro_market, got '{micro_market}'")
                continue

            if raw_level == "micro_market" and (micro_market is None or micro_market == ""):
                rejected_count += 1
                validation_errors.append(f"Row {row_num}: micro_market record requires non-empty micro_market")
                continue

            # Convert rent to Decimal
            numeric_rent = clean_rent_value(raw_rent)
            if numeric_rent is None:
                rejected_count += 1
                validation_errors.append(f"Row {row_num}: Invalid or non-positive rent value '{raw_rent}'")
                continue

            # Duplicate handling / Upsert
            if raw_level == "city_average":
                condition = and_(
                    OfficeMarketMetric.city == raw_city,
                    OfficeMarketMetric.rent_level == "city_average"
                )
            else:
                condition = and_(
                    OfficeMarketMetric.city == raw_city,
                    OfficeMarketMetric.rent_level == "micro_market",
                    OfficeMarketMetric.micro_market == micro_market
                )

            existing = session.scalar(select(OfficeMarketMetric).where(condition))

            if existing:
                if existing.rent_inr_per_sqft_per_month != numeric_rent:
                    existing.rent_inr_per_sqft_per_month = numeric_rent
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                new_record = OfficeMarketMetric(
                    rent_level=raw_level,
                    city=raw_city,
                    micro_market=micro_market,
                    rent_inr_per_sqft_per_month=numeric_rent,
                )
                session.add(new_record)
                imported_count += 1

        session.commit()
        print("\n" + "=" * 70)
        print("OFFICE RENT IMPORT SUMMARY")
        print("=" * 70)
        print(f"Total Source Rows    : {total_rows}")
        print(f"Imported (New Rows)  : {imported_count}")
        print(f"Updated (Changed)    : {updated_count}")
        print(f"Skipped (Unchanged)  : {skipped_count}")
        print(f"Rejected (Invalid)   : {rejected_count}")

        if validation_errors:
            print("\nValidation Errors encountered:")
            for err in validation_errors:
                print(f"  - {err}")
        print("=" * 70)

    except Exception as e:
        session.rollback()
        print(f"[FATAL ERROR] Import failed. Transaction rolled back: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    import_office_rents()
