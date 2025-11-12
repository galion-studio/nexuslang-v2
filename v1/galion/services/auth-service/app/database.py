"""
Database connection and session management.
Uses SQLAlchemy for ORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings

# Create database engine
# pool_pre_ping=True checks connection health before using
# pool_recycle=3600 recycles connections every hour
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Use in FastAPI endpoints like: db: Session = Depends(get_db)
    
    This ensures the session is properly closed after each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

