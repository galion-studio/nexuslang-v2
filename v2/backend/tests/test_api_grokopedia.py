"""
Test suite for Grokopedia API endpoints.
Tests knowledge search, entry management, and graph operations.
"""

import pytest
from fastapi.testclient import TestClient

from ..main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestSearch:
    """Test search endpoints."""
    
    def test_search_knowledge(self, client):
        """Test knowledge search."""
        response = client.get("/api/v2/grokopedia/search?q=machine+learning&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "query" in data
        assert data["query"] == "machine learning"
    
    def test_search_with_filters(self, client):
        """Test search with filters."""
        response = client.get(
            "/api/v2/grokopedia/search?q=AI&verified_only=true&tags=technology"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
    
    def test_query_suggestions(self, client):
        """Test query suggestions."""
        response = client.get("/api/v2/grokopedia/suggest?q=quantum&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)


class TestEntries:
    """Test entry management endpoints."""
    
    def test_get_entry(self, client):
        """Test getting an entry (may not exist in test DB)."""
        # This test assumes the database may be empty
        test_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v2/grokopedia/entries/{test_id}")
        
        # Should return 404 if entry doesn't exist
        assert response.status_code in [200, 404]
    
    def test_create_entry_requires_auth(self, client):
        """Test that creating entry requires authentication."""
        response = client.post(
            "/api/v2/grokopedia/entries",
            json={
                "title": "Test Entry",
                "content": "Test content",
                "tags": ["test"]
            }
        )
        
        # Should require authentication
        assert response.status_code == 401


class TestTags:
    """Test tag endpoints."""
    
    def test_get_popular_tags(self, client):
        """Test getting popular tags."""
        response = client.get("/api/v2/grokopedia/tags?limit=20")
        
        assert response.status_code == 200
        data = response.json()
        assert "tags" in data


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

