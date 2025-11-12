"""
Simple API Tests for CMS
Run with: pytest tests/test_api.py
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

# Create test client
client = TestClient(app)

# Create fresh database for testing
@pytest.fixture(autouse=True)
def setup_database():
    """Create fresh database before each test"""
    Base.metadata.create_all(bind=engine)
    yield
    # Could drop tables here if needed
    # Base.metadata.drop_all(bind=engine)

# ===== BASIC ENDPOINT TESTS =====

def test_root_endpoint():
    """Test root endpoint returns welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "cms-api"

# ===== AUTHENTICATION TESTS =====

def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_username():
    """Test registering with duplicate username fails"""
    # Register first user
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "testpass123"
        }
    )
    
    # Try to register with same username
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser2",
            "email": "different@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 400

def test_login():
    """Test user login"""
    # First register a user
    client.post(
        "/api/auth/register",
        json={
            "username": "logintest",
            "email": "login@example.com",
            "password": "testpass123"
        }
    )
    
    # Then login
    response = client.post(
        "/api/auth/login",
        data={
            "username": "logintest",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with wrong password fails"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401

# ===== CATEGORY TESTS =====

def test_get_empty_categories():
    """Test getting categories when none exist"""
    response = client.get("/api/categories/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_category():
    """Test creating a category (requires auth)"""
    # Register and login
    client.post(
        "/api/auth/register",
        json={
            "username": "catuser",
            "email": "cat@example.com",
            "password": "testpass123"
        }
    )
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "catuser",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Create category
    response = client.post(
        "/api/categories/",
        json={
            "name": "Technology",
            "slug": "technology",
            "description": "Tech articles"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Technology"
    assert data["slug"] == "technology"

# ===== CONTENT TESTS =====

def test_get_empty_content():
    """Test getting content when none exists"""
    response = client.get("/api/content/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_content():
    """Test creating content (requires auth)"""
    # Register and login
    client.post(
        "/api/auth/register",
        json={
            "username": "contentuser",
            "email": "content@example.com",
            "password": "testpass123"
        }
    )
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "contentuser",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Create content
    response = client.post(
        "/api/content/",
        json={
            "title": "Test Post",
            "slug": "test-post",
            "content": "This is test content",
            "content_type": "post",
            "status": "published"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["slug"] == "test-post"
    assert data["views"] == 0

def test_content_requires_auth():
    """Test that creating content without auth fails"""
    response = client.post(
        "/api/content/",
        json={
            "title": "Test Post",
            "slug": "test-post",
            "content": "This is test content",
            "content_type": "post",
            "status": "published"
        }
    )
    assert response.status_code == 401

# ===== API DOCUMENTATION TESTS =====

def test_openapi_docs():
    """Test that OpenAPI documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_redoc_docs():
    """Test that ReDoc documentation is accessible"""
    response = client.get("/redoc")
    assert response.status_code == 200

# Run tests with: pytest tests/test_api.py -v

