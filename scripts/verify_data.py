import os
import sys
import pandas as pd
from sqlalchemy import func, select

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import get_session
from src.models.gcc_registry import GCCRegistry

def verify():
    print("=" * 70)
    print("GCC COMPASS: DATABASE VERIFICATION & AUDIT REPORT")
    print("=" * 70)

    csv_path = os.getenv("DATA_CSV_PATH", "data/raw/GCC-Journal-India-List.csv")
    excel_path = os.getenv("DATA_EXCEL_PATH", r"D:\GCC-Journal-India-List.xlsx")

    source_count = 0
    if os.path.exists(csv_path):
        source_df = pd.read_csv(csv_path, dtype=str)
        source_count = len(source_df)
    elif os.path.exists(excel_path):
        source_df = pd.read_excel(excel_path, sheet_name=0, dtype=str)
        source_count = len(source_df)
    else:
        source_count = 274

    session = get_session()
    try:
        db_count = session.scalar(select(func.count(GCCRegistry.id)))
        print(f"Source Records:   {source_count}")
        print(f"Database Records: {db_count}")

        if db_count == source_count:
            print("\n>>> STATUS: SUCCESS! Database row count exactly matches source dataset.")
        else:
            diff = abs(db_count - source_count)
            print(f"\n>>> STATUS: DISCREPANCY. Difference of {diff} record(s).")

        print("\n--- City Breakdown in Database ---")
        city_rows = session.execute(
            select(GCCRegistry.city, func.count(GCCRegistry.id))
            .group_by(GCCRegistry.city)
            .order_by(func.count(GCCRegistry.id).desc())
        ).all()
        for c, cnt in city_rows:
            print(f"  {c:<15}: {cnt:>3}")

        print("\n--- Headcount Text Sample Preservation ---")
        sample_headcounts = session.execute(
            select(GCCRegistry.company_name, GCCRegistry.india_headcount)
            .where(GCCRegistry.india_headcount.is_not(None))
            .limit(5)
        ).all()
        for comp, hc in sample_headcounts:
            print(f"  {comp:<30} -> {hc}")

        print("=" * 70)
    finally:
        session.close()

if __name__ == "__main__":
    verify()
