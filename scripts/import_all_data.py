import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.import_gcc_data import run_import as import_gccs
from scripts.import_office_rents import import_office_rents
from scripts.import_salary_benchmarks import import_salary_benchmarks
from scripts.import_incentives import import_incentives

def import_all():
    print("#" * 70)
    print("GCC COMPASS: MASTER REPOSITORY DATA INGESTION PIPELINE")
    print("Loading all datasets into PostgreSQL from repository files...")
    print("#" * 70 + "\n")

    # 1. GCC Registry (274 records)
    print(">>> STEP 1/4: IMPORTING GCC COMPANIES REGISTRY")
    import_gccs()
    print("\n" + "-" * 70 + "\n")

    # 2. Office Market Metrics (64 records)
    print(">>> STEP 2/4: IMPORTING OFFICE RENT BENCHMARKS")
    import_office_rents()
    print("\n" + "-" * 70 + "\n")

    # 3. Talent Salary Benchmarks (330 records)
    print(">>> STEP 3/4: IMPORTING TALENT SALARY BENCHMARKS")
    import_salary_benchmarks()
    print("\n" + "-" * 70 + "\n")

    # 4. State Incentive Schemes (43 records)
    print(">>> STEP 4/4: IMPORTING STATE INCENTIVE SCHEMES")
    import_incentives()
    print("\n" + "=" * 70)
    print("ALL 4 DATASETS IMPORTED SUCCESSFULLY INTO POSTGRESQL!")
    print("=" * 70)

if __name__ == "__main__":
    import_all()
