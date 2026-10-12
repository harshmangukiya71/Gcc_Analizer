from typing import Tuple, Optional

# The 8 supported focus markets
SUPPORTED_CITIES = {
    "Bengaluru",
    "Hyderabad",
    "Pune",
    "Mumbai",
    "Delhi NCR",
    "Chennai",
    "Kolkata",
    "Ahmedabad",
}

# Normalization mapping for common variations and aliases
CITY_NORMALIZATION_MAP = {
    # Bengaluru variations
    "bengaluru": "Bengaluru",
    "bangalore": "Bengaluru",
    "blr": "Bengaluru",
    # Hyderabad variations
    "hyderabad": "Hyderabad",
    "hyd": "Hyderabad",
    # Pune variations
    "pune": "Pune",
    # Mumbai variations
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
    "navi mumbai": "Mumbai",
    "thane": "Mumbai",
    # Delhi NCR variations
    "delhi ncr": "Delhi NCR",
    "delhi": "Delhi NCR",
    "new delhi": "Delhi NCR",
    "gurgaon": "Delhi NCR",
    "gurugram": "Delhi NCR",
    "noida": "Delhi NCR",
    "greater noida": "Delhi NCR",
    "faridabad": "Delhi NCR",
    "ghaziabad": "Delhi NCR",
    # Chennai variations
    "chennai": "Chennai",
    "madras": "Chennai",
    # Kolkata variations
    "kolkata": "Kolkata",
    "calcutta": "Kolkata",
    # Ahmedabad variations
    "ahmedabad": "Ahmedabad",
    "amdavad": "Ahmedabad",
    "gandhinagar": "Ahmedabad",
}

def normalize_city(raw_city: Optional[str]) -> Tuple[str, Optional[str]]:
    """
    Normalizes a city string to the canonical market name.
    
    Returns:
        (normalized_city, raw_city_if_different)
        - normalized_city: The canonical market name (or title-cased emerging market name)
        - raw_city_if_different: The exact raw source value if it differed from the normalized name, else None.
    """
    clean_raw = (raw_city or "").strip()
    if not clean_raw:
        return "", None

    key = clean_raw.lower()
    if key in CITY_NORMALIZATION_MAP:
        canonical = CITY_NORMALIZATION_MAP[key]
        raw_if_diff = clean_raw if clean_raw != canonical else None
        return canonical, raw_if_diff

    # For other emerging cities outside the 8 focus markets (e.g. Coimbatore, Jaipur, Kochi)
    title_cased = clean_raw.title()
    raw_if_diff = clean_raw if clean_raw != title_cased else None
    return title_cased, raw_if_diff
