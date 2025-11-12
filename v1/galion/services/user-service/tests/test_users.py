"""
Tests for user management endpoints.
"""

import pytest
from fastapi import status


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Health check should return 200 and service info."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data


class TestGetMyProfile:
    """Test getting current user's profile."""
    
    def test_get_my_profile_success(self, client, test_user, auth_headers):
        """Authenticated user should be able to get their profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["role"] == test_user.role
    
    def test_get_my_profile_unauthorized(self, client):
        """Request without token should fail."""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateMyProfile:
    """Test updating current user's profile."""
    
    def test_update_profile_success(self, client, test_user, auth_headers):
        """User should be able to update their profile."""
        update_data = {
            "name": "Updated Name",
            "bio": "This is my bio",
            "avatar_url": "https://example.com/avatar.jpg"
        }
        
        response = client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["bio"] == "This is my bio"
        assert data["avatar_url"] == "https://example.com/avatar.jpg"
    
    def test_update_profile_partial(self, client, test_user, auth_headers):
        """Should be able to update only some fields."""
        update_data = {
            "bio": "New bio only"
        }
        
        response = client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["bio"] == "New bio only"
        assert data["name"] == test_user.name  # Unchanged
    
    def test_update_profile_unauthorized(self, client):
        """Request without token should fail."""
        update_data = {"name": "Hacker"}
        
        response = client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetUserById:
    """Test getting user by ID."""
    
    def test_get_user_by_id_success(self, client, test_user, auth_headers):
        """Should be able to get any user by ID."""
        response = client.get(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
    
    def test_get_user_by_id_not_found(self, client, auth_headers):
        """Should return 404 for non-existent user."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = client.get(
            f"/api/v1/users/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestListUsers:
    """Test listing all users."""
    
    def test_list_users_success(self, client, test_user, auth_headers, db):
        """Should return paginated list of users."""
        # Create additional test users
        from app.models.user import User
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        for i in range(5):
            user = User(
                email=f"user{i}@example.com",
                password_hash=pwd_context.hash("password"),
                name=f"User {i}",
                role="user",
                is_active=True
            )
            db.add(user)
        db.commit()
        
        # Get first page
        response = client.get(
            "/api/v1/users/?limit=3&offset=0",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["users"]) == 3
        assert data["total"] == 6  # 5 new + 1 test_user
        assert data["limit"] == 3
        assert data["offset"] == 0


class TestSearchUsers:
    """Test user search."""
    
    def test_search_by_name(self, client, test_user, auth_headers, db):
        """Should be able to search users by name."""
        # Create additional users
        from app.models.user import User
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        users_data = [
            ("john@example.com", "John Doe"),
            ("jane@example.com", "Jane Smith"),
            ("johnny@example.com", "Johnny Walker"),
        ]
        
        for email, name in users_data:
            user = User(
                email=email,
                password_hash=pwd_context.hash("password"),
                name=name,
                role="user",
                is_active=True
            )
            db.add(user)
        db.commit()
        
        # Search for "john"
        search_data = {
            "query": "john",
            "limit": 10,
            "offset": 0
        }
        
        response = client.post(
            "/api/v1/users/search",
            json=search_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 2  # Should find "John" and "Johnny"
    
    def test_search_by_role(self, client, test_user, admin_user, auth_headers):
        """Should be able to filter by role."""
        search_data = {
            "role": "admin",
            "limit": 10,
            "offset": 0
        }
        
        response = client.post(
            "/api/v1/users/search",
            json=search_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["users"][0]["role"] == "admin"


class TestAdminOperations:
    """Test admin-only operations."""
    
    def test_deactivate_user_as_admin(self, client, test_user, admin_headers):
        """Admin should be able to deactivate users."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/deactivate",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is False
    
    def test_deactivate_user_as_regular_user(self, client, admin_user, auth_headers):
        """Regular user should NOT be able to deactivate users."""
        response = client.put(
            f"/api/v1/users/{admin_user.id}/deactivate",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_activate_user_as_admin(self, client, test_user, admin_headers, db):
        """Admin should be able to activate users."""
        # First deactivate the user
        test_user.is_active = False
        db.commit()
        
        # Then activate
        response = client.put(
            f"/api/v1/users/{test_user.id}/activate",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is True
    
    def test_admin_cannot_deactivate_self(self, client, admin_user, admin_headers):
        """Admin should not be able to deactivate their own account."""
        response = client.put(
            f"/api/v1/users/{admin_user.id}/deactivate",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

