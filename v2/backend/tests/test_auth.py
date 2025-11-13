"""
Authentication Tests
Comprehensive tests for authentication system.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..main import app
from ..core.database import Base, get_db
from ..models.user import User

# Test database
TEST_DATABASE_URL = "postgresql://nexus:9k3mNp8rT2xQv5jL6wYz4cB1nF7dK0sA@localhost:5432/nexus_db_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_user(setup_database):
    """Test user registration."""
    response = client.post("/api/v2/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!@#"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"


def test_register_duplicate_email(setup_database):
    """Test registration with existing email."""
    # First registration
    client.post("/api/v2/auth/register", json={
        "email": "duplicate@example.com",
        "username": "user1",
        "password": "Password123!@#"
    })
    
    # Second registration with same email
    response = client.post("/api/v2/auth/register", json={
        "email": "duplicate@example.com",
        "username": "user2",
        "password": "Password123!@#"
    })
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login(setup_database):
    """Test user login."""
    # Register user first
    client.post("/api/v2/auth/register", json={
        "email": "login@example.com",
        "username": "loginuser",
        "password": "Login123!@#"
    })
    
    # Login
    response = client.post("/api/v2/auth/login", json={
        "email": "login@example.com",
        "password": "Login123!@#"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(setup_database):
    """Test login with wrong password."""
    response = client.post("/api/v2/auth/login", json={
        "email": "login@example.com",
        "password": "WrongPassword123!"
    })
    
    assert response.status_code == 401


def test_get_profile(setup_database):
    """Test getting user profile."""
    # Register and login
    response = client.post("/api/v2/auth/register", json={
        "email": "profile@example.com",
        "username": "profileuser",
        "password": "Profile123!@#"
    })
    
    token = response.json()["access_token"]
    
    # Get profile
    response = client.get("/api/v2/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile@example.com"
    assert data["credits"] == 100.0  # Default credits


def test_unauthorized_access(setup_database):
    """Test access without authentication."""
    response = client.get("/api/v2/auth/me")
    
    assert response.status_code == 403  # or 401
"""

