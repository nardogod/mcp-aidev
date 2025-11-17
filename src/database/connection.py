"""
Database connection management for MCP-AIDev
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from .models import Base

# Global engine and session factory
_engine = None
_SessionLocal = None


def init_db(database_url: str = None) -> None:
    """
    Initialize database connection and create tables.
    
    Args:
        database_url: SQLite database URL. Defaults to env variable or local file.
    """
    global _engine, _SessionLocal
    
    if database_url is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./data/mcp_aidev.db")
    
    # Special handling for in-memory database (testing)
    if database_url == ":memory:" or "mode=memory" in database_url:
        _engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        # Ensure directory exists for SQLite file
        if database_url.startswith("sqlite:///"):
            db_path = database_url.replace("sqlite:///", "")
            if db_path.startswith("./"):
                db_path = db_path[2:]
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
        
        _engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
        )
    
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    
    # Create all tables
    Base.metadata.create_all(bind=_engine)


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Yields:
        Database session that auto-closes after use.
    """
    if _SessionLocal is None:
        init_db()
    
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def clear_db() -> None:
    """
    Clear all data from database (for testing).
    """
    global _engine
    if _engine is not None:
        Base.metadata.drop_all(bind=_engine)
        Base.metadata.create_all(bind=_engine)
