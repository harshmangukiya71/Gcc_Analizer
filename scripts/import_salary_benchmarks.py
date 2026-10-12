import os
import sys
import pandas as pd
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import get_engine, get_session
from src.models.base import Base
from src.models.talent_salary import TalentSalaryBenchmark

def import_salary_benchmarks(file_path: str = "data/raw/sansovi_salary_benchmarks.csv"):
    print("=" * 70)
    print("GCC COMPASS: IMPORTING TALENT SALARY BENCHMARKS INTO POSTGRESQL")
    print("=" * 70)

    # 1. Automatic Schema Verification & Creation in PostgreSQL
    print("[1/3] Ensuring talent_salary_benchmarks table exists...")
    try:
        engine = get_engine()
        Base.metadata.create_all(engine)
        print("      -> Schema verified in PostgreSQL database.")
    except Exception as e:
        print(f"[ERROR] Could not connect to PostgreSQL: {e}")
        print("Please check DATABASE_URL in .env.")
        sys.exit(1)

    # 2. Locate and Read CSV (Self-contained in repo)
    if not os.path.exists(file_path):
        fallback = os.path.join(os.path.dirname(__file__), "..", file_path)
        if os.path.exists(fallback):
            file_path = fallback
        else:
            print(f"[ERROR] Source file not found: {file_path}")
            sys.exit(1)

    print(f"[2/3] Reading salary benchmark dataset from: {file_path}")
    df = pd.read_csv(file_path)
    print(f"      -> Loaded {len(df)} records from CSV.")

    # 3. Transactional Ingestion
    print("[3/3] Importing records into PostgreSQL...")
    session = get_session()
    inserted = 0

    try:
        # Clear existing Sansovi benchmarks to prevent duplicate keys on re-run
        session.execute(
            text("DELETE FROM talent_salary_benchmarks WHERE source_name = 'Sansovi GCC Salary Benchmark'")
        )

        for idx, row in df.iterrows():
            record = TalentSalaryBenchmark(
                city=str(row["city"]),
                gcc_type="Global Capability Center (GCC)",
                sector="All Verticals (Blended)",
                job_family=str(row.get("job_family", "Engineering")),
                job_title=str(row["job_title"]),
                seniority_level=str(row["seniority_level"]),
                experience_min_years=int(row["experience_min_years"]),
                experience_max_years=int(row["experience_max_years"]),
                salary_min=Decimal(str(row["salary_min"])),
                salary_max=Decimal(str(row["salary_max"])),
                currency="INR",
                compensation_type="Total CTC (Fixed + Variable)",
                salary_period="Annual",
                data_year=2026,
                sample_size=int(row["sample_size"]) if pd.notna(row.get("sample_size")) else None,
                source_name=str(row["source_name"]),
                source_url=str(row.get("source_url", "")),
                source_notes=str(row.get("source_notes", "")),
                confidence_level="High"
            )
            session.add(record)
            inserted += 1

        session.commit()
        print("\n" + "=" * 70)
        print("TALENT SALARY BENCHMARK IMPORT SUMMARY")
        print("=" * 70)
        print(f"Total CSV Rows Processed : {len(df)}")
        print(f"Inserted into PostgreSQL : {inserted}")
        print("=" * 70)

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to import salary benchmarks: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    import_salary_benchmarks()
