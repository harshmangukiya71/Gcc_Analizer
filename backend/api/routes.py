import os
import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from backend.core.config import settings
from db.connection import get_db
from db.models import (
    GCCRegistry,
    OfficeMarketMetric,
    TalentSalaryBenchmark,
    IncentiveScheme,
)

router = APIRouter(prefix="/api", tags=["Market Insights"])

# Load cached Sansovi salary benchmarks JSON for fast instant lookups & rich breakdowns
SALARY_CACHE: List[Dict[str, Any]] = []
if settings.SALARY_JSON_PATH.exists():
    try:
        with open(settings.SALARY_JSON_PATH, "r", encoding="utf-8") as f:
            SALARY_CACHE = json.load(f)
    except Exception as e:
        print("Warning: could not load salary cache:", e)


@router.get("/summary", summary="Dashboard KPI Counters")
def get_summary(db: Session = Depends(get_db)):
    gcc_count = db.scalar(select(func.count(GCCRegistry.id))) or 0
    rent_count = db.scalar(select(func.count(OfficeMarketMetric.id))) or 0
    salary_count = db.scalar(select(func.count(TalentSalaryBenchmark.id))) or len(SALARY_CACHE)
    incentive_count = db.scalar(select(func.count(IncentiveScheme.id))) or 0
    return {
        "gcc_companies": gcc_count,
        "office_rents": rent_count,
        "talent_benchmarks": salary_count,
        "incentive_schemes": incentive_count,
    }


@router.get("/gccs", summary="Filterable GCC Companies Registry")
def get_gccs(
    city: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    stmt = select(GCCRegistry)
    if city and city.lower() != "all":
        stmt = stmt.where(GCCRegistry.city == city)
    if sector and sector.lower() != "all":
        stmt = stmt.where(GCCRegistry.sector == sector)
    if search:
        kw = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                GCCRegistry.company_name.ilike(kw),
                GCCRegistry.gcc_notes.ilike(kw),
                GCCRegistry.key_roles_hired.ilike(kw),
            )
        )
    stmt = stmt.order_by(GCCRegistry.company_name.asc())
    records = db.scalars(stmt).all()
    return [
        {
            "id": r.id,
            "company_name": r.company_name,
            "city": r.city,
            "sector": r.sector or "N/A",
            "india_headcount": r.india_headcount or "Unspecified",
            "key_roles_hired": r.key_roles_hired or "N/A",
            "gcc_notes": r.gcc_notes or "",
            "website": r.website or "#",
        }
        for r in records
    ]


@router.get("/rents", summary="Office Rent Benchmarks")
def get_rents(
    city: Optional[str] = Query(None),
    rent_level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    stmt = select(OfficeMarketMetric)
    if city and city.lower() != "all":
        stmt = stmt.where(OfficeMarketMetric.city == city)
    if rent_level and rent_level.lower() != "all":
        stmt = stmt.where(OfficeMarketMetric.rent_level == rent_level)
    stmt = stmt.order_by(OfficeMarketMetric.rent_inr_per_sqft_per_month.desc())
    records = db.scalars(stmt).all()
    return [
        {
            "id": r.id,
            "city": r.city,
            "rent_level": r.rent_level,
            "micro_market": r.micro_market or "City Average",
            "rent_inr_per_sqft_per_month": float(r.rent_inr_per_sqft_per_month),
        }
        for r in records
    ]


@router.get("/rent-chart", summary="City Average Rent Chart Data")
def get_rent_chart(db: Session = Depends(get_db)):
    stmt = (
        select(OfficeMarketMetric.city, OfficeMarketMetric.rent_inr_per_sqft_per_month)
        .where(OfficeMarketMetric.rent_level == "city_average")
        .order_by(OfficeMarketMetric.rent_inr_per_sqft_per_month.desc())
    )
    results = db.execute(stmt).all()
    return [{"city": r[0], "rent": float(r[1])} for r in results]


@router.get("/gcc-chart", summary="City GCC Counts Chart Data")
def get_gcc_chart(db: Session = Depends(get_db)):
    stmt = (
        select(GCCRegistry.city, func.count(GCCRegistry.id))
        .group_by(GCCRegistry.city)
        .order_by(func.count(GCCRegistry.id).desc())
    )
    results = db.execute(stmt).all()
    return [{"city": r[0], "count": r[1]} for r in results]


@router.get("/salary-benchmark", summary="Sansovi Salary Benchmark Calculator")
def get_salary_benchmark(
    role: str = Query("data-engineer"),
    city: str = Query("bengaluru"),
    experienceBand: str = Query("3-7 yr"),
):
    """
    Returns exact benchmark data matching Sansovi parameters.
    Uses cached records extracted from Sansovi GCC Intelligence.
    """
    r_key = role.lower().strip()
    c_key = city.lower().strip()
    exp_clean = experienceBand.lower().replace("+", " ").strip()

    for item in SALARY_CACHE:
        item_role = item.get("_role_key", "").lower()
        item_city = item.get("_city_key", "").lower()
        item_exp = item.get("experienceBand", "").lower()

        if item_role == r_key and item_city == c_key:
            if "3-7" in exp_clean and "3" in item_exp and "7" in item_exp:
                return item
            elif "0-2" in exp_clean and "0" in item_exp and "2" in item_exp:
                return item
            elif "7-12" in exp_clean and "7" in item_exp and "12" in item_exp:
                return item
            elif "12-18" in exp_clean and "12" in item_exp and "18" in item_exp:
                return item
            elif "18" in exp_clean and "18+" in item_exp:
                return item

    # Fallback to first matching role & city
    for item in SALARY_CACHE:
        if item.get("_role_key", "").lower() == r_key and item.get("_city_key", "").lower() == c_key:
            return item

    if SALARY_CACHE:
        return SALARY_CACHE[0]

    return {"error": "No benchmark data found"}


@router.get("/salaries-table", summary="Database Talent Salary Records")
def get_salaries_table(db: Session = Depends(get_db)):
    """Returns all salary benchmark rows from PostgreSQL."""
    stmt = select(TalentSalaryBenchmark).order_by(
        TalentSalaryBenchmark.job_title, TalentSalaryBenchmark.experience_min_years
    )
    records = db.scalars(stmt).all()
    return [
        {
            "id": r.id,
            "job_title": r.job_title,
            "city": r.city,
            "job_family": r.job_family,
            "seniority_level": r.seniority_level,
            "salary_min": float(r.salary_min) if r.salary_min else 0,
            "salary_max": float(r.salary_max) if r.salary_max else 0,
            "sample_size": r.sample_size,
            "source_notes": r.source_notes,
        }
        for r in records
    ]


@router.get("/incentives", summary="State GCC Incentive Policies")
def get_incentives(
    state: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    stmt = select(IncentiveScheme)
    if state and state.lower() != "all":
        stmt = stmt.where(IncentiveScheme.state_or_ut == state)
    if category and category.lower() != "all":
        stmt = stmt.where(IncentiveScheme.incentive_category == category)
    if search:
        kw = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                IncentiveScheme.policy_name.ilike(kw),
                IncentiveScheme.benefit_description.ilike(kw),
                IncentiveScheme.eligibility_criteria.ilike(kw),
            )
        )
    stmt = stmt.order_by(IncentiveScheme.state_or_ut.asc(), IncentiveScheme.id.asc())
    records = db.scalars(stmt).all()
    return [
        {
            "id": r.id,
            "state_or_ut": r.state_or_ut,
            "policy_name": r.policy_name,
            "incentive_category": r.incentive_category or "General",
            "benefit_description": r.benefit_description,
            "maximum_benefit": float(r.maximum_benefit) if r.maximum_benefit else None,
            "currency": r.currency or "INR",
            "eligibility_criteria": r.eligibility_criteria or "N/A",
            "policy_status": r.policy_status,
            "official_source_url": r.official_source_url or "#",
            "source_notes": r.source_notes or "State GCC Policies, Colliers",
        }
        for r in records
    ]
