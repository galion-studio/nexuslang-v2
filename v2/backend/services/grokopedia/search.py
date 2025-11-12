"""
Grokopedia - Semantic Search Implementation
Uses embeddings and vector similarity for intelligent search.
Now powered by AI Router for multi-model support.
"""

from typing import List, Dict, Any, Optional
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import openai

from ...core.config import settings
from ..ai import get_ai_router


class SemanticSearch:
    """
    Semantic search engine for Grokopedia.
    Uses AI Router for embeddings and enhanced search with multi-model support.
    """
    
    def __init__(self):
        # Use OpenAI client for embeddings (specialized task)
        self.openai_client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY or settings.OPENROUTER_API_KEY
        )
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dim = 1536
        
        # Use AI Router for enhanced search and summarization
        self.ai_router = get_ai_router()
    
    async def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding vector for text using OpenAI.
        """
        response = await self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    async def search(
        self,
        query: str,
        db: AsyncSession,
        limit: int = 10,
        verified_only: bool = False,
        tags: Optional[List[str]] = None,
        use_ai_enhancement: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search on knowledge base.
        
        Args:
            query: Natural language search query
            db: Database session
            limit: Maximum results to return
            verified_only: Only return verified entries
            tags: Filter by tags
            use_ai_enhancement: Use AI to enhance/expand the search query
        
        Returns:
            List of matching knowledge entries
        """
        # Optionally enhance query with AI before searching
        search_query = query
        if use_ai_enhancement and self.ai_router:
            try:
                enhanced = await self.ai_router.quick_response(
                    f"Expand this search query with related terms and concepts: {query}",
                    system_message="You are a search query enhancement assistant. Return only the enhanced query, no explanations."
                )
                search_query = enhanced
            except Exception as e:
                print(f"AI enhancement failed, using original query: {e}")
                search_query = query
        
        # Create embedding for query
        query_embedding = await self.create_embedding(search_query)
        
        # Build SQL query with vector similarity
        # Using pgvector's <-> operator for cosine similarity
        from ...models.knowledge import KnowledgeEntry
        
        stmt = select(
            KnowledgeEntry,
            func.cosine_similarity(
                KnowledgeEntry.embeddings,
                query_embedding
            ).label('similarity')
        )
        
        # Apply filters
        if verified_only:
            stmt = stmt.where(KnowledgeEntry.verified == True)
        
        if tags:
            stmt = stmt.where(KnowledgeEntry.tags.contains(tags))
        
        # Order by similarity and limit
        stmt = stmt.order_by('similarity DESC').limit(limit)
        
        # Execute query
        result = await db.execute(stmt)
        rows = result.all()
        
        # Format results
        entries = []
        for row in rows:
            entry = row.KnowledgeEntry
            entries.append({
                'id': str(entry.id),
                'title': entry.title,
                'slug': entry.slug,
                'summary': entry.summary,
                'content': entry.content,
                'tags': entry.tags,
                'verified': entry.verified,
                'similarity': row.similarity,
                'views_count': entry.views_count,
                'upvotes_count': entry.upvotes_count
            })
        
        return entries
    
    async def search_fulltext(
        self,
        query: str,
        db: AsyncSession,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform full-text search (fallback for simple queries).
        Faster than semantic search but less intelligent.
        """
        from ...models.knowledge import KnowledgeEntry
        
        # PostgreSQL full-text search
        stmt = select(KnowledgeEntry).where(
            func.to_tsvector('english', KnowledgeEntry.content).match(query)
        ).limit(limit)
        
        result = await db.execute(stmt)
        entries = result.scalars().all()
        
        return [
            {
                'id': str(entry.id),
                'title': entry.title,
                'slug': entry.slug,
                'summary': entry.summary,
                'tags': entry.tags,
                'verified': entry.verified
            }
            for entry in entries
        ]
    
    async def get_related_entries(
        self,
        entry_id: str,
        db: AsyncSession,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get entries related to a given entry.
        Uses knowledge graph relationships.
        """
        from ...models.knowledge import KnowledgeEntry, KnowledgeGraph
        
        # Query knowledge graph
        stmt = select(KnowledgeEntry).join(
            KnowledgeGraph,
            KnowledgeGraph.target_id == KnowledgeEntry.id
        ).where(
            KnowledgeGraph.source_id == entry_id
        ).order_by(
            KnowledgeGraph.weight.desc()
        ).limit(limit)
        
        result = await db.execute(stmt)
        entries = result.scalars().all()
        
        return [
            {
                'id': str(entry.id),
                'title': entry.title,
                'summary': entry.summary,
                'relationship': 'related_to'  # TODO: Get actual relationship type
            }
            for entry in entries
        ]
    
    async def suggest_queries(self, partial_query: str, limit: int = 5) -> List[str]:
        """
        Suggest query completions based on partial input.
        """
        # TODO: Implement query suggestion
        # Could use:
        # - Common queries database
        # - Entry titles
        # - AI-generated suggestions
        
        suggestions = [
            f"{partial_query} definition",
            f"{partial_query} examples",
            f"{partial_query} applications",
            f"how does {partial_query} work",
            f"{partial_query} vs alternatives"
        ]
        
        return suggestions[:limit]


# Global search engine instance
_search_engine = None


def get_search_engine() -> SemanticSearch:
    """Get or create the global search engine."""
    global _search_engine
    if _search_engine is None:
        _search_engine = SemanticSearch()
    return _search_engine

