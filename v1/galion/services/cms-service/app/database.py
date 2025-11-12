"""
Database Configuration for CMS
Simple SQLite setup for easy deployment and testing
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database file location
# This creates a local database file - no complex setup needed
DATABASE_URL = "sqlite:///./cms.db"

# Create the SQLite engine
# check_same_thread=False is needed for SQLite with FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session factory for database connections
# Each request will get its own database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models
Base = declarative_base()

# Dependency to get database session for each request
# This automatically handles opening and closing database connections
def get_db():
    """
    Generator that provides a database session
    Automatically closes the session when done
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

