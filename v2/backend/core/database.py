"""
Database configuration and session management.
Uses SQLAlchemy with async support and pgvector for embeddings.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from core.config import settings

# Handle both PostgreSQL and SQLite URLs
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine with connection pooling
engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    poolclass=NullPool if settings.DEBUG else None,
    pool_size=20 if not settings.DEBUG and "postgresql" in database_url else 5,
    max_overflow=10 if not settings.DEBUG and "postgresql" in database_url else 0,
    pool_pre_ping=True if "postgresql" in database_url else False,
    pool_recycle=3600 if "postgresql" in database_url else -1,
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()

async def init_db():
    """
    Initialize database:
    - Create all tables
    - Enable extensions (UUID, pgvector) if PostgreSQL
    """
    async with engine.begin() as conn:
        # Only enable extensions for PostgreSQL
        if "postgresql" in settings.DATABASE_URL:
            try:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            except Exception as e:
                print(f"Warning: Could not enable extensions: {e}")
        
        # Import all models to register them with Base
        try:
            from ..models import user, project, billing, community, knowledge
        except ImportError as e:
            print(f"Warning: Some models not imported: {e}")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database initialized successfully")


async def close_db():
    """
    Close database connections.
    Call on application shutdown.
    """
    await engine.dispose()
    print("✅ Database connections closed")

async def get_db():
    """
    Dependency for getting database session.
    Use with FastAPI Depends().
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

