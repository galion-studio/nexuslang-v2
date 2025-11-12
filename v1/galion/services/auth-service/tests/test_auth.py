"""
Tests for authentication endpoints.
These tests verify registration, login, and token functionality.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """
    Test health check endpoint.
    This should always return 200 OK.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_register_success(client: TestClient):
    """
    Test successful user registration.
    Should create a new user and return user data.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123",
            "name": "Test User"
        }
    )
    
    # Check response
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user"]["email"] == "test@example.com"
    assert data["data"]["user"]["name"] == "Test User"
    assert data["data"]["user"]["role"] == "user"
    assert data["data"]["user"]["status"] == "active"
    
    # Make sure password is not in response
    assert "password" not in data["data"]["user"]
    assert "password_hash" not in data["data"]["user"]


def test_register_duplicate_email(client: TestClient):
    """
    Test registration with duplicate email.
    Should return 400 Bad Request.
    """
    # Register first user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123",
            "name": "Test User"
        }
    )
    
    # Try to register again with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "DifferentPassword456",
            "name": "Another User"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_invalid_email(client: TestClient):
    """
    Test registration with invalid email format.
    Pydantic should catch this and return 422.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "SecurePassword123",
            "name": "Test User"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_register_short_password(client: TestClient):
    """
    Test registration with password that's too short.
    Should return 422 validation error.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "short",  # Less than 8 characters
            "name": "Test User"
        }
    )
    
    assert response.status_code == 422


def test_login_success(client: TestClient):
    """
    Test successful login.
    Should return JWT token and user data.
    """
    # First, register a user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123",
            "name": "Test User"
        }
    )
    
    # Then login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # Check token is present
    assert "token" in data["data"]
    assert isinstance(data["data"]["token"], str)
    assert len(data["data"]["token"]) > 0
    
    # Check expiration info
    assert "expires_in" in data["data"]
    assert data["data"]["expires_in"] == 3600  # 1 hour
    
    # Check user data
    assert data["data"]["user"]["email"] == "test@example.com"


def test_login_invalid_email(client: TestClient):
    """
    Test login with email that doesn't exist.
    Should return 401 Unauthorized.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "SomePassword123"
        }
    )
    
    assert response.status_code == 401
    assert "invalid credentials" in response.json()["detail"].lower()


def test_login_wrong_password(client: TestClient):
    """
    Test login with correct email but wrong password.
    Should return 401 Unauthorized.
    """
    # Register a user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123",
            "name": "Test User"
        }
    )
    
    # Try to login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword456"
        }
    )
    
    assert response.status_code == 401
    assert "invalid credentials" in response.json()["detail"].lower()


def test_protected_endpoint_with_token(client: TestClient):
    """
    Test accessing protected endpoint with valid token.
    Should return user data.
    """
    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123",
            "name": "Test User"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123"
        }
    )
    token = login_response.json()["data"]["token"]
    
    # Access protected endpoint with token
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "test@example.com"
    assert data["data"]["name"] == "Test User"


def test_protected_endpoint_without_token(client: TestClient):
    """
    Test accessing protected endpoint without token.
    Should return 403 Forbidden (FastAPI's default for missing auth).
    """
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403


def test_protected_endpoint_with_invalid_token(client: TestClient):
    """
    Test accessing protected endpoint with invalid token.
    Should return 401 Unauthorized.
    """
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token-here"}
    )
    assert response.status_code == 401


def test_password_hashing(client: TestClient):
    """
    Test that passwords are properly hashed and not stored in plain text.
    This is a security-critical test.
    """
    password = "SecurePassword123"
    
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": password,
            "name": "Test User"
        }
    )
    
    # Login should work with correct password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": password
        }
    )
    assert response.status_code == 200
    
    # Login should fail with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword456"
        }
    )
    assert response.status_code == 401


def test_user_role_defaults_to_user(client: TestClient):
    """
    Test that new users get 'user' role by default.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123",
            "name": "Test User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["user"]["role"] == "user"


def test_user_status_defaults_to_active(client: TestClient):
    """
    Test that new users get 'active' status by default.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123",
            "name": "Test User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["user"]["status"] == "active"

