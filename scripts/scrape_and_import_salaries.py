import os
import sys
import json
import urllib.request
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import get_engine, get_session
from src.models.base import Base
from src.models.talent_salary import TalentSalaryBenchmark

API_BASE = "https://sansovi-gcc-platform-492263949881.asia-south1.run.app/api/v1/intelligence/salary-benchmark"

ROLES = [
    "data-engineer", "ml-engineer", "swe", "cloud-devops",
    "risk-analyst", "product-manager", "cybersecurity", "adas",
    "finance", "hr-bp", "vp-tech", "cto"
]

CITIES = ["bengaluru", "hyderabad", "pune", "mumbai", "chennai", "ncr"]

EXP_BANDS = [
    ("0-2 yr", 0, 2, "0–2 years"),
    ("3-7 yr", 3, 7, "3–7 years"),
    ("7-12 yr", 7, 12, "7–12 years"),
    ("12-18 yr", 12, 18, "12–18 years"),
    ("18+ yr", 18, 30, "18+ years")
]

CITY_NAME_MAP = {
    "bengaluru": "Bengaluru",
    "hyderabad": "Hyderabad",
    "pune": "Pune",
    "mumbai": "Mumbai",
    "chennai": "Chennai",
    "ncr": "Delhi NCR"
}

JOB_FAMILY_MAP = {
    "data-engineer": "Data & Analytics",
    "ml-engineer": "AI / Machine Learning",
    "swe": "Software Engineering",
    "cloud-devops": "Cloud & Infrastructure",
    "risk-analyst": "Risk & Analytics",
    "product-manager": "Product Management",
    "cybersecurity": "Information Security",
    "adas": "Automotive & Embedded",
    "finance": "Corporate Functions",
    "hr-bp": "Human Resources",
    "vp-tech": "Executive Leadership",
    "cto": "Executive Leadership"
}

def fetch_single(role_key, city_key, exp_tuple):
    exp_api, exp_min, exp_max, exp_label = exp_tuple
    url = f"{API_BASE}?role={role_key}&city={city_key}&experienceBand={urllib.parse.quote(exp_api)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            data["_role_key"] = role_key
            data["_city_key"] = city_key
            data["_exp_min"] = exp_min
            data["_exp_max"] = exp_max
            data["_exp_label"] = exp_label
            return data
    except Exception as e:
        print(f"Error fetching {role_key}-{city_key}-{exp_api}: {e}")
        return None

def scrape_and_import():
    print("=" * 70)
    print("SANSOVI SALARY BENCHMARK: SCRAPING & POSTGRESQL IMPORT")
    print("=" * 70)

    tasks = []
    for r in ROLES:
        for c in CITIES:
            for exp in EXP_BANDS:
                tasks.append((r, c, exp))

    print(f"Total benchmark combinations to fetch: {len(tasks)}")

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_single, r, c, exp): (r, c, exp) for r, c, exp in tasks}
        completed = 0
        for fut in as_completed(futures):
            res = fut.result()
            if res:
                results.append(res)
            completed += 1
            if completed % 60 == 0 or completed == len(tasks):
                print(f"  -> Progress: {completed}/{len(tasks)} combinations scraped ({len(results)} successful)")

    print(f"\nSuccessfully collected {len(results)} benchmark records.")

    # 1. Save Raw JSON and CSV
    os.makedirs("data/raw", exist_ok=True)
    json_path = "data/raw/sansovi_salary_benchmarks.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved full JSON to: {json_path}")

    flat_rows = []
    for d in results:
        sr = d.get("salaryRange", {})
        flat_rows.append({
            "job_title": d.get("role"),
            "city": CITY_NAME_MAP.get(d.get("_city_key"), d.get("city")),
            "job_family": JOB_FAMILY_MAP.get(d.get("_role_key"), "Engineering"),
            "seniority_level": d.get("_exp_label"),
            "experience_min_years": d.get("_exp_min"),
            "experience_max_years": d.get("_exp_max"),
            "salary_min": sr.get("p25", 0) * 100000,
            "salary_median": sr.get("median", 0) * 100000,
            "salary_max": sr.get("p75", 0) * 100000,
            "salary_p90": sr.get("p90", 0) * 100000,
            "currency": "INR",
            "salary_period": "Annual",
            "data_year": 2026,
            "sample_size": d.get("dataPoints", 0),
            "source_name": "Sansovi GCC Salary Benchmark",
            "source_url": "https://www.sansovi.com/gcc/salary-benchmark/",
            "confidence_level": "High",
            "verticals_json": json.dumps(d.get("verticalBreakdown", [])),
            "city_breakdown_json": json.dumps(d.get("cityBreakdown", []))
        })

    df = pd.DataFrame(flat_rows)
    csv_path = "data/raw/sansovi_salary_benchmarks.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved tabular CSV to: {csv_path}")

    # 2. Database Ingestion
    print("\nConnecting to PostgreSQL and verifying talent_salary_benchmarks table...")
    engine = get_engine()
    Base.metadata.create_all(engine)

    session = get_session()
    inserted = 0
    updated = 0

    try:
        # Clear existing Sansovi benchmarks to prevent stale duplicates
        session.execute(
            text("DELETE FROM talent_salary_benchmarks WHERE source_name = 'Sansovi GCC Salary Benchmark'")
        )
        session.commit()

        for r in flat_rows:
            record = TalentSalaryBenchmark(
                city=r["city"],
                gcc_type="Global Capability Center (GCC)",
                sector="All Verticals (Blended)",
                job_family=r["job_family"],
                job_title=r["job_title"],
                seniority_level=r["seniority_level"],
                experience_min_years=r["experience_min_years"],
                experience_max_years=r["experience_max_years"],
                salary_min=Decimal(str(r["salary_min"])),
                salary_max=Decimal(str(r["salary_max"])),
                currency="INR",
                compensation_type="Total CTC (Fixed + Variable)",
                salary_period="Annual",
                data_year=2026,
                sample_size=r["sample_size"],
                source_name=r["source_name"],
                source_url=r["source_url"],
                source_notes=f"P10-P90 range with industry vertical and city cost indices. Median: INR {r['salary_median'] / 100000:.1f}L",
                confidence_level=r["confidence_level"]
            )
            session.add(record)
            inserted += 1

        session.commit()
        print("\n" + "=" * 70)
        print("DATABASE INGESTION COMPLETE")
        print(f"  Inserted Records in PostgreSQL : {inserted}")
        print("=" * 70)

    except Exception as e:
        session.rollback()
        print(f"Error importing into PostgreSQL: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    scrape_and_import()
