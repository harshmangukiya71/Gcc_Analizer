"""
Backward-compatibility bridge for src.models -> db.models
"""
from db.models import (
    Base,
    GCCRegistry,
    TalentSalaryBenchmark,
    OfficeMarketMetric,
    IncentiveScheme,
    GCCExpansionEvent,
)

__all__ = [
    "Base",
    "GCCRegistry",
    "TalentSalaryBenchmark",
    "OfficeMarketMetric",
    "IncentiveScheme",
    "GCCExpansionEvent",
]
