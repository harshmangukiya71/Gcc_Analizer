"""
Backward-compatibility bridge for src.normalizers -> backend.core.normalizers
"""
from backend.core.normalizers import normalize_city, SUPPORTED_CITIES, CITY_NORMALIZATION_MAP

__all__ = ["normalize_city", "SUPPORTED_CITIES", "CITY_NORMALIZATION_MAP"]
