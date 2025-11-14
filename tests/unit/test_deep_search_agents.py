"""
Unit tests for Deep Search agents: Planner, Searcher, and Analyzer.
Tests individual agent functionality and coordination.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
import json

from v2.backend.services.deep_search.agents import (
    PlannerAgent, SearcherAgent, AnalyzerAgent, AgentOrchestrator,
    AgentResult, AgentState
)


class TestPlannerAgent:
    """Test the Planner Agent functionality"""

    @pytest.fixture
    def planner(self):
        """Create planner agent instance"""
        return PlannerAgent()

    def test_planner_initialization(self, planner):
        """Test planner agent initialization"""
        assert planner.name == "planner"
        assert planner.state == AgentState.IDLE
        assert hasattr(planner, 'personas')
        assert 'default' in planner.personas
        assert 'isaac' in planner.personas

    @pytest.mark.asyncio
    async def test_planner_execute_simple_query(self, planner):
        """Test planning a simple query"""
        input_data = {"query": "What is Python?"}

        result = await planner.execute(input_data)

        assert isinstance(result, AgentResult)
        assert result.success == True
        assert result.agent_name == "planner"
        assert result.state == AgentState.COMPLETED
        assert "research_plan" in result.data

        plan = result.data["research_plan"]
        assert "original_query" in plan
        assert "query_analysis" in plan
        assert "search_queries" in plan
        assert "execution_plan" in plan

    @pytest.mark.asyncio
    async def test_planner_execute_complex_query(self, planner):
        """Test planning a complex analytical query"""
        input_data = {
            "query": "Compare the performance of React vs Vue.js for enterprise applications"
        }

        result = await planner.execute(input_data)

        assert result.success == True
        plan = result.data["research_plan"]
        analysis = plan["query_analysis"]

        # Should identify as analytical and comparative
        assert analysis["query_type"] in ["analytical", "comparative"]
        assert analysis["complexity"] > 0.3  # Should be fairly complex

        # Should generate multiple search queries
        assert len(plan["search_queries"]) > 1

    def test_query_analysis(self, planner):
        """Test query analysis functionality"""
        # Simple query
        analysis = planner._analyze_query("What is AI?")
        assert analysis["complexity"] < 0.5
        assert analysis["query_type"] == "explanatory"

        # Complex query
        analysis = planner._analyze_query("Compare and contrast REST APIs with GraphQL")
        assert analysis["complexity"] > 0.4
        assert analysis["query_type"] == "comparative"

        # Technical query
        analysis = planner._analyze_query("How does Docker container networking work?")
        assert analysis["complexity"] > 0.3
        assert "technical_terms" in analysis["complexity_factors"]

    def test_research_approach_determination(self, planner):
        """Test research approach selection"""
        # Simple query -> quick approach
        simple_analysis = {"complexity": 0.2, "estimated_depth": "quick"}
        approach = planner._determine_research_approach(simple_analysis, {})
        assert approach["max_searches"] <= 3
        assert approach["validation_level"] == "basic"

        # Complex query -> comprehensive approach
        complex_analysis = {"complexity": 0.7, "estimated_depth": "comprehensive"}
        approach = planner._determine_research_approach(complex_analysis, {})
        assert approach["max_searches"] >= 3
        assert approach["validation_level"] == "cross_reference"

    def test_search_query_generation(self, planner):
        """Test search query generation"""
        queries = planner._generate_search_queries(
            "What is machine learning?",
            {"query_type": "explanatory", "complexity": 0.3}
        )

        assert len(queries) >= 1
        assert "What is machine learning?" in queries  # Original query included

        # Should generate variations for explanatory queries
        assert any("how to" in q.lower() for q in queries) or any("tutorial" in q.lower() for q in queries)

    def test_persona_guidance(self, planner):
        """Test persona guidance generation"""
        guidance = planner._get_persona_guidance("isaac")
        assert guidance["writing_style"] == "Isaac Asimov-style clear explanations"
        assert guidance["focus_area"] == "educational clarity and accessibility"
        assert "key_instructions" in guidance
        assert len(guidance["key_instructions"]) > 0

        # Test default persona
        guidance = planner._get_persona_guidance("nonexistent")
        assert guidance["writing_style"] == "balanced and comprehensive"


class TestSearcherAgent:
    """Test the Searcher Agent functionality"""

    @pytest.fixture
    def searcher(self):
        """Create searcher agent instance"""
        return SearcherAgent()

    @pytest.fixture
    def mock_search_engine(self):
        """Mock search engine"""
        engine = Mock()
        engine.search = AsyncMock(return_value=[
            Mock(title="Result 1", content="Content 1", similarity=0.9, id="1")
        ])
        engine.search_fulltext = AsyncMock(return_value=[])
        return engine

    @pytest.fixture
    def mock_db(self):
        """Mock database connection"""
        return Mock()

    def test_searcher_initialization(self, searcher):
        """Test searcher agent initialization"""
        assert searcher.name == "searcher"
        assert hasattr(searcher, 'search_strategies')
        assert len(searcher.search_strategies) > 0

    @pytest.mark.asyncio
    async def test_searcher_execute_basic(self, searcher, mock_search_engine, mock_db):
        """Test basic search execution"""
        input_data = {"query": "test search"}
        context = {"search_engine": mock_search_engine, "db": mock_db}

        result = await searcher.execute(input_data, context)

        assert isinstance(result, AgentResult)
        assert result.success == True
        assert result.agent_name == "searcher"
        assert "sources" in result.data
        assert "search_query" in result.data

    @pytest.mark.asyncio
    async def test_searcher_semantic_search(self, searcher, mock_search_engine, mock_db):
        """Test semantic search functionality"""
        mock_search_engine.search.return_value = [
            Mock(title="AI Guide", content="AI is...", similarity=0.95, id="1",
                 tags=["ai", "ml"], verified=True, created_at=datetime.now(), updated_at=datetime.now())
        ]

        input_data = {"query": "artificial intelligence"}
        context = {"search_engine": mock_search_engine, "db": mock_db}

        result = await searcher.execute(input_data, context)

        assert result.success == True
        sources = result.data["sources"]
        assert len(sources) > 0
        assert sources[0]["title"] == "AI Guide"
        assert sources[0]["relevance_score"] == 0.95
        assert sources[0]["search_method"] == "semantic"

    @pytest.mark.asyncio
    async def test_searcher_fallback_to_fulltext(self, searcher, mock_search_engine, mock_db):
        """Test fallback to full-text search"""
        # Semantic search returns no results
        mock_search_engine.search.return_value = []
        mock_search_engine.search_fulltext.return_value = [
            Mock(title="Backup Result", content="Content", id="2",
                 tags=[], verified=False, created_at=datetime.now(), updated_at=datetime.now())
        ]

        input_data = {"query": "test query"}
        context = {"search_engine": mock_search_engine, "db": mock_db}

        result = await searcher.execute(input_data, context)

        assert result.success == True
        sources = result.data["sources"]
        assert len(sources) > 0
        assert sources[0]["search_method"] == "fulltext"

    @pytest.mark.asyncio
    async def test_searcher_no_db_connection(self, searcher):
        """Test search without database connection"""
        input_data = {"query": "test"}
        context = {}  # No db

        result = await searcher.execute(input_data, context)

        assert result.success == False
        assert "Database connection" in result.error_message

    def test_source_deduplication(self, searcher):
        """Test source deduplication and ranking"""
        sources = [
            {"id": "1", "title": "Same Title", "relevance_score": 0.8},
            {"id": "2", "title": "Same Title", "relevance_score": 0.9},  # Different ID, same title
            {"id": "3", "title": "Different Title", "relevance_score": 0.7}
        ]

        deduplicated = searcher._deduplicate_and_rank(sources, "test query")

        # Should remove duplicates based on title
        assert len(deduplicated) <= len(sources)
        # Should be sorted by relevance (highest first)
        assert deduplicated[0]["relevance_score"] >= deduplicated[-1]["relevance_score"]

    def test_source_ranking_factors(self, searcher):
        """Test source ranking considers multiple factors"""
        sources = [
            {"id": "1", "title": "Old Source", "relevance_score": 0.8, "verified": False,
             "created_at": datetime(2020, 1, 1)},
            {"id": "2", "title": "New Verified Source", "relevance_score": 0.7, "verified": True,
             "created_at": datetime(2024, 1, 1)}
        ]

        ranked = searcher._deduplicate_and_rank(sources, "test")

        # Verified recent source should rank higher despite lower base score
        assert ranked[0]["id"] == "2"


class TestAnalyzerAgent:
    """Test the Analyzer Agent functionality"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer agent instance"""
        return AnalyzerAgent()

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer agent initialization"""
        assert analyzer.name == "analyzer"
        assert hasattr(analyzer, 'synthesis_strategies')
        assert len(analyzer.synthesis_strategies) > 0

    @pytest.mark.asyncio
    async def test_analyzer_execute_basic(self, analyzer):
        """Test basic analysis execution"""
        input_data = {
            "query": "What is AI?",
            "sources": [
                {"title": "AI Guide", "content": "AI is artificial intelligence", "id": "1"}
            ]
        }

        result = await analyzer.execute(input_data)

        assert isinstance(result, AgentResult)
        assert result.success == True
        assert result.agent_name == "analyzer"

    @pytest.mark.asyncio
    async def test_analyzer_no_sources(self, analyzer):
        """Test analyzer with no sources"""
        input_data = {"query": "test", "sources": []}

        result = await analyzer.execute(input_data)

        assert result.success == False
        assert "No sources provided" in result.error_message

    def test_source_validation(self, analyzer):
        """Test source validation and filtering"""
        sources = [
            {"id": "1", "title": "Good Source", "content": "Valid content", "score": 0.9},
            {"id": "2", "title": "Empty Source", "content": "", "score": 0.1},
            {"id": "3", "title": "Spam Source", "content": "Buy now!", "score": 0.2}
        ]

        validated = analyzer._validate_sources(sources)

        # Should filter out low-quality sources
        assert len(validated) <= len(sources)
        # Should keep high-quality sources
        assert any(s["id"] == "1" for s in validated)

    def test_key_information_extraction(self, analyzer):
        """Test key information extraction from sources"""
        sources = [
            {"title": "ML Guide", "content": "Machine learning is a subset of AI. It uses algorithms to learn patterns.", "id": "1"},
            {"title": "AI Overview", "content": "AI systems can perform tasks that typically require human intelligence.", "id": "2"}
        ]

        key_info = analyzer._extract_key_information(sources, "What is machine learning?")

        assert "main_points" in key_info
        assert len(key_info["main_points"]) > 0
        assert isinstance(key_info["main_points"][0], str)

    def test_information_validation(self, analyzer):
        """Test information cross-validation"""
        key_info = {
            "main_points": [
                "ML is a subset of AI",
                "AI performs intelligent tasks",
                "ML learns from data"
            ]
        }

        validation = analyzer._cross_validate_information(key_info)

        assert "reliability_score" in validation
        assert 0.0 <= validation["reliability_score"] <= 1.0

    def test_confidence_calculation(self, analyzer):
        """Test confidence score calculation"""
        sources = [{"id": "1"}, {"id": "2"}, {"id": "3"}]  # 3 sources
        validation = {"reliability_score": 0.8}
        answer = "Test synthesized answer"

        confidence = analyzer._calculate_confidence_score(sources, validation, answer)

        assert 0.0 <= confidence <= 1.0
        # Should be higher with more sources and higher validation score
        assert confidence > 0.5

    def test_quality_metrics_calculation(self, analyzer):
        """Test quality metrics calculation"""
        sources = [{"id": "1", "verified": True}, {"id": "2", "verified": False}]
        validation = {"reliability_score": 0.9}
        answer = "Comprehensive answer with multiple points covered"

        metrics = analyzer._calculate_quality_metrics(sources, validation, answer)

        assert "source_diversity" in metrics
        assert "information_depth" in metrics
        assert "factual_consistency" in metrics
        assert all(0.0 <= v <= 1.0 for v in metrics.values())


class TestAgentOrchestratorIntegration:
    """Test agent orchestrator integration"""

    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator for testing"""
        orch = AgentOrchestrator()
        yield orch
        # Cleanup if needed

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes all agents"""
        assert len(orchestrator.agents) == 3
        assert "planner" in orchestrator.agents
        assert "searcher" in orchestrator.agents
        assert "analyzer" in orchestrator.agents

    @pytest.mark.asyncio
    async def test_orchestrator_execute_research(self, orchestrator):
        """Test full research execution"""
        result = await orchestrator.execute_research("What is Python?", {"depth": "quick"})

        # Should return a dictionary with expected structure
        assert isinstance(result, dict)
        assert "query" in result
        assert "synthesized_answer" in result
        assert "confidence_score" in result

    def test_credit_calculation(self, orchestrator):
        """Test research credit calculation"""
        # Quick research
        credits = orchestrator.calculate_research_credits("quick", 1.0, 3)
        assert credits >= 5.0  # Base credits

        # Comprehensive research
        credits = orchestrator.calculate_research_credits("comprehensive", 2.0, 8)
        assert credits >= 15.0  # Base credits

        # Exhaustive research
        credits = orchestrator.calculate_research_credits("exhaustive", 5.0, 15)
        assert credits >= 25.0  # Base credits

    def test_agent_status_reporting(self, orchestrator):
        """Test agent status reporting"""
        status = orchestrator.get_agent_status()

        assert len(status) == 3
        for agent_status in status.values():
            assert "state" in agent_status
            assert "metrics" in agent_status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
