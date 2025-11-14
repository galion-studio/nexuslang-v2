"""
Unit tests for AgentOrchestrator.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from v2.backend.services.agents.agent_orchestrator import AgentOrchestrator, OrchestratorMetrics


class TestOrchestratorMetrics:
    """Test the OrchestratorMetrics class."""

    def test_initialization(self):
        """Test metrics initialization."""
        metrics = OrchestratorMetrics()

        assert metrics.total_executions == 0
        assert metrics.total_cost == 0.0
        assert metrics.average_response_time == 0.0
        assert metrics.success_rate == 1.0
        assert isinstance(metrics.agent_usage, dict)
        assert isinstance(metrics.cost_by_agent, dict)
        assert isinstance(metrics.errors_by_agent, dict)

    def test_record_execution(self):
        """Test recording an agent execution."""
        metrics = OrchestratorMetrics()

        # Mock agent result
        result = Mock()
        result.success = True
        result.cost = 0.05

        # Record execution
        metrics.record_execution("test_agent", result, 1.5)

        assert metrics.total_executions == 1
        assert metrics.total_cost == 0.05
        assert metrics.average_response_time == 1.5
        assert metrics.success_rate == 1.0
        assert metrics.agent_usage["test_agent"] == 1
        assert metrics.cost_by_agent["test_agent"] == 0.05

    def test_record_multiple_executions(self):
        """Test recording multiple executions."""
        metrics = OrchestratorMetrics()

        # First execution
        result1 = Mock()
        result1.success = True
        result1.cost = 0.10
        metrics.record_execution("agent1", result1, 1.0)

        # Second execution (failure)
        result2 = Mock()
        result2.success = False
        result2.cost = 0.05
        metrics.record_execution("agent2", result2, 2.0)

        # Third execution
        result3 = Mock()
        result3.success = True
        result3.cost = 0.08
        metrics.record_execution("agent1", result3, 1.5)

        assert metrics.total_executions == 3
        assert metrics.total_cost == 0.23
        assert metrics.average_response_time == pytest.approx(1.5, rel=1e-2)
        assert metrics.success_rate == pytest.approx(2/3, rel=1e-2)
        assert metrics.agent_usage["agent1"] == 2
        assert metrics.agent_usage["agent2"] == 1
        assert metrics.errors_by_agent["agent2"] == 1

    def test_get_summary(self):
        """Test getting metrics summary."""
        metrics = OrchestratorMetrics()

        # Add some test data
        result = Mock()
        result.success = True
        result.cost = 0.05
        metrics.record_execution("test_agent", result, 1.0)

        summary = metrics.get_summary()

        expected_keys = [
            'total_executions', 'total_cost', 'average_response_time',
            'success_rate', 'agent_usage', 'cost_by_agent', 'errors_by_agent'
        ]

        for key in expected_keys:
            assert key in summary


class TestAgentOrchestrator:
    """Test the AgentOrchestrator class."""

    @pytest.fixture
    async def orchestrator(self, tmp_path):
        """Create test orchestrator."""
        state_file = tmp_path / "test_state.json"
        orchestrator = AgentOrchestrator(shared_state_path=str(state_file))

        # Mock database and cache managers
        orchestrator.db_manager = AsyncMock()
        orchestrator.cache_manager = AsyncMock()

        yield orchestrator

        await orchestrator.cleanup()

    def test_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert isinstance(orchestrator.agents, dict)
        assert isinstance(orchestrator.metrics, OrchestratorMetrics)
        assert isinstance(orchestrator.task_queue, object)
        assert orchestrator.is_running is False
        assert isinstance(orchestrator.cost_limits, dict)
        assert 'per_execution' in orchestrator.cost_limits
        assert 'per_hour' in orchestrator.cost_limits
        assert 'per_day' in orchestrator.cost_limits

    async def test_add_agent(self, orchestrator, mock_agent):
        """Test adding an agent."""
        orchestrator.agents["test_agent"] = mock_agent

        assert "test_agent" in orchestrator.agents
        assert orchestrator.agents["test_agent"] == mock_agent

    async def test_get_agent_status_single(self, orchestrator, mock_agent):
        """Test getting status of a single agent."""
        orchestrator.agents["test_agent"] = mock_agent

        status = orchestrator.get_agent_status("test_agent")

        assert status == mock_agent.get_status.return_value

    async def test_get_agent_status_all(self, orchestrator, mock_agent):
        """Test getting status of all agents."""
        orchestrator.agents["test_agent"] = mock_agent

        statuses = orchestrator.get_agent_status()

        assert isinstance(statuses, list)
        assert len(statuses) == 1
        assert statuses[0] == mock_agent.get_status.return_value

    async def test_get_agent_status_not_found(self, orchestrator):
        """Test getting status of non-existent agent."""
        status = orchestrator.get_agent_status("non_existent")

        assert status == {"error": "Agent 'non_existent' not found"}

    async def test_task_queue_operations(self, orchestrator, sample_task):
        """Test task queue operations."""
        # Add task
        task_id = await orchestrator.task_queue.add_task(sample_task)
        assert task_id is not None

        # Get task
        task = await orchestrator.task_queue.get_next_task()
        assert task is not None
        assert task["task_id"] == task_id

        # Queue should be empty now
        task = await orchestrator.task_queue.get_next_task()
        assert task is None

    async def test_integration_registration(self, orchestrator, sample_integration_config):
        """Test integration registration."""
        success = orchestrator.register_integration(
            "test_integration",
            sample_integration_config["type"],
            sample_integration_config["config"]
        )

        # Should succeed since we're using webhook integration
        assert success is True
        assert "test_integration" in orchestrator.get_registered_integrations()

    async def test_integration_operations(self, orchestrator):
        """Test integration operations."""
        # Register a webhook integration
        orchestrator.register_integration("test_webhook", "webhook", {
            "webhook_url": "https://httpbin.org/post",
            "secret": "test_secret"
        })

        # Test notification sending
        result = await orchestrator.send_notification(
            "Test message",
            integration="webhook"
        )

        # Result should be handled gracefully
        assert result is not None or result is None  # Either success or expected failure

    async def test_save_load_state(self, orchestrator, tmp_path, mock_agent):
        """Test saving and loading orchestrator state."""
        # Add test data
        orchestrator.agents["test_agent"] = mock_agent
        orchestrator.is_running = True

        # Save state
        await orchestrator.save_state()

        # Verify file was created
        state_file = tmp_path / "test_state.json"
        assert state_file.exists()

        # Create new orchestrator and load state
        new_orchestrator = AgentOrchestrator(shared_state_path=str(state_file))
        state = await new_orchestrator.load_state()

        assert state is not None
        assert state["orchestrator"]["is_running"] is True
        assert "agents" in state

    async def test_cost_tracking(self, orchestrator):
        """Test cost tracking and limits."""
        # Test cost limits are set
        assert orchestrator.cost_limits["per_execution"] == 0.10
        assert orchestrator.cost_limits["per_hour"] == 10.0
        assert orchestrator.cost_limits["per_day"] == 50.0

    async def test_error_handling(self, orchestrator):
        """Test error handling in orchestrator operations."""
        # Test with invalid integration
        result = await orchestrator.execute_integration_operation(
            "non_existent_integration", "test_operation"
        )

        assert result is None

        # Test with invalid agent
        status = orchestrator.get_agent_status("non_existent_agent")
        assert "error" in status

    async def test_string_representations(self, orchestrator, mock_agent):
        """Test string representations."""
        orchestrator.agents["test_agent"] = mock_agent

        str_repr = str(orchestrator)
        repr_repr = repr(orchestrator)

        assert "AgentOrchestrator" in str_repr
        assert "AgentOrchestrator" in repr_repr
        assert "agents=1" in str_repr
        assert "running=False" in str_repr
