"""
Pytest configuration and shared fixtures for Galion testing.
"""

import asyncio
import pytest
import os
import tempfile
from typing import Dict, Any, AsyncGenerator
from unittest.mock import Mock, AsyncMock

from v2.backend.services.agents.agent_orchestrator import AgentOrchestrator
from v2.backend.services.integrations import IntegrationManager
from v2.backend.core.database import DatabaseManager
from v2.backend.core.cache import CacheManager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def temp_db():
    """Create a temporary database for testing."""
    # Use in-memory SQLite for tests
    db_manager = DatabaseManager("sqlite:///:memory:")

    # Initialize database schema
    await db_manager.initialize()

    yield db_manager

    # Cleanup
    await db_manager.cleanup()


@pytest.fixture(scope="session")
async def temp_cache():
    """Create a temporary cache for testing."""
    # Use in-memory Redis for tests (mocked)
    cache_manager = CacheManager(redis_url="redis://localhost:6379/1")

    yield cache_manager

    # Cleanup
    await cache_manager.cleanup()


@pytest.fixture
async def orchestrator(temp_db, temp_cache):
    """Create a test orchestrator instance."""
    # Create temporary directory for shared state
    with tempfile.TemporaryDirectory() as temp_dir:
        shared_state_path = os.path.join(temp_dir, "agent-state.json")

        orchestrator = AgentOrchestrator(shared_state_path=shared_state_path)

        # Mock database and cache managers
        orchestrator.db_manager = temp_db
        orchestrator.cache_manager = temp_cache

        yield orchestrator

        # Cleanup
        await orchestrator.cleanup()


@pytest.fixture
async def integration_manager():
    """Create a test integration manager."""
    manager = IntegrationManager()
    yield manager
    await manager.cleanup()


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = Mock()
    agent.name = "test_agent"
    agent.get_status.return_value = {
        "name": "test_agent",
        "status": "idle",
        "capabilities": ["test"],
        "success_rate": 1.0
    }
    agent.execute_task = AsyncMock(return_value=Mock(success=True, data={"result": "success"}))
    return agent


@pytest.fixture
def mock_integration():
    """Create a mock integration for testing."""
    integration = Mock()
    integration.test_connection = AsyncMock(return_value=Mock(success=True))
    integration.get_capabilities = AsyncMock(return_value=["test_operation"])
    integration.execute_operation = AsyncMock(return_value=Mock(success=True, data={"result": "success"}))
    return integration


@pytest.fixture
def sample_task():
    """Sample task data for testing."""
    return {
        "task_id": "test_task_123",
        "description": "Test task for unit testing",
        "priority": "normal",
        "requirements": ["test_capability"],
        "metadata": {"test": True}
    }


@pytest.fixture
def sample_agent_config():
    """Sample agent configuration for testing."""
    return {
        "name": "test_agent",
        "type": "test",
        "capabilities": ["test_operation"],
        "personality": {
            "expertise_level": "expert",
            "communication_style": "technical"
        }
    }


@pytest.fixture
def sample_integration_config():
    """Sample integration configuration for testing."""
    return {
        "type": "webhook",
        "config": {
            "webhook_url": "https://httpbin.org/post",
            "secret": "test_secret"
        }
    }


# Test utilities
class TestUtils:
    """Utility functions for testing."""

    @staticmethod
    def create_mock_response(success: bool = True, data: Any = None, error: str = None):
        """Create a mock response object."""
        response = Mock()
        response.success = success
        response.data = data
        response.error = error
        return response

    @staticmethod
    def create_test_task(task_type: str = "test", **kwargs):
        """Create a test task with default values."""
        task = {
            "task_id": f"test_{task_type}_{kwargs.get('id', '123')}",
            "type": task_type,
            "description": f"Test {task_type} task",
            "priority": kwargs.get("priority", "normal"),
            "created_at": "2024-01-20T10:00:00Z",
            "metadata": kwargs.get("metadata", {})
        }
        task.update(kwargs)
        return task

    @staticmethod
    async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
        """Wait for a condition to become true."""
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            if await condition_func():
                return True
            await asyncio.sleep(interval)

        return False


# Global test utilities instance
test_utils = TestUtils()


@pytest.fixture
def utils():
    """Provide test utilities to tests."""
    return test_utils


# Environment setup for tests
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    original_env = dict(os.environ)

    # Set test environment variables
    os.environ.update({
        "GALION_ENV": "test",
        "GALION_LOG_LEVEL": "WARNING",  # Reduce log noise during tests
        "GALION_TESTING": "true",
    })

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# Async test marker
pytestmark = pytest.mark.asyncio
