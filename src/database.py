"""
Backward-compatibility bridge for src.database -> db.connection
"""
from db.connection import get_engine, get_session, get_db

__all__ = ["get_engine", "get_session", "get_db"]
