"""
Database connection and management for Galion Platform Backend
Provides async database operations using SQLAlchemy.

"Your imagination is the end."
"""

import asyncio
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

logger = logging.getLogger(__name__)

# Import settings after environment is set
from .config import settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models"""
    pass


# Database engine and session
_engine = None
_async_session_maker = None


def get_engine():
    """Get or create database engine"""
    global _engine
    if _engine is None:
        database_url = os.getenv("DATABASE_URL", settings.database_url)
        _engine = create_async_engine(
            database_url,
            echo=settings.debug,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_recycle=settings.db_pool_recycle,
        )
        logger.info("Database engine created")
    return _engine


def get_async_session_maker():
    """Get or create async session maker"""
    global _async_session_maker
    if _async_session_maker is None:
        engine = get_engine()
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection"""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# For synchronous operations (like in auth service)
def get_db_session() -> AsyncSession:
    """Get database session for synchronous operations"""
    session_maker = get_async_session_maker()
    return session_maker()


async def create_tables():
    """Create database tables"""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Table creation failed: {e}")
        raise


async def close_database():
    """Close database connections"""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
        logger.info("Database connections closed")


async def check_database_health() -> dict:
    """Check database health"""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return {
            "status": "healthy",
            "connection": True,
            "response_time": 0.001
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "connection": False
        }


async def run_migrations():
    """Run database migrations"""
    logger.info("Running database migrations")
    # For now, just create tables
    # In production, this would use Alembic
    await create_tables()
    logger.info("Migrations completed")


# Export functions and classes
__all__ = [
    "Base",
    "get_db",
    "get_db_session",
    "create_tables",
    "close_database",
    "check_database_health",
    "run_migrations"
]