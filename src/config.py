"""
Backward-compatibility bridge for src.config -> backend.core.config
"""
from backend.core.config import settings, Settings

__all__ = ["settings", "Settings"]
