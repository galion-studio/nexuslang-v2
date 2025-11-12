"""
Pytest configuration and fixtures for security tests.
"""

import pytest
import asyncio
import os
from typing import AsyncGenerator

# Set test environment variables
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only-min-32-chars-long-abcdef"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # Use DB 15 for tests

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import after setting env vars
from main import app
from core.database import Base, get_db
from core.redis_client import get_redis, close_redis


# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test database fixture
@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    Creates tables before test, drops after.
    """
    # Create test engine
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


# Test client fixture
@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with dependency overrides."""
    def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# Redis fixture
@pytest.fixture(scope="function")
async def test_redis():
    """Get test Redis client."""
    redis = await get_redis()
    
    # Clear test DB before test
    if redis.is_connected:
        await redis.redis.flushdb()
    
    yield redis
    
    # Clear test DB after test
    if redis.is_connected:
        await redis.redis.flushdb()


# Cleanup fixture
@pytest.fixture(scope="session", autouse=True)
async def cleanup():
    """Cleanup after all tests."""
    yield
    await close_redis()
    
    # Remove test database
    if os.path.exists("./test.db"):
        os.remove("./test.db")
