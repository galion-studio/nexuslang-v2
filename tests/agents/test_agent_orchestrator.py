"""
Comprehensive tests for the Agent Orchestrator and multi-agent system.
Tests task routing, agent coordination, performance monitoring, and error handling.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import time
from typing import Dict, Any

from v2.backend.services.agents.agent_orchestrator import AgentOrchestrator, Task
from v2.backend.services.agents.base_agent import AgentResult, AgentContext, AgentType
from v2.backend.services.agents.financial_advisor import FinancialAdvisorAgent
from v2.backend.services.agents.customer_support import CustomerSupportAgent


class TestAgentOrchestrator:
    """Test the AgentOrchestrator class"""

    @pytest.fixture
    async def orchestrator(self):
        """Create a test orchestrator instance"""
        orch = AgentOrchestrator(max_concurrent_tasks=5)

        # Mock agents to avoid real API calls
        orch.agents = {
            AgentType.FINANCIAL_ADVISOR: Mock(spec=FinancialAdvisorAgent),
            AgentType.CUSTOMER_SUPPORT: Mock(spec=CustomerSupportAgent),
        }

        # Mock the agents' execute methods
        for agent in orch.agents.values():
            agent.execute = AsyncMock(return_value=AgentResult(
                success=True,
                response="Mock response",
                cost=0.02,
                execution_time=1.0
            ))

        yield orch

        # Cleanup
        if orch.is_running:
            await orch.stop()

    @pytest.mark.asyncio
    async def test_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert len(orchestrator.agents) == 2
        assert orchestrator.max_concurrent_tasks == 5
        assert orchestrator.status.value == "idle"
        assert len(orchestrator.active_tasks) == 0

    @pytest.mark.asyncio
    async def test_start_stop_orchestrator(self, orchestrator):
        """Test starting and stopping the orchestrator"""
        assert not orchestrator.is_running

        await orchestrator.start()
        assert orchestrator.is_running
        assert orchestrator.processing_task is not None

        await orchestrator.stop()
        assert not orchestrator.is_running
        assert orchestrator.processing_task is None

    @pytest.mark.asyncio
    async def test_task_execution_success(self, orchestrator):
        """Test successful task execution"""
        await orchestrator.start()

        prompt = "Help me with financial planning"
        context = AgentContext(user_id="test_user")

        result = await orchestrator.execute(prompt, AgentType.FINANCIAL_ADVISOR, context)

        assert result.success == True
        assert result.response == "Mock response"
        assert result.cost == 0.02
        assert result.execution_time == 1.0

        # Verify agent was called correctly
        agent = orchestrator.agents[AgentType.FINANCIAL_ADVISOR]
        agent.execute.assert_called_once_with(prompt, context)

    @pytest.mark.asyncio
    async def test_automatic_agent_selection(self, orchestrator):
        """Test automatic agent selection based on prompt content"""
        await orchestrator.start()

        test_cases = [
            ("I need help with my budget", AgentType.FINANCIAL_ADVISOR),
            ("My app is crashing, please help", AgentType.CUSTOMER_SUPPORT),
            ("How do I invest in stocks?", AgentType.FINANCIAL_ADVISOR),
            ("I can't log in to my account", AgentType.CUSTOMER_SUPPORT),
        ]

        for prompt, expected_agent in test_cases:
            result = await orchestrator.execute(prompt)

            # Verify the correct agent was selected
            for agent_type, agent in orchestrator.agents.items():
                if agent_type == expected_agent:
                    agent.execute.assert_called()
                else:
                    agent.execute.assert_not_called()

            # Reset mocks for next test
            for agent in orchestrator.agents.values():
                agent.execute.reset_mock()

    @pytest.mark.asyncio
    async def test_agent_execution_failure(self, orchestrator):
        """Test handling of agent execution failures"""
        await orchestrator.start()

        # Make one agent fail
        failing_agent = orchestrator.agents[AgentType.FINANCIAL_ADVISOR]
        failing_agent.execute = AsyncMock(side_effect=Exception("Agent error"))

        result = await orchestrator.execute("Test prompt", AgentType.FINANCIAL_ADVISOR)

        assert result.success == False
        assert "Agent error" in result.error
        assert result.cost == 0.0

    @pytest.mark.asyncio
    async def test_task_timeout(self, orchestrator):
        """Test task timeout handling"""
        # Set very short timeout
        orchestrator.timeout = 0.1

        # Make agent take longer than timeout
        slow_agent = orchestrator.agents[AgentType.FINANCIAL_ADVISOR]
        async def slow_execute(*args, **kwargs):
            await asyncio.sleep(0.2)  # Longer than timeout
            return AgentResult(success=True, response="Slow response", cost=0.01, execution_time=0.2)

        slow_agent.execute = slow_execute

        result = await orchestrator.execute("Slow task", AgentType.FINANCIAL_ADVISOR)

        assert result.success == False
        assert "timed out" in result.response.lower()

    def test_metrics_tracking(self, orchestrator):
        """Test metrics tracking functionality"""
        initial_tasks = orchestrator.metrics.total_tasks

        # Add some mock completed tasks
        orchestrator.metrics.completed_tasks = 5
        orchestrator.metrics.total_cost = 0.10
        orchestrator.metrics.average_execution_time = 1.5

        metrics = orchestrator.get_metrics()

        assert metrics.total_tasks == initial_tasks
        assert metrics.completed_tasks == 5
        assert metrics.total_cost == 0.10
        assert metrics.average_execution_time == 1.5

    @pytest.mark.asyncio
    async def test_concurrent_task_processing(self, orchestrator):
        """Test processing multiple tasks concurrently"""
        await orchestrator.start()

        # Create multiple tasks
        tasks = []
        for i in range(3):
            task = asyncio.create_task(
                orchestrator.execute(f"Task {i}", AgentType.FINANCIAL_ADVISOR)
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)

        # All tasks should succeed
        assert all(result.success for result in results)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_queue_status_tracking(self, orchestrator):
        """Test queue status tracking"""
        await orchestrator.start()

        # Initially empty
        status = orchestrator.get_queue_status()
        assert status['queue_size'] == 0
        assert status['active_tasks'] == 0

        # Add a task
        task = Task(id="test_task", prompt="Test", agent_type=AgentType.FINANCIAL_ADVISOR)
        await orchestrator.task_queue.put(task)
        orchestrator.active_tasks[task.id] = task

        status = orchestrator.get_queue_status()
        assert status['active_tasks'] == 1

    @pytest.mark.asyncio
    async def test_health_check(self, orchestrator):
        """Test health check functionality"""
        health = await orchestrator.health_check()

        assert 'orchestrator' in health
        assert 'agents' in health
        assert health['orchestrator']['status'] in ['healthy', 'stopped']
        assert len(health['agents']) == 2

        # All agents should report healthy status
        for agent_status in health['agents'].values():
            assert 'status' in agent_status

    def test_agent_status_reporting(self, orchestrator):
        """Test agent status reporting"""
        status = orchestrator.get_agent_status()

        assert len(status) == 2
        assert AgentType.FINANCIAL_ADVISOR.value in status
        assert AgentType.CUSTOMER_SUPPORT.value in status

        for agent_info in status.values():
            assert 'name' in agent_info
            assert 'status' in agent_info
            assert 'capabilities' in agent_info


class TestTask:
    """Test the Task class"""

    def test_task_creation(self):
        """Test task creation with all parameters"""
        context = AgentContext(user_id="test_user", session_id="session_123")
        task = Task(
            id="task_123",
            prompt="Test prompt",
            agent_type=AgentType.FINANCIAL_ADVISOR,
            context=context,
            priority=3
        )

        assert task.id == "task_123"
        assert task.prompt == "Test prompt"
        assert task.agent_type == AgentType.FINANCIAL_ADVISOR
        assert task.context == context
        assert task.priority == 3
        assert isinstance(task.created_at, float)

    def test_task_auto_timestamp(self):
        """Test automatic timestamp assignment"""
        before = time.time()
        task = Task(id="test", prompt="test")
        after = time.time()

        assert before <= task.created_at <= after


class TestAgentIntegration:
    """Integration tests for agent interactions"""

    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator with real agents for integration testing"""
        orch = AgentOrchestrator(max_concurrent_tasks=3)

        # Replace with real agents (they'll use mock services)
        orch.agents = {
            AgentType.FINANCIAL_ADVISOR: FinancialAdvisorAgent(),
            AgentType.CUSTOMER_SUPPORT: CustomerSupportAgent(),
        }

        # Mock the external services to avoid real API calls
        with patch('v2.backend.services.agents.financial_advisor.openai') as mock_openai:
            mock_openai.Audio.transcribe.return_value = {"text": "Mock transcription"}
            yield orch

        await orch.stop()

    @pytest.mark.asyncio
    async def test_agent_response_format(self, orchestrator):
        """Test that agents return properly formatted responses"""
        await orchestrator.start()

        result = await orchestrator.execute("Test financial advice", AgentType.FINANCIAL_ADVISOR)

        # Check response structure
        assert isinstance(result, AgentResult)
        assert isinstance(result.success, bool)
        assert isinstance(result.response, str)
        assert isinstance(result.cost, float)
        assert isinstance(result.execution_time, float)

    @pytest.mark.asyncio
    async def test_agent_context_passing(self, orchestrator):
        """Test that context is properly passed to agents"""
        await orchestrator.start()

        context = AgentContext(
            user_id="user_123",
            session_id="session_456",
            user_preferences={"language": "en", "expertise": "beginner"}
        )

        result = await orchestrator.execute("Budget help", AgentType.FINANCIAL_ADVISOR, context)

        assert result.success  # Should work with context

    @pytest.mark.asyncio
    async def test_agent_error_recovery(self, orchestrator):
        """Test agent error recovery and fallback behavior"""
        await orchestrator.start()

        # Test with invalid input
        result = await orchestrator.execute("", AgentType.FINANCIAL_ADVISOR)

        # Should handle gracefully
        assert isinstance(result, AgentResult)

    @pytest.mark.asyncio
    async def test_performance_under_load(self, orchestrator):
        """Test performance under concurrent load"""
        await orchestrator.start()

        start_time = time.time()

        # Execute multiple concurrent tasks
        tasks = []
        for i in range(5):
            task = asyncio.create_task(
                orchestrator.execute(f"Task {i}", AgentType.FINANCIAL_ADVISOR)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # All tasks should complete
        assert all(result.success for result in results)

        # Should complete within reasonable time (allowing for async processing)
        total_time = end_time - start_time
        assert total_time < 10  # Less than 10 seconds for 5 concurrent tasks


class TestAgentOrchestratorEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    async def orchestrator(self):
        orch = AgentOrchestrator(max_concurrent_tasks=2)

        # Mock agents
        orch.agents = {
            AgentType.FINANCIAL_ADVISOR: Mock(spec=FinancialAdvisorAgent),
        }

        for agent in orch.agents.values():
            agent.execute = AsyncMock(return_value=AgentResult(
                success=True, response="OK", cost=0.01, execution_time=0.5
            ))

        yield orch
        if orch.is_running:
            await orch.stop()

    @pytest.mark.asyncio
    async def test_nonexistent_agent_request(self, orchestrator):
        """Test requesting a non-existent agent"""
        result = await orchestrator.execute("Test", AgentType.CODE_EXECUTION)

        # Should fail gracefully
        assert result.success == False
        assert "no agent available" in result.response.lower()

    @pytest.mark.asyncio
    async def test_empty_prompt_handling(self, orchestrator):
        """Test handling of empty or whitespace-only prompts"""
        test_cases = ["", "   ", "\n\t  \n"]

        for prompt in test_cases:
            result = await orchestrator.execute(prompt, AgentType.FINANCIAL_ADVISOR)
            # Should handle gracefully (implementation dependent)
            assert isinstance(result, AgentResult)

    @pytest.mark.asyncio
    async def test_very_long_prompt(self, orchestrator):
        """Test handling of very long prompts"""
        long_prompt = "Help me " * 1000  # Very long prompt

        result = await orchestrator.execute(long_prompt, AgentType.FINANCIAL_ADVISOR)

        # Should handle long prompts
        assert isinstance(result, AgentResult)

    @pytest.mark.asyncio
    async def test_special_characters_in_prompt(self, orchestrator):
        """Test handling of special characters and unicode in prompts"""
        special_prompts = [
            "Hello @#$%^&*()!",
            "Test with émojis 🎉🚀💡",
            "Unicode: 你好世界 🌍",
            "Symbols: ≤≥≠≈∞∫",
        ]

        for prompt in special_prompts:
            result = await orchestrator.execute(prompt, AgentType.FINANCIAL_ADVISOR)
            assert isinstance(result, AgentResult)

    @pytest.mark.asyncio
    async def test_memory_cleanup(self, orchestrator):
        """Test that completed tasks are properly cleaned up"""
        await orchestrator.start()

        # Execute several tasks
        for i in range(3):
            await orchestrator.execute(f"Task {i}", AgentType.FINANCIAL_ADVISOR)

        # Check that tasks were tracked and cleaned up
        assert len(orchestrator.completed_tasks) == 3
        assert len(orchestrator.active_tasks) == 0

    @pytest.mark.asyncio
    async def test_agent_restart_handling(self, orchestrator):
        """Test handling of agent restarts during execution"""
        await orchestrator.start()

        # Simulate agent becoming unavailable during execution
        agent = orchestrator.agents[AgentType.FINANCIAL_ADVISOR]
        agent.execute = AsyncMock(side_effect=Exception("Agent restarted"))

        result = await orchestrator.execute("Test", AgentType.FINANCIAL_ADVISOR)

        assert result.success == False
        assert "Agent restarted" in result.error

    def test_metrics_accuracy(self, orchestrator):
        """Test that metrics are accurately tracked"""
        # Simulate some activity
        orchestrator.metrics.total_tasks = 10
        orchestrator.metrics.completed_tasks = 8
        orchestrator.metrics.failed_tasks = 2
        orchestrator.metrics.total_cost = 0.20

        metrics = orchestrator.get_metrics()

        assert metrics.total_tasks == 10
        assert metrics.completed_tasks == 8
        assert metrics.failed_tasks == 2
        assert metrics.total_cost == 0.20

        # Test success rate calculation
        success_rate = metrics.completed_tasks / metrics.total_tasks
        assert success_rate == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
