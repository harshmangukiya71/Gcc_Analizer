import os
import sys
import csv
from decimal import Decimal
import psycopg2
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def import_incentives(file_path: str = "data/raw/state_gcc_incentive_policies.csv"):
    print("=" * 70)
    print("GCC COMPASS: IMPORTING STATE INCENTIVE SCHEMES INTO POSTGRESQL")
    print("=" * 70)

    # 1. Connect to PostgreSQL
    print("[1/3] Connecting to PostgreSQL database...")
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        print("[ERROR] DATABASE_URL not set in .env")
        sys.exit(1)

    dsn = db_url.replace("postgresql+psycopg2://", "postgresql://")
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()

    # 2. Verify Table Exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS incentive_schemes (
        id BIGSERIAL PRIMARY KEY,
        policy_name TEXT NOT NULL,
        city TEXT,
        state_or_ut TEXT NOT NULL,
        gcc_type TEXT,
        incentive_category TEXT,
        benefit_description TEXT NOT NULL,
        incentive_formula TEXT,
        maximum_benefit NUMERIC(14, 2),
        currency VARCHAR(50),
        eligibility_criteria TEXT,
        effective_from DATE,
        effective_until DATE,
        application_deadline DATE,
        policy_status TEXT NOT NULL,
        official_source_url TEXT,
        source_notes TEXT,
        last_verified_at DATE,
        created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
    );
    """)
    conn.commit()
    print("      -> Table incentive_schemes verified.")

    # 3. Locate CSV File
    if not os.path.exists(file_path):
        fallback = os.path.join(os.path.dirname(__file__), "..", file_path)
        if os.path.exists(fallback):
            file_path = fallback
        else:
            print(f"[ERROR] Source file not found: {file_path}")
            sys.exit(1)

    print(f"[2/3] Reading state incentives dataset from: {file_path}")

    # 4. Truncate & Insert
    print("[3/3] Inserting 43 incentive records across 8 states...")
    cur.execute("TRUNCATE TABLE incentive_schemes RESTART IDENTITY;")

    count = 0
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            max_ben = None
            if row.get("maximum_benefit"):
                try:
                    max_ben = Decimal(row["maximum_benefit"])
                except Exception:
                    max_ben = None

            cur.execute("""
                INSERT INTO incentive_schemes (
                    policy_name, state_or_ut, gcc_type, incentive_category,
                    benefit_description, maximum_benefit, currency,
                    eligibility_criteria, policy_status, official_source_url, source_notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row["policy_name"],
                row["state_or_ut"],
                "Global Capability Center (GCC)",
                row["incentive_category"],
                row["benefit_description"],
                max_ben,
                row["currency"] or "INR",
                row["eligibility_criteria"] or None,
                row["policy_status"] or "Active",
                row["official_source_url"] or None,
                row["source_notes"] or "State GCC Policies, Colliers"
            ))
            count += 1

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Successfully imported {count} incentive scheme records into PostgreSQL!")
    print("=" * 70)

if __name__ == "__main__":
    import_incentives()
