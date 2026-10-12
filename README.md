# GCC Compass — India Market Insights Platform

Enterprise-grade PostgreSQL Database, Data Ingestion Pipeline & Full-Stack Analytics Dashboard for Global Capability Centers (GCCs) in India.

---

## 1. Enterprise Architecture Overview

The repository is structured following modern software engineering principles, featuring strict separation of concerns across presentation (**`frontend/`**), business logic (**`backend/`**), data persistence (**`db/`**), and ingestion automation (**`scripts/`**):

```text
Gcc_Analizer/
├── frontend/                               # Dedicated Presentation Layer
│   ├── css/
│   │   └── styles.css                      # Custom theme, range track & badge styles
│   ├── js/
│   │   └── app.js                          # Client-side reactivity, Chart.js & data fetching
│   ├── assets/                             # Logos, branding & UI static assets
│   └── index.html                          # Semantic dashboard UI (Tailwind CSS + Chart.js)
│
├── backend/                                # Enterprise Application Layer (FastAPI)
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                       # Modular RESTful API route definitions
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                       # Environment settings & Pathlib configuration
│   │   └── normalizers.py                  # City canonicalization & alias handling
│   ├── main.py                             # FastAPI server setup, static file mounting & CORS
│   └── __init__.py
│
├── db/                                     # Database Persistence & Schema Layer
│   ├── models/                             # SQLAlchemy 2.0 Declarative ORM Models
│   │   ├── __init__.py                     # Clean package exports
│   │   ├── base.py                         # DeclarativeBase definition
│   │   ├── gcc_registry.py                 # Table 1: GCC Master Registry
│   │   ├── talent_salary.py                # Table 2: Salary Benchmarks
│   │   ├── office_market.py                # Table 3: Office Market Metrics
│   │   ├── incentive_schemes.py            # Table 4: Government Incentive Schemes
│   │   └── expansion_events.py             # Table 5: GCC Expansion Events
│   ├── schema/
│   │   └── schema.sql                      # Production PostgreSQL DDL (DDL + Indexes + Constraints)
│   ├── connection.py                       # Connection pooling, sessionmaker & get_db dependency
│   ├── queries.py                          # High-performance zero-join database queries
│   └── __init__.py
│
├── alembic/                                # Database Migration Management
│   ├── versions/                           # Versioned migration revisions
│   └── env.py                              # Alembic migration runner
│
├── data/                                   # Offline Bundled Datasets
│   └── raw/
│       ├── GCC-Journal-India-List.csv               # 274 master GCC records
│       ├── GCC_Office_Rents_City_and_MicroMarket.csv# 64 office rent records (7 cities + 57 micro-markets)
│       ├── sansovi_salary_benchmarks.csv            # 330 talent salary records (11 roles, 6 cities, 5 exp bands)
│       ├── sansovi_salary_benchmarks.json           # Full nested benchmarks with vertical & city indexes
│       └── state_gcc_incentive_policies.csv         # 43 state incentive policies across 8 Indian states
│
├── scripts/                                # Ingestion Pipelines & Verification CLI
│   ├── import_all_data.py                  # Master loader for all 4 datasets
│   ├── import_gcc_data.py                  # Batch upsert pipeline for GCC registry
│   ├── import_office_rents.py              # Transactional upsert for office rent data
│   ├── import_salary_benchmarks.py         # Transactional upsert for talent salary data
│   ├── import_incentives.py                # Transactional upsert for state incentive policies
│   ├── verify_data.py                      # Data validation audit
│   └── verify_office_rents.py              # Office metrics integrity audit
│
├── tests/                                  # Pytest Test Suite
│   └── test_office_rents.py                # Data integrity and schema verification tests
│
├── run.py                                  # Primary Application Entry Point (`python run.py`)
├── app.py                                  # Backward-Compatible Runner (`python app.py`)
├── requirements.txt                        # Project dependencies
├── alembic.ini                             # Alembic configuration
└── .env.example                            # Environment variables template
```

---

## 2. Quick Start Guide

### Step 1: Configure Environment Variables
Copy `.env.example` to `.env` and specify your PostgreSQL credentials:
```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/gcc_compass
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Populate PostgreSQL Database
Run the master ingestion script:
```bash
python scripts/import_all_data.py
```

### Step 4: Run the Application
Start the dashboard using either entry point:
```bash
python run.py
# or
python app.py
```

Then open your browser at:
- **Interactive Dashboard:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 3. Key Design Decisions

1. **Separation of Concerns**: The frontend is no longer embedded inside Python strings. HTML, CSS, and JavaScript are isolated in `frontend/`, enabling independent UI development, caching, and maintenance.
2. **Dedicated `db/` Layer**: All ORM models reside in `db/models/`, raw DDL and migrations in `db/schema/`, and connection lifecycle management in `db/connection.py`.
3. **Modular API Endpoints**: Endpoints are grouped logically in `backend/api/routes.py` with typed query parameters and automatic OpenAPI generation.
4. **Backward Compatibility**: `src/` functions as an import proxy, ensuring existing scripts (`scripts/import_*.py`, `alembic/`) and external automations run without breaking changes.
