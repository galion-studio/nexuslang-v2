"""
Integration tests for API endpoints.
"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock

from v2.backend.main import app
from v2.backend.services.integrations import IntegrationManager


@pytest.fixture
def client():
    """Create test client for API testing."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def mock_integration_manager():
    """Mock integration manager for API tests."""
    manager = Mock(spec=IntegrationManager)

    # Mock available integrations
    manager.get_available_integrations.return_value = ["webhook", "github", "slack"]

    # Mock registered integrations
    manager.get_registered_integrations.return_value = ["test_webhook"]

    # Mock integration status
    mock_status = Mock()
    mock_status.name = "test_webhook"
    mock_status.healthy = True
    mock_status.last_check = None
    mock_status.error_message = None
    mock_status.capabilities = ["send_notification", "send_alert"]

    manager.get_integration_status.return_value = mock_status
    manager.get_all_statuses.return_value = {"test_webhook": mock_status}
    manager.get_integration_capabilities.return_value = ["send_notification", "send_alert"]
    manager.register_integration.return_value = True
    manager.unregister_integration.return_value = True
    manager.execute_operation.return_value = Mock(success=True, data={"result": "success"})

    return manager


@pytest.mark.asyncio
class TestIntegrationAPI:
    """Test integration API endpoints."""

    async def test_get_available_integrations(self, async_client, mock_integration_manager):
        """Test getting available integrations."""
        # Mock the dependency
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        response = await async_client.get("/integrations/available")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "webhook" in data

        # Clean up override
        app.dependency_overrides.clear()

    async def test_get_registered_integrations(self, async_client, mock_integration_manager):
        """Test getting registered integrations."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        response = await async_client.get("/integrations/registered")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "test_webhook" in data

        app.dependency_overrides.clear()

    async def test_register_integration(self, async_client, mock_integration_manager):
        """Test registering a new integration."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        integration_config = {
            "type": "webhook",
            "config": {
                "webhook_url": "https://httpbin.org/post",
                "secret": "test_secret"
            }
        }

        response = await async_client.post(
            "/integrations/register/test_integration",
            json=integration_config
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "registered successfully" in data["message"]

        app.dependency_overrides.clear()

    async def test_unregister_integration(self, async_client, mock_integration_manager):
        """Test unregistering an integration."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        response = await async_client.delete("/integrations/unregister/test_webhook")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "unregistered successfully" in data["message"]

        app.dependency_overrides.clear()

    async def test_get_integration_status_all(self, async_client, mock_integration_manager):
        """Test getting all integration statuses."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        response = await async_client.get("/integrations/status")

        assert response.status_code == 200
        data = response.json()

        assert "total_integrations" in data
        assert "healthy_integrations" in data
        assert "integrations" in data
        assert "test_webhook" in data["integrations"]

        integration_data = data["integrations"]["test_webhook"]
        assert integration_data["name"] == "test_webhook"
        assert integration_data["healthy"] is True
        assert "capabilities" in integration_data

        app.dependency_overrides.clear()

    async def test_get_integration_status_single(self, async_client, mock_integration_manager):
        """Test getting single integration status."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        response = await async_client.get("/integrations/status/test_webhook")

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "test_webhook"
        assert data["healthy"] is True
        assert "capabilities" in data

        app.dependency_overrides.clear()

    async def test_get_integration_status_not_found(self, async_client, mock_integration_manager):
        """Test getting status of non-existent integration."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        # Mock to return None for non-existent integration
        mock_integration_manager.get_integration_status.return_value = None

        response = await async_client.get("/integrations/status/non_existent")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

        app.dependency_overrides.clear()

    async def test_get_integration_capabilities(self, async_client, mock_integration_manager):
        """Test getting integration capabilities."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        response = await async_client.get("/integrations/capabilities/test_webhook")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert "send_notification" in data
        assert "send_alert" in data

        app.dependency_overrides.clear()

    async def test_get_integration_config_schema(self, async_client, mock_integration_manager):
        """Test getting integration config schema."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        # Mock schema response
        mock_schema = {
            "type": "object",
            "properties": {
                "webhook_url": {"type": "string"},
                "secret": {"type": "string"}
            }
        }
        mock_integration_manager.get_integration_config_schema.return_value = mock_schema

        response = await async_client.get("/integrations/schema/webhook")

        assert response.status_code == 200
        data = response.json()
        assert data == mock_schema

        app.dependency_overrides.clear()

    async def test_execute_operation(self, async_client, mock_integration_manager):
        """Test executing an integration operation."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        operation_request = {
            "integration": "test_webhook",
            "operation": "send_notification",
            "parameters": {
                "title": "Test Notification",
                "message": "Test message"
            }
        }

        response = await async_client.post("/integrations/execute", json=operation_request)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data
        assert "timestamp" in data

        app.dependency_overrides.clear()

    async def test_execute_bulk_operations(self, async_client, mock_integration_manager):
        """Test executing bulk operations."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        # Mock bulk operation result
        mock_result = Mock(success=True, data={"result": "success"})
        mock_integration_manager.execute_bulk_operation.return_value = [mock_result, mock_result]

        bulk_request = {
            "operations": [
                {
                    "integration": "test_webhook",
                    "operation": "send_notification",
                    "parameters": {"title": "Test 1", "message": "Message 1"}
                },
                {
                    "integration": "test_webhook",
                    "operation": "send_notification",
                    "parameters": {"title": "Test 2", "message": "Message 2"}
                }
            ]
        }

        response = await async_client.post("/integrations/execute/bulk", json=bulk_request)

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "results" in data
        assert len(data["results"]) == 2

        app.dependency_overrides.clear()

    async def test_search_integrations(self, async_client, mock_integration_manager):
        """Test searching integrations."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        # Mock search results
        mock_results = [
            {
                "name": "test_webhook",
                "capabilities": ["send_notification"],
                "healthy": True
            }
        ]
        mock_integration_manager.search_integrations.return_value = mock_results

        response = await async_client.get("/integrations/search?query=webhook")

        assert response.status_code == 200
        data = response.json()

        assert "query" in data
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "test_webhook"

        app.dependency_overrides.clear()

    async def test_test_integration(self, async_client, mock_integration_manager):
        """Test integration connection testing."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        response = await async_client.post("/integrations/test/test_webhook")

        assert response.status_code == 200
        data = response.json()

        assert "integration" in data
        assert "healthy" in data
        assert "tested_at" in data

        app.dependency_overrides.clear()

    async def test_get_integration_stats(self, async_client, mock_integration_manager):
        """Test getting integration statistics."""
        app.dependency_overrides[IntegrationManager] = lambda: mock_integration_manager

        # Mock stats
        mock_stats = {
            "total_integrations": 1,
            "healthy_integrations": 1,
            "uptime_percentage": 100.0,
            "last_updated": "2024-01-20T10:00:00Z"
        }
        mock_integration_manager.get_integration_stats.return_value = mock_stats

        response = await async_client.get("/integrations/stats")

        assert response.status_code == 200
        data = response.json()
        assert data == mock_stats

        app.dependency_overrides.clear()


class TestAgentAPI:
    """Test agent API endpoints."""

    async def test_get_agents(self, async_client):
        """Test getting all agents."""
        response = await async_client.get("/agents")

        # Should return a list (may be empty in test environment)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_agent_status(self, async_client):
        """Test getting agent status."""
        response = await async_client.get("/agents/status")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_execute_task(self, async_client):
        """Test task execution."""
        task_request = {
            "description": "Test task for API testing",
            "priority": "normal",
            "requirements": ["test"],
            "metadata": {"test": True}
        }

        response = await async_client.post("/agents/execute", json=task_request)

        # May succeed or fail depending on agent availability
        assert response.status_code in [200, 400, 500]
        data = response.json()

        if response.status_code == 200:
            assert "task_id" in data
        else:
            assert "detail" in data or "error" in data


class TestHealthAPI:
    """Test health check endpoints."""

    async def test_health_check(self, async_client):
        """Test basic health check."""
        response = await async_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    async def test_detailed_health(self, async_client):
        """Test detailed health check."""
        response = await async_client.get("/health/detailed")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data


class TestTaskAPI:
    """Test task management endpoints."""

    async def test_get_tasks(self, async_client):
        """Test getting tasks."""
        response = await async_client.get("/tasks")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_create_task(self, async_client):
        """Test creating a task."""
        task_data = {
            "description": "Test task creation",
            "priority": "normal",
            "metadata": {"source": "api_test"}
        }

        response = await async_client.post("/tasks", json=task_data)

        assert response.status_code in [200, 201]
        if response.status_code == 201:
            data = response.json()
            assert "task_id" in data

    async def test_get_task_queue_status(self, async_client):
        """Test getting task queue status."""
        response = await async_client.get("/tasks/queue/status")

        assert response.status_code == 200
        data = response.json()
        assert "queue_size" in data
        assert "active_tasks" in data
        assert "max_concurrent" in data
