"""
Database connection and session management.
Uses SQLAlchemy ORM with PostgreSQL database.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings


# Create database engine
# echo=True shows SQL queries in console (useful for debugging)
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,  # Connection pool size
    max_overflow=10,  # Maximum overflow connections
    pool_pre_ping=True,  # Test connections before using
)

# Session factory - creates new database sessions
SessionLocal = sessionmaker(
    autocommit=False,  # Manual transaction control
    autoflush=False,  # Manual flush control
    bind=engine
)

# Base class for all database models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    
    The session is automatically closed after the request completes.
    If an exception occurs, the transaction is rolled back.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

