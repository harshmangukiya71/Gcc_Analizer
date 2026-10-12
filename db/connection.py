import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))

_engine = None
_SessionLocal = None

def get_engine():
    """Returns or creates the singleton SQLAlchemy engine."""
    global _engine
    if _engine is not None:
        return _engine

    if not DATABASE_URL or "YOUR_PASSWORD_HERE" in DATABASE_URL:
        raise ValueError(
            "DATABASE_URL is not configured properly in .env. Please update your PostgreSQL password."
        )
    url = DATABASE_URL
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

    _engine = create_engine(
        url,
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT,
        pool_pre_ping=True,
    )
    return _engine

def get_session() -> Session:
    """Returns a new Session instance from the sessionmaker."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal()

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database sessions safely."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()
