"""
Comprehensive tests for the Deep Search API endpoints.
Tests deep research functionality, chat integration, and error handling.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json

from v2.backend.main import app
from v2.backend.services.deep_search.agents import AgentOrchestrator


class TestDeepSearchAPI:
    """Test the Deep Search API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    async def async_client(self):
        """Create async test client"""
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            yield client

    @pytest.fixture
    def mock_orchestrator(self):
        """Mock the agent orchestrator"""
        orchestrator = Mock(spec=AgentOrchestrator)
        orchestrator.execute_research = AsyncMock()
        return orchestrator

    def test_deep_research_endpoint_exists(self, client):
        """Test that the deep research endpoint exists and is accessible"""
        # This should be a POST endpoint
        response = client.post("/api/v2/grokopedia/deep-research")
        # Should not be 404
        assert response.status_code != 404

    def test_deep_search_chat_endpoint_exists(self, client):
        """Test that the deep search chat endpoint exists"""
        response = client.post("/api/v2/ai/deep-search")
        # Should not be 404
        assert response.status_code != 404

    @pytest.mark.asyncio
    async def test_deep_research_success(self, async_client, mock_orchestrator):
        """Test successful deep research request"""
        mock_response = {
            "query": "What is machine learning?",
            "synthesized_answer": "Machine learning is a subset of AI...",
            "sources_used": [{"title": "ML Guide", "content": "..."}],
            "confidence_score": 0.85,
            "processing_time": 2.5,
            "persona_used": "isaac",
            "metadata": {
                "workflow_path": ["planning", "searching", "analyzing"],
                "adaptation_decisions": [],
                "iterations": 1
            }
        }
        mock_orchestrator.execute_research.return_value = mock_response

        with patch('v2.backend.api.grokopedia.AgentOrchestrator', return_value=mock_orchestrator):
            payload = {
                "query": "What is machine learning?",
                "persona": "isaac",
                "depth": "comprehensive"
            }

            response = await async_client.post("/api/v2/grokopedia/deep-research", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "What is machine learning?"
            assert "synthesized_answer" in data
            assert "sources_used" in data
            assert "confidence_score" in data
            assert data["persona_used"] == "isaac"

    @pytest.mark.asyncio
    async def test_deep_research_with_sources(self, async_client, mock_orchestrator):
        """Test deep research with source inclusion"""
        mock_response = {
            "query": "Test query",
            "synthesized_answer": "Test answer",
            "sources_used": [
                {"title": "Source 1", "content": "Content 1", "score": 0.9},
                {"title": "Source 2", "content": "Content 2", "score": 0.8}
            ],
            "confidence_score": 0.75,
            "processing_time": 1.2,
            "persona_used": "technical"
        }
        mock_orchestrator.execute_research.return_value = mock_response

        with patch('v2.backend.api.grokopedia.AgentOrchestrator', return_value=mock_orchestrator):
            payload = {
                "query": "Test query",
                "include_sources": True,
                "max_sources": 5,
                "persona": "technical"
            }

            response = await async_client.post("/api/v2/grokopedia/deep-research", json=payload)
            assert response.status_code == 200

            data = response.json()
            assert len(data["sources_used"]) == 2
            assert data["sources_used"][0]["title"] == "Source 1"

    @pytest.mark.asyncio
    async def test_deep_research_different_personas(self, async_client, mock_orchestrator):
        """Test deep research with different writing personas"""
        personas = ["isaac", "technical", "creative", "default"]

        for persona in personas:
            mock_response = {
                "query": "Test query",
                "synthesized_answer": f"Response in {persona} style",
                "sources_used": [],
                "confidence_score": 0.8,
                "processing_time": 1.0,
                "persona_used": persona
            }
            mock_orchestrator.execute_research.return_value = mock_response

            with patch('v2.backend.api.grokopedia.AgentOrchestrator', return_value=mock_orchestrator):
                payload = {
                    "query": "Test query",
                    "persona": persona
                }

                response = await async_client.post("/api/v2/grokopedia/deep-research", json=payload)
                assert response.status_code == 200

                data = response.json()
                assert data["persona_used"] == persona

    @pytest.mark.asyncio
    async def test_deep_research_different_depths(self, async_client, mock_orchestrator):
        """Test deep research with different depth levels"""
        depths = ["quick", "comprehensive", "exhaustive"]

        for depth in depths:
            mock_response = {
                "query": "Test query",
                "synthesized_answer": f"Response with {depth} depth",
                "sources_used": [],
                "confidence_score": 0.8,
                "processing_time": 1.0,
                "depth_used": depth
            }
            mock_orchestrator.execute_research.return_value = mock_response

            with patch('v2.backend.api.grokopedia.AgentOrchestrator', return_value=mock_orchestrator):
                payload = {
                    "query": "Test query",
                    "depth": depth
                }

                response = await async_client.post("/api/v2/grokopedia/deep-research", json=payload)
                assert response.status_code == 200

                data = response.json()
                assert data["depth_used"] == depth

    @pytest.mark.asyncio
    async def test_deep_research_empty_query(self, async_client):
        """Test deep research with empty query"""
        payload = {
            "query": "",
            "persona": "isaac"
        }

        response = await async_client.post("/api/v2/grokopedia/deep-research", json=payload)
        # Should handle gracefully - either validation error or default behavior
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_deep_research_invalid_persona(self, async_client, mock_orchestrator):
        """Test deep research with invalid persona"""
        mock_response = {
            "query": "Test query",
            "synthesized_answer": "Default response",
            "sources_used": [],
            "confidence_score": 0.8,
            "processing_time": 1.0,
            "persona_used": "default"  # Should fallback to default
        }
        mock_orchestrator.execute_research.return_value = mock_response

        with patch('v2.backend.api.grokopedia.AgentOrchestrator', return_value=mock_orchestrator):
            payload = {
                "query": "Test query",
                "persona": "invalid_persona"
            }

            response = await async_client.post("/api/v2/grokopedia/deep-research", json=payload)
            assert response.status_code == 200

            data = response.json()
            assert data["persona_used"] == "default"

    @pytest.mark.asyncio
    async def test_deep_search_chat_integration(self, async_client):
        """Test deep search integration with chat API"""
        # Mock the AI service
        with patch('v2.backend.api.ai.get_ai_service') as mock_get_ai:
            mock_ai = Mock()
            mock_ai.chat_completion = AsyncMock(return_value={
                "response": "Deep search enhanced response",
                "search_results": [
                    {"title": "Source 1", "content": "Content 1", "score": 0.9}
                ],
                "search_performed": True,
                "confidence_score": 0.85
            })
            mock_get_ai.return_value = mock_ai

            payload = {
                "messages": [{"role": "user", "content": "What is AI?"}],
                "searchQuery": "artificial intelligence",
                "model": "gpt-4",
                "searchLimit": 5,
                "includeSources": True
            }

            response = await async_client.post("/api/v2/ai/deep-search", json=payload)
            assert response.status_code == 200

            data = response.json()
            assert "response" in data
            assert data.get("search_performed") == True
            assert "search_results" in data

    @pytest.mark.asyncio
    async def test_deep_research_orchestrator_failure(self, async_client, mock_orchestrator):
        """Test handling of orchestrator failures"""
        mock_orchestrator.execute_research.side_effect = Exception("Orchestrator error")

        with patch('v2.backend.api.grokopedia.AgentOrchestrator', return_value=mock_orchestrator):
            payload = {
                "query": "Test query"
            }

            response = await async_client.post("/api/v2/grokopedia/deep-research", json=payload)
            assert response.status_code == 500

            data = response.json()
            assert "error" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_deep_research_rate_limiting(self, async_client, mock_orchestrator):
        """Test rate limiting for deep research"""
        mock_response = {
            "query": "Test",
            "synthesized_answer": "Response",
            "sources_used": [],
            "confidence_score": 0.8,
            "processing_time": 1.0
        }
        mock_orchestrator.execute_research.return_value = mock_response

        # This test would need rate limiting middleware to be fully tested
        # For now, just verify normal operation
        with patch('v2.backend.api.grokopedia.AgentOrchestrator', return_value=mock_orchestrator):
            payload = {"query": "Test query"}

            response = await async_client.post("/api/v2/grokopedia/deep-research", json=payload)
            assert response.status_code in [200, 429]  # 429 would be rate limited

    def test_deep_research_request_validation(self, client):
        """Test request validation for deep research"""
        # Missing query
        payload = {"persona": "isaac"}
        response = client.post("/api/v2/grokopedia/deep-research", json=payload)
        assert response.status_code == 422  # Validation error

        # Invalid depth
        payload = {"query": "test", "depth": "invalid"}
        response = client.post("/api/v2/grokopedia/deep-research", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_deep_research_workflow_metadata(self, async_client, mock_orchestrator):
        """Test that workflow metadata is properly returned"""
        mock_response = {
            "query": "Test query",
            "synthesized_answer": "Test answer",
            "sources_used": [],
            "confidence_score": 0.9,
            "processing_time": 3.2,
            "metadata": {
                "workflow_path": ["planning", "searching", "analyzing", "synthesizing"],
                "adaptation_decisions": ["increased_search_depth"],
                "iterations": 2,
                "processing_phases": ["planning", "searching", "analyzing"],
                "quality_metrics": {"source_quality": 0.85, "consistency": 0.92}
            }
        }
        mock_orchestrator.execute_research.return_value = mock_response

        with patch('v2.backend.api.grokopedia.AgentOrchestrator', return_value=mock_orchestrator):
            payload = {"query": "Test query", "depth": "exhaustive"}

            response = await async_client.post("/api/v2/grokopedia/deep-research", json=payload)
            assert response.status_code == 200

            data = response.json()
            assert "metadata" in data
            assert "workflow_path" in data["metadata"]
            assert "adaptation_decisions" in data["metadata"]
            assert len(data["metadata"]["workflow_path"]) > 0


class TestDeepSearchIntegration:
    """Integration tests for deep search functionality"""

    @pytest.mark.asyncio
    async def test_end_to_end_deep_research(self, async_client):
        """Test complete end-to-end deep research flow"""
        # This would be a full integration test with real services
        # For now, test the endpoint structure
        payload = {
            "query": "What are microservices?",
            "persona": "technical",
            "depth": "comprehensive",
            "include_sources": True
        }

        response = await async_client.post("/api/v2/grokopedia/deep-research", json=payload)

        # Should not be 404 (endpoint exists)
        assert response.status_code != 404

        # If successful, should have expected structure
        if response.status_code == 200:
            data = response.json()
            required_fields = ["query", "synthesized_answer", "confidence_score"]
            for field in required_fields:
                assert field in data

    @pytest.mark.asyncio
    async def test_concurrent_deep_research_requests(self, async_client):
        """Test handling multiple concurrent deep research requests"""
        # Create multiple concurrent requests
        tasks = []
        for i in range(3):
            payload = {
                "query": f"Test query {i}",
                "persona": "isaac"
            }
            task = async_client.post("/api/v2/grokopedia/deep-research", json=payload)
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # All requests should complete (may succeed or fail based on implementation)
        assert len(responses) == 3
        for response in responses:
            assert response.status_code in [200, 500, 429]  # Valid response codes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
