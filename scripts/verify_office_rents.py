import os
import sys
from sqlalchemy import select, func

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import get_session
from src.models.office_market import OfficeMarketMetric

def verify_office_rents():
    print("=" * 70)
    print("GCC COMPASS: VERIFICATION OF OFFICE RENT BENCHMARKS")
    print("=" * 70)

    session = get_session()
    try:
        total_in_db = session.scalar(select(func.count(OfficeMarketMetric.id)))
        city_avg_count = session.scalar(
            select(func.count(OfficeMarketMetric.id)).where(OfficeMarketMetric.rent_level == "city_average")
        )
        micro_count = session.scalar(
            select(func.count(OfficeMarketMetric.id)).where(OfficeMarketMetric.rent_level == "micro_market")
        )

        print(f"Total Office Rent Records in DB : {total_in_db}  (Expected: 64)")
        print(f"City Average Records            : {city_avg_count}  (Expected: 7)")
        print(f"Micro-Market Records            : {micro_count}  (Expected: 57)")

        # Verify Ahmedabad check
        ahmedabad_cnt = session.scalar(
            select(func.count(OfficeMarketMetric.id)).where(OfficeMarketMetric.city.ilike("%ahmedabad%"))
        )
        print(f"Ahmedabad Records Count         : {ahmedabad_cnt}  (Expected: 0 - omitted from source PDF)")

        all_matched = (total_in_db == 64 and city_avg_count == 7 and micro_count == 57 and ahmedabad_cnt == 0)

        if all_matched:
            print("\n>>> AUDIT VERIFICATION: PASSED! All counts match source specifications exactly.")
        else:
            print("\n>>> AUDIT VERIFICATION: DISCREPANCY DETECTED.")
            if total_in_db != 64:
                print(f"    - Total mismatch: {total_in_db} vs expected 64")
            if city_avg_count != 7:
                print(f"    - City average mismatch: {city_avg_count} vs expected 7")
            if micro_count != 57:
                print(f"    - Micro market mismatch: {micro_count} vs expected 57")

        print("\n--- City Average Benchmarks (Ranked Lowest to Highest) ---")
        avg_query = (
            select(OfficeMarketMetric.city, OfficeMarketMetric.rent_inr_per_sqft_per_month)
            .where(OfficeMarketMetric.rent_level == "city_average")
            .order_by(OfficeMarketMetric.rent_inr_per_sqft_per_month)
        )
        for c, rent in session.execute(avg_query).all():
            print(f"  {c:<15}: INR {rent:>6.2f} / sq ft / month")

        print("\n--- Sample Bengaluru Micro-Markets (Ranked Highest to Lowest) ---")
        blr_query = (
            select(OfficeMarketMetric.micro_market, OfficeMarketMetric.rent_inr_per_sqft_per_month)
            .where(
                OfficeMarketMetric.city == "Bengaluru",
                OfficeMarketMetric.rent_level == "micro_market"
            )
            .order_by(OfficeMarketMetric.rent_inr_per_sqft_per_month.desc())
        )
        for mm, rent in session.execute(blr_query).all():
            print(f"  {mm:<25}: INR {rent:>6.2f} / sq ft / month")

        print("=" * 70)
        return all_matched

    finally:
        session.close()

if __name__ == "__main__":
    verify_office_rents()
