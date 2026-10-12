import os
import sys
import pandas as pd
from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import get_engine, get_session
from src.models.base import Base
# Import all models to ensure complete schema creation
from src.models.gcc_registry import GCCRegistry
from src.models.talent_salary import TalentSalaryBenchmark
from src.models.office_market import OfficeMarketMetric
from src.models.incentive_schemes import IncentiveScheme
from src.models.expansion_events import GCCExpansionEvent
from src.normalizers import normalize_city

def run_import(batch_size: int = 500):
    print("=" * 70)
    print("GCC COMPASS: AUTOMATED SCHEMA VERIFICATION & DATA INGESTION")
    print("=" * 70)

    # 1. Automatic Schema Creation directly in PostgreSQL
    print("[1/4] Connecting to PostgreSQL and creating schema...")
    try:
        engine = get_engine()
        Base.metadata.create_all(engine)
        print("      -> Schema verified and all 5 tables/indexes created successfully!")
    except Exception as e:
        print(f"[ERROR] Could not connect to PostgreSQL or create schema: {e}")
        print("Please ensure your PostgreSQL password is set in .env and the database exists.")
        sys.exit(1)

    # 2. Locate Source File
    csv_path = os.getenv("DATA_CSV_PATH", "data/raw/GCC-Journal-India-List.csv")
    excel_path = os.getenv("DATA_EXCEL_PATH", r"D:\GCC-Journal-India-List.xlsx")
    
    file_to_load = None
    if os.path.exists(csv_path):
        file_to_load = csv_path
        print(f"[2/4] Reading data from CSV: {csv_path}")
        df = pd.read_csv(csv_path, dtype=str)
    elif os.path.exists(excel_path):
        file_to_load = excel_path
        print(f"[2/4] Reading master sheet from Excel: {excel_path}")
        df = pd.read_excel(excel_path, sheet_name=0, dtype=str)
    else:
        print(f"[ERROR] Neither CSV ({csv_path}) nor Excel ({excel_path}) could be found.")
        sys.exit(1)

    df = df.fillna("")
    total_records = len(df)
    print(f"      -> Total records found in dataset: {total_records}")

    # 3. Process records and prepare for batch upsert
    print(f"[3/4] Validating records and preparing batch upsert...")
    session = get_session()
    
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    rejected_count = 0
    validation_errors = []
    
    records_to_upsert = []

    for idx, row in df.iterrows():
        row_num = idx + 2
        comp_name = row.get("Company / GCC Name", "").strip()
        raw_city = row.get("City", "").strip()

        # Validation: Required fields
        if not comp_name:
            rejected_count += 1
            validation_errors.append(f"Row {row_num}: Missing 'Company / GCC Name'")
            continue

        if not raw_city:
            rejected_count += 1
            validation_errors.append(f"Row {row_num}: Missing 'City' for company '{comp_name}'")
            continue

        city_normalized, city_raw_saved = normalize_city(raw_city)

        website = row.get("Website", "").strip() or None
        parent_hq_country = row.get("Parent HQ Country", "").strip() or None
        sector = row.get("Sector", "").strip() or None
        india_headcount = row.get("India Headcount", "").strip() or None
        key_roles = row.get("Key Roles Hired", "").strip() or None
        notes = row.get("GCC Notes", "").strip() or None

        records_to_upsert.append({
            "company_name": comp_name,
            "website": website,
            "parent_hq_country": parent_hq_country,
            "city": city_normalized,
            "city_raw": city_raw_saved,
            "sector": sector,
            "india_headcount": india_headcount,
            "key_roles_hired": key_roles,
            "gcc_notes": notes,
            "source_name": "GCC Journal India",
        })

    # 4. Transactional Upsert Execution
    print(f"[4/4] Executing database transaction in batches of {batch_size}...")
    try:
        # Pre-query existing (company_name, city) pairs to distinguish inserts vs updates
        existing_keys = set(
            session.execute(
                select(GCCRegistry.company_name, GCCRegistry.city)
            ).all()
        )

        for i in range(0, len(records_to_upsert), batch_size):
            chunk = records_to_upsert[i : i + batch_size]
            for rec in chunk:
                key = (rec["company_name"], rec["city"])
                is_update = key in existing_keys

                stmt = insert(GCCRegistry).values(**rec)
                stmt = stmt.on_conflict_do_update(
                    constraint="uq_gcc_registry_company_city",
                    set_={
                        "website": stmt.excluded.website,
                        "parent_hq_country": stmt.excluded.parent_hq_country,
                        "sector": stmt.excluded.sector,
                        "india_headcount": stmt.excluded.india_headcount,
                        "key_roles_hired": stmt.excluded.key_roles_hired,
                        "gcc_notes": stmt.excluded.gcc_notes,
                        "updated_at": func.now(),
                    }
                )
                session.execute(stmt)

                if is_update:
                    updated_count += 1
                else:
                    inserted_count += 1
                    existing_keys.add(key)

        session.commit()
        print("\n" + "=" * 70)
        print("IMPORT TRANSACTION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"Total Source Rows Read: {total_records}")
        print(f"Newly Inserted Records: {inserted_count}")
        print(f"Updated Records       : {updated_count}")
        print(f"Skipped Records       : {skipped_count}")
        print(f"Rejected Records      : {rejected_count}")
        
        if validation_errors:
            print("\nValidation Errors encountered:")
            for err in validation_errors:
                print(f"  - {err}")
        print("=" * 70)

    except Exception as e:
        session.rollback()
        print(f"\n[FATAL ERROR] Ingestion failed. Transaction rolled back: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    run_import()
