"""
Test configuration and fixtures.
Shared test setup that can be used across all test files.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt
from datetime import datetime, timedelta

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.models.user import User


# Use in-memory SQLite for testing (fast and isolated)
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test database engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create session factory for tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database for each test.
    
    This ensures tests are isolated and don't affect each other.
    After each test, all data is cleared.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client for making HTTP requests.
    
    Override the get_db dependency to use our test database.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """
    Create a test user in the database.
    
    Returns a User object that can be used in tests.
    """
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        email="test@example.com",
        password_hash=pwd_context.hash("testpassword123"),
        name="Test User",
        role="user",
        email_verified=True,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@pytest.fixture
def admin_user(db):
    """
    Create a test admin user in the database.
    """
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        email="admin@example.com",
        password_hash=pwd_context.hash("adminpassword123"),
        name="Admin User",
        role="admin",
        email_verified=True,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@pytest.fixture
def test_token(test_user):
    """
    Create a valid JWT token for the test user.
    
    This token can be used to authenticate requests in tests.
    """
    payload = {
        "sub": test_user.email,
        "exp": datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return token


@pytest.fixture
def admin_token(admin_user):
    """
    Create a valid JWT token for the admin user.
    """
    payload = {
        "sub": admin_user.email,
        "exp": datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return token


@pytest.fixture
def auth_headers(test_token):
    """
    Create authorization headers with valid token.
    
    Usage in tests:
        response = client.get("/api/v1/users/me", headers=auth_headers)
    """
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture
def admin_headers(admin_token):
    """
    Create authorization headers with admin token.
    """
    return {"Authorization": f"Bearer {admin_token}"}

