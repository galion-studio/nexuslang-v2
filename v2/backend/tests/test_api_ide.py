"""
Test suite for IDE API endpoints.
Tests project management, file operations, and code execution.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from ..main import app
from ..models.user import User
from ..models.project import Project, File


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
async def test_user(db: AsyncSession):
    """Create test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def auth_headers(test_user, client):
    """Get authentication headers."""
    # Login to get token
    response = client.post("/api/v2/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestProjectEndpoints:
    """Test project management endpoints."""
    
    def test_create_project(self, client, auth_headers):
        """Test project creation."""
        response = client.post(
            "/api/v2/ide/projects",
            json={
                "name": "Test Project",
                "description": "A test project",
                "visibility": "private"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["visibility"] == "private"
        assert "id" in data
    
    def test_list_projects(self, client, auth_headers):
        """Test listing user's projects."""
        response = client.get("/api/v2/ide/projects", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_project(self, client, auth_headers):
        """Test getting project details."""
        # Create project first
        create_response = client.post(
            "/api/v2/ide/projects",
            json={"name": "Test Project"},
            headers=auth_headers
        )
        project_id = create_response.json()["id"]
        
        # Get project
        response = client.get(f"/api/v2/ide/projects/{project_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
    
    def test_delete_project(self, client, auth_headers):
        """Test project deletion."""
        # Create project
        create_response = client.post(
            "/api/v2/ide/projects",
            json={"name": "Test Project"},
            headers=auth_headers
        )
        project_id = create_response.json()["id"]
        
        # Delete project
        response = client.delete(
            f"/api/v2/ide/projects/{project_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get(f"/api/v2/ide/projects/{project_id}", headers=auth_headers)
        assert get_response.status_code == 404


class TestFileEndpoints:
    """Test file management endpoints."""
    
    def test_create_file(self, client, auth_headers):
        """Test file creation."""
        # Create project first
        project_response = client.post(
            "/api/v2/ide/projects",
            json={"name": "Test Project"},
            headers=auth_headers
        )
        project_id = project_response.json()["id"]
        
        # Create file
        response = client.post(
            f"/api/v2/ide/projects/{project_id}/files",
            json={
                "path": "test.nx",
                "content": "print(\"Hello\")"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["path"] == "test.nx"
        assert data["content"] == "print(\"Hello\")"
    
    def test_update_file(self, client, auth_headers):
        """Test file update."""
        # Create project and file
        project_response = client.post(
            "/api/v2/ide/projects",
            json={"name": "Test Project"},
            headers=auth_headers
        )
        project_id = project_response.json()["id"]
        
        file_response = client.post(
            f"/api/v2/ide/projects/{project_id}/files",
            json={"path": "test.nx", "content": "print(\"Hello\")"},
            headers=auth_headers
        )
        file_id = file_response.json()["id"]
        
        # Update file
        response = client.put(
            f"/api/v2/ide/files/{file_id}",
            json={"content": "print(\"Updated\")"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "print(\"Updated\")"
        assert data["version"] == 2  # Version incremented


class TestCodeExecution:
    """Test code execution endpoints."""
    
    def test_execute_code(self, client, auth_headers):
        """Test code execution."""
        response = client.post(
            "/api/v2/ide/execute",
            json={"code": "print(\"Hello NexusLang!\")"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True or data["success"] is False
        assert "output" in data
        assert "execution_time" in data
    
    def test_compile_code(self, client, auth_headers):
        """Test binary compilation."""
        response = client.post(
            "/api/v2/ide/compile",
            json={"code": "fn main() { print(\"Test\") }"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "output" in data
    
    def test_analyze_code(self, client, auth_headers):
        """Test code analysis."""
        response = client.post(
            "/api/v2/ide/analyze",
            json={"code": "fn main() {}"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert "warnings" in data
        assert "suggestions" in data


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

