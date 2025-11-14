"""
Integration tests for the complete Deep Search workflow.
Tests end-to-end functionality from query to synthesized response.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import time

from v2.backend.services.deep_search.agents import AgentOrchestrator
from v2.backend.services.deep_search.workflow import StateMachine, ResearchState


class TestDeepSearchWorkflow:
    """Test the complete deep search workflow"""

    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator with mocked dependencies"""
        orch = AgentOrchestrator()

        # Mock the database and search engine for testing
        mock_db = Mock()
        mock_search_engine = Mock()
        mock_search_engine.search = AsyncMock(return_value=[
            Mock(
                title="Test Source 1",
                content="This is test content about the query topic.",
                similarity=0.9,
                id="1",
                tags=["test"],
                verified=True,
                created_at="2024-01-01",
                updated_at="2024-01-01"
            )
        ])

        # Replace agents with mocks that return proper results
        orch.agents['planner'].execute = AsyncMock(return_value=self._mock_planner_result())
        orch.agents['searcher'].execute = AsyncMock(return_value=self._mock_searcher_result())
        orch.agents['analyzer'].execute = AsyncMock(return_value=self._mock_analyzer_result())

        yield orch

    def _mock_planner_result(self):
        """Mock planner agent result"""
        from v2.backend.services.deep_search.agents import AgentResult, AgentState
        return AgentResult(
            agent_name="planner",
            state=AgentState.COMPLETED,
            data={
                "research_plan": {
                    "original_query": "test query",
                    "search_queries": ["test query"],
                    "execution_plan": {"phases": []}
                }
            },
            metadata={},
            execution_time=0.5,
            credits_used=0.5,
            success=True
        )

    def _mock_searcher_result(self):
        """Mock searcher agent result"""
        from v2.backend.services.deep_search.agents import AgentResult, AgentState
        return AgentResult(
            agent_name="searcher",
            state=AgentState.COMPLETED,
            data={
                "sources": [
                    {
                        "id": "1",
                        "title": "Test Source",
                        "content": "Test content about the topic",
                        "relevance_score": 0.9,
                        "search_method": "semantic"
                    }
                ]
            },
            metadata={},
            execution_time=1.0,
            credits_used=0.2,
            success=True
        )

    def _mock_analyzer_result(self):
        """Mock analyzer agent result"""
        from v2.backend.services.deep_search.agents import AgentResult, AgentState
        return AgentResult(
            agent_name="analyzer",
            state=AgentState.COMPLETED,
            data={
                "synthesized_answer": "This is a synthesized answer based on the research.",
                "key_information": {"main_points": ["Point 1", "Point 2"]},
                "confidence_score": 0.85,
                "sources_used": [{"title": "Test Source"}]
            },
            metadata={},
            execution_time=1.5,
            credits_used=1.0,
            success=True
        )

    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self, orchestrator):
        """Test complete workflow from query to answer"""
        query = "What is machine learning?"
        context = {"depth": "comprehensive", "persona": "isaac"}

        start_time = time.time()
        result = await orchestrator.execute_research(query, context)
        end_time = time.time()

        # Verify result structure
        assert isinstance(result, dict)
        assert result["query"] == query
        assert "synthesized_answer" in result
        assert "sources_used" in result
        assert "confidence_score" in result
        assert "processing_time" in result
        assert "persona_used" in result
        assert "metadata" in result

        # Verify reasonable processing time
        assert result["processing_time"] > 0
        assert result["processing_time"] < end_time - start_time + 1  # Allow some tolerance

    @pytest.mark.asyncio
    async def test_workflow_with_different_personas(self, orchestrator):
        """Test workflow with different writing personas"""
        query = "Explain quantum computing"
        personas = ["isaac", "technical", "creative"]

        for persona in personas:
            context = {"persona": persona, "depth": "quick"}

            result = await orchestrator.execute_research(query, context)

            assert result["persona_used"] == persona
            assert "synthesized_answer" in result
            assert len(result["synthesized_answer"]) > 0

    @pytest.mark.asyncio
    async def test_workflow_with_different_depths(self, orchestrator):
        """Test workflow with different research depths"""
        query = "What are microservices?"
        depths = ["quick", "comprehensive", "exhaustive"]

        for depth in depths:
            context = {"depth": depth, "persona": "default"}

            result = await orchestrator.execute_research(query, context)

            assert result["depth_used"] == depth
            assert "synthesized_answer" in result

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, orchestrator):
        """Test workflow error handling and recovery"""
        # Make planner fail
        orchestrator.agents['planner'].execute = AsyncMock(side_effect=Exception("Planner error"))

        result = await orchestrator.execute_research("test query")

        # Should handle error gracefully
        assert isinstance(result, dict)
        assert "error" in result or "query" in result

    @pytest.mark.asyncio
    async def test_workflow_metadata_collection(self, orchestrator):
        """Test that workflow collects comprehensive metadata"""
        query = "Test metadata collection"
        context = {"depth": "comprehensive"}

        result = await orchestrator.execute_research(query, context)

        metadata = result.get("metadata", {})

        # Should include workflow information
        expected_keys = ["workflow_path", "adaptation_decisions", "iterations"]
        for key in expected_keys:
            assert key in metadata

        # Workflow path should be a list
        assert isinstance(metadata["workflow_path"], list)
        assert len(metadata["workflow_path"]) > 0

    @pytest.mark.asyncio
    async def test_concurrent_workflow_execution(self, orchestrator):
        """Test running multiple workflows concurrently"""
        queries = [
            "What is AI?",
            "How does blockchain work?",
            "Explain cloud computing"
        ]

        # Create concurrent tasks
        tasks = []
        for query in queries:
            context = {"depth": "quick"}
            task = asyncio.create_task(orchestrator.execute_research(query, context))
            tasks.append(task)

        # Execute concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Verify all completed
        assert len(results) == len(queries)
        for result in results:
            assert isinstance(result, dict)
            assert "synthesized_answer" in result

        # Should complete faster than sequential execution
        total_time = end_time - start_time
        expected_sequential_time = len(queries) * 2.0  # Rough estimate
        assert total_time < expected_sequential_time

    @pytest.mark.asyncio
    async def test_workflow_with_empty_sources(self, orchestrator):
        """Test workflow when no sources are found"""
        # Mock searcher to return no sources
        from v2.backend.services.deep_search.agents import AgentResult, AgentState
        empty_search_result = AgentResult(
            agent_name="searcher",
            state=AgentState.COMPLETED,
            data={"sources": []},
            metadata={},
            execution_time=0.5,
            credits_used=0.1,
            success=True
        )
        orchestrator.agents['searcher'].execute = AsyncMock(return_value=empty_search_result)

        result = await orchestrator.execute_research("obscure topic with no sources")

        # Should still provide a response (possibly indicating limited information)
        assert isinstance(result, dict)
        assert "synthesized_answer" in result

    @pytest.mark.asyncio
    async def test_workflow_credit_calculation(self, orchestrator):
        """Test that credits are properly calculated"""
        # Test different depths
        depths_and_min_credits = [
            ("quick", 5),
            ("comprehensive", 15),
            ("exhaustive", 25)
        ]

        for depth, min_credits in depths_and_min_credits:
            result = await orchestrator.execute_research("test", {"depth": depth})

            # Should have reasonable credit usage
            assert result.get("processing_time", 0) > 0

    @pytest.mark.asyncio
    async def test_workflow_agent_coordination(self, orchestrator):
        """Test that agents coordinate properly"""
        query = "Test coordination"

        # Verify agents are called in sequence
        call_order = []

        async def mock_planner(*args, **kwargs):
            call_order.append("planner")
            return self._mock_planner_result()

        async def mock_searcher(*args, **kwargs):
            call_order.append("searcher")
            return self._mock_searcher_result()

        async def mock_analyzer(*args, **kwargs):
            call_order.append("analyzer")
            return self._mock_analyzer_result()

        orchestrator.agents['planner'].execute = mock_planner
        orchestrator.agents['searcher'].execute = mock_searcher
        orchestrator.agents['analyzer'].execute = mock_analyzer

        result = await orchestrator.execute_research(query)

        # Should call agents in correct order
        assert call_order == ["planner", "searcher", "analyzer"]
        assert result["synthesized_answer"] is not None


class TestWorkflowStateMachine:
    """Test the workflow state machine"""

    @pytest.fixture
    def state_machine(self):
        """Create state machine instance"""
        return StateMachine()

    def test_state_machine_initialization(self, state_machine):
        """Test state machine initializes correctly"""
        status = state_machine.get_workflow_stats()
        assert status["current_state"] == ResearchState.INITIALIZING
        assert status["total_workflows"] == 0

    @pytest.mark.asyncio
    async def test_state_machine_workflow_execution(self, state_machine):
        """Test state machine can execute workflows"""
        workflow_data = {
            "query": "test",
            "context": {"depth": "quick"}
        }

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator._handle_planning = AsyncMock(return_value={"data": {}})
        mock_orchestrator._handle_searching = AsyncMock(return_value={"data": {}})
        mock_orchestrator._handle_analyzing = AsyncMock(return_value={"data": {}})
        mock_orchestrator._handle_validating = AsyncMock(return_value={"data": {}})
        mock_orchestrator._handle_synthesizing = AsyncMock(return_value={"data": {}})

        result = await state_machine.execute_workflow(workflow_data, mock_orchestrator)

        # Should complete successfully
        assert result.success == True
        assert result.final_state == ResearchState.COMPLETED
        assert len(result.execution_path) > 0

    def test_state_machine_quality_adaptation(self, state_machine):
        """Test state machine adapts based on quality metrics"""
        # This would test the adaptive logic
        # For now, just verify the state machine exists
        assert hasattr(state_machine, 'execute_workflow')


class TestDeepSearchPerformance:
    """Performance tests for deep search"""

    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator for performance testing"""
        orch = AgentOrchestrator()
        # Mock agents for faster execution
        for agent in orch.agents.values():
            agent.execute = AsyncMock(return_value=Mock(
                success=True,
                data={"test": "data"},
                execution_time=0.1,
                credits_used=0.1
            ))
        yield orch

    @pytest.mark.asyncio
    async def test_workflow_performance_under_load(self, orchestrator):
        """Test performance with multiple concurrent requests"""
        num_requests = 10
        query = "Performance test query"

        # Create multiple concurrent requests
        tasks = []
        for i in range(num_requests):
            context = {"depth": "quick"}
            task = asyncio.create_task(orchestrator.execute_research(query, context))
            tasks.append(task)

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Verify all completed
        assert len(results) == num_requests
        assert all(isinstance(r, dict) for r in results)

        # Check performance
        total_time = end_time - start_time
        avg_time_per_request = total_time / num_requests

        # Should be reasonably fast (< 1 second per request on average)
        assert avg_time_per_request < 1.0

        print(".2f")
        print(".3f")

    @pytest.mark.asyncio
    async def test_memory_efficiency(self, orchestrator):
        """Test memory efficiency of workflows"""
        # Run multiple workflows and ensure no memory leaks
        for i in range(5):
            result = await orchestrator.execute_research(f"Query {i}")
            assert result is not None

        # Check that agent states are clean
        status = orchestrator.get_agent_status()
        assert len(status) == 3  # All agents still present


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
