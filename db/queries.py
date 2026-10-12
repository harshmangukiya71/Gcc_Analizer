from typing import List, Dict, Any, Optional
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

try:
    from db.models.gcc_registry import GCCRegistry
    from db.models.talent_salary import TalentSalaryBenchmark
    from db.models.office_market import OfficeMarketMetric
    from db.models.incentive_schemes import IncentiveScheme
    from db.models.expansion_events import GCCExpansionEvent
except ImportError:
    from src.models.gcc_registry import GCCRegistry
    from src.models.talent_salary import TalentSalaryBenchmark
    from src.models.office_market import OfficeMarketMetric
    from src.models.incentive_schemes import IncentiveScheme
    from src.models.expansion_events import GCCExpansionEvent

# =============================================================================
# GCC REGISTRY QUERIES
# =============================================================================

def list_gccs_filtered(
    session: Session,
    city: Optional[str] = None,
    sector: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[GCCRegistry]:
    """List GCCs filtered by city, sector, and search keyword without joins."""
    stmt = select(GCCRegistry)
    if city:
        stmt = stmt.where(GCCRegistry.city == city)
    if sector:
        stmt = stmt.where(GCCRegistry.sector == sector)
    if keyword:
        pattern = f"%{keyword}%"
        stmt = stmt.where(
            or_(
                GCCRegistry.company_name.ilike(pattern),
                GCCRegistry.gcc_notes.ilike(pattern),
                GCCRegistry.key_roles_hired.ilike(pattern),
            )
        )
    stmt = stmt.order_by(GCCRegistry.company_name).limit(limit).offset(offset)
    return list(session.scalars(stmt).all())

def count_gccs_by_city(session: Session) -> List[Dict[str, Any]]:
    """Count GCCs grouped by city."""
    stmt = (
        select(GCCRegistry.city, func.count(GCCRegistry.id).label("count"))
        .group_by(GCCRegistry.city)
        .order_by(func.count(GCCRegistry.id).desc())
    )
    return [{"city": r[0], "count": r[1]} for r in session.execute(stmt).all()]

def count_gccs_by_sector(session: Session) -> List[Dict[str, Any]]:
    """Count GCCs grouped by sector."""
    stmt = (
        select(GCCRegistry.sector, func.count(GCCRegistry.id).label("count"))
        .group_by(GCCRegistry.sector)
        .order_by(func.count(GCCRegistry.id).desc())
    )
    return [{"sector": r[0], "count": r[1]} for r in session.execute(stmt).all()]

# =============================================================================
# TALENT SALARY BENCHMARK QUERIES
# =============================================================================

def get_salary_benchmark_range(
    session: Session,
    job_title: str,
    city: Optional[str] = None,
    seniority: Optional[str] = None
) -> Optional[TalentSalaryBenchmark]:
    """Get salary benchmark range for a job title in a given market."""
    stmt = select(TalentSalaryBenchmark).where(
        TalentSalaryBenchmark.job_title.ilike(f"%{job_title}%")
    )
    if city:
        stmt = stmt.where(TalentSalaryBenchmark.city == city)
    if seniority:
        stmt = stmt.where(TalentSalaryBenchmark.seniority_level.ilike(f"%{seniority}%"))
    return session.scalars(stmt).first()

# =============================================================================
# OFFICE MARKET RENT QUERIES
# =============================================================================

def get_office_rents(
    session: Session,
    city: Optional[str] = None,
    rent_level: Optional[str] = None
) -> List[OfficeMarketMetric]:
    """Query office rent benchmarks with optional city and level filters."""
    stmt = select(OfficeMarketMetric)
    if city and city.lower() != "all":
        stmt = stmt.where(OfficeMarketMetric.city == city)
    if rent_level and rent_level.lower() != "all":
        stmt = stmt.where(OfficeMarketMetric.rent_level == rent_level)
    stmt = stmt.order_by(OfficeMarketMetric.city, OfficeMarketMetric.micro_market)
    return list(session.scalars(stmt).all())

# =============================================================================
# INCENTIVE SCHEMES QUERIES
# =============================================================================

def get_incentives(
    session: Session,
    state: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
) -> List[IncentiveScheme]:
    """Query state government incentive schemes with multi-criteria filtering."""
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
                IncentiveScheme.eligibility_criteria.ilike(kw)
            )
        )
    stmt = stmt.order_by(IncentiveScheme.state_or_ut.asc(), IncentiveScheme.id.asc())
    return list(session.scalars(stmt).all())
