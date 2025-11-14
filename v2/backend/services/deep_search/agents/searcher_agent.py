"""
Searcher Agent for Deep Search System
Finds and retrieves relevant information from knowledge sources
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentResult, AgentState

logger = logging.getLogger(__name__)


class SearcherAgent(BaseAgent):
    """
    Agent responsible for searching and retrieving information

    Uses multiple search strategies:
    - Semantic search in knowledge base
    - Full-text search fallback
    - Related content discovery
    - Source validation and ranking
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("searcher", config)

    def _initialize(self):
        """Initialize searcher-specific components"""
        self.search_strategies = [
            "semantic_search",
            "fulltext_search",
            "related_search",
            "tag_based_search"
        ]

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> AgentResult:
        """
        Execute search for the given query

        Args:
            input_data: Contains query and search parameters
            context: Additional context including database connection

        Returns:
            AgentResult with found sources
        """
        query = input_data.get("query", "")
        context = context or {}
        db = context.get("db")

        if not db:
            return AgentResult(
                agent_name=self.name,
                state=AgentState.FAILED,
                data={},
                metadata={"error": "Database connection not provided"},
                execution_time=0.0,
                credits_used=0.0,
                success=False,
                error_message="Database connection required for search"
            )

        try:
            # Get search engine from context or initialize
            search_engine = context.get("search_engine")
            if not search_engine:
                from ..grokopedia.search import get_search_engine
                search_engine = get_search_engine()

            # Execute multi-strategy search
            all_sources = []

            # Strategy 1: Semantic search
            semantic_results = await self._execute_semantic_search(
                search_engine, query, db, context
            )
            all_sources.extend(semantic_results)

            # Strategy 2: Full-text search (if semantic fails or returns few results)
            if len(all_sources) < 3:
                fulltext_results = await self._execute_fulltext_search(
                    search_engine, query, db, context
                )
                all_sources.extend(fulltext_results)

            # Strategy 3: Related content search
            related_results = await self._execute_related_search(
                search_engine, query, db, all_sources, context
            )
            all_sources.extend(related_results)

            # Remove duplicates and rank results
            deduplicated_sources = self._deduplicate_and_rank(all_sources, query)

            # Limit results based on context
            max_sources = context.get("max_sources", 10)
            final_sources = deduplicated_sources[:max_sources]

            return AgentResult(
                agent_name=self.name,
                state=AgentState.COMPLETED,
                data={
                    "sources": final_sources,
                    "search_query": query,
                    "strategies_used": self.search_strategies[:3],  # Used first 3 strategies
                    "total_found": len(all_sources),
                    "final_count": len(final_sources)
                },
                metadata={
                    "query": query,
                    "search_strategies": len(self.search_strategies),
                    "sources_before_deduplication": len(all_sources),
                    "sources_after_deduplication": len(deduplicated_sources),
                    "final_sources_returned": len(final_sources)
                },
                execution_time=0.0,  # Will be set by base class
                credits_used=len(final_sources) * 0.1,  # 0.1 credits per source
                success=True
            )

        except Exception as e:
            logger.error(f"Search execution failed: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                state=AgentState.FAILED,
                data={},
                metadata={"error": str(e), "query": query},
                execution_time=0.0,
                credits_used=0.0,
                success=False,
                error_message=f"Search failed: {str(e)}"
            )

    async def _execute_semantic_search(self, search_engine, query: str, db, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute semantic search in knowledge base"""
        try:
            limit = context.get("search_limit", 10)
            results = await search_engine.search(
                query=query,
                db=db,
                limit=limit,
                verified_only=False
            )

            sources = []
            for result in results:
                sources.append({
                    "id": str(result.id) if hasattr(result, 'id') else result.get('id', ''),
                    "title": result.title,
                    "content": result.content,
                    "summary": getattr(result, 'summary', None),
                    "tags": getattr(result, 'tags', []) or [],
                    "verified": getattr(result, 'verified', False),
                    "relevance_score": getattr(result, 'similarity', 0.0) or 0.0,
                    "search_method": "semantic",
                    "created_at": getattr(result, 'created_at', datetime.utcnow()),
                    "updated_at": getattr(result, 'updated_at', datetime.utcnow())
                })

            return sources

        except Exception as e:
            logger.warning(f"Semantic search failed: {e}")
            return []

    async def _execute_fulltext_search(self, search_engine, query: str, db, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute full-text search as fallback"""
        try:
            limit = context.get("search_limit", 10)
            results = await search_engine.search_fulltext(query, db, limit)

            sources = []
            for result in results:
                sources.append({
                    "id": str(result.id) if hasattr(result, 'id') else result.get('id', ''),
                    "title": result.title,
                    "content": result.content,
                    "summary": getattr(result, 'summary', None),
                    "tags": getattr(result, 'tags', []) or [],
                    "verified": getattr(result, 'verified', False),
                    "relevance_score": 0.5,  # Lower default score for fulltext
                    "search_method": "fulltext",
                    "created_at": getattr(result, 'created_at', datetime.utcnow()),
                    "updated_at": getattr(result, 'updated_at', datetime.utcnow())
                })

            return sources

        except Exception as e:
            logger.warning(f"Full-text search failed: {e}")
            return []

    async def _execute_related_search(self, search_engine, query: str, db, existing_sources: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find related content based on existing sources"""
        related_sources = []

        try:
            # Extract tags from top existing sources
            all_tags = []
            for source in existing_sources[:3]:  # Use top 3 sources
                all_tags.extend(source.get('tags', []))

            # Remove duplicates
            unique_tags = list(set(all_tags))[:5]  # Limit to 5 tags

            # Search by tags
            if unique_tags:
                tag_query = " ".join(unique_tags)
                tag_results = await search_engine.search(
                    query=tag_query,
                    db=db,
                    limit=5,
                    verified_only=False
                )

                for result in tag_results:
                    # Avoid duplicates
                    result_id = str(result.id) if hasattr(result, 'id') else result.get('id', '')
                    if not any(s['id'] == result_id for s in existing_sources):
                        related_sources.append({
                            "id": result_id,
                            "title": result.title,
                            "content": result.content,
                            "summary": getattr(result, 'summary', None),
                            "tags": getattr(result, 'tags', []) or [],
                            "verified": getattr(result, 'verified', False),
                            "relevance_score": 0.3,  # Lower score for related content
                            "search_method": "related",
                            "created_at": getattr(result, 'created_at', datetime.utcnow()),
                            "updated_at": getattr(result, 'updated_at', datetime.utcnow())
                        })

        except Exception as e:
            logger.warning(f"Related search failed: {e}")

        return related_sources

    def _deduplicate_and_rank(self, sources: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Remove duplicates and rank sources by relevance"""
        if not sources:
            return []

        # Remove duplicates based on ID
        seen_ids = set()
        deduplicated = []

        for source in sources:
            source_id = source.get('id', '')
            if source_id and source_id not in seen_ids:
                seen_ids.add(source_id)
                deduplicated.append(source)

        # Rank by relevance score, then by verification status, then by recency
        def sort_key(source):
            score = source.get('relevance_score', 0.0)
            verified_bonus = 0.2 if source.get('verified', False) else 0.0
            # Recency bonus (newer content gets slight preference)
            created_at = source.get('created_at', datetime.utcnow())
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_old = (datetime.utcnow() - created_at).days
            recency_bonus = max(0, 0.1 - (days_old / 365) * 0.1)  # Up to 0.1 bonus for very recent content

            return score + verified_bonus + recency_bonus

        ranked = sorted(deduplicated, key=sort_key, reverse=True)

        return ranked