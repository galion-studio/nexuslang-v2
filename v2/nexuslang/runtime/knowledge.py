"""
NexusLang v2 - Knowledge Integration
Connects NexusLang to Grokopedia knowledge base.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import httpx
import asyncio


@dataclass
class KnowledgeEntry:
    """
    Represents a single knowledge entry from Grokopedia.
    """
    id: str
    title: str
    summary: str
    content: str
    tags: List[str]
    verified: bool
    confidence: float
    related_concepts: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'content': self.content,
            'tags': self.tags,
            'verified': self.verified,
            'confidence': self.confidence,
            'related_concepts': self.related_concepts
        }


class KnowledgeClient:
    """
    Client for querying the Grokopedia knowledge base.
    """
    
    def __init__(self, api_url: str = "http://localhost:8000/api/v2/grokopedia"):
        self.api_url = api_url
        self.cache = {}  # Simple in-memory cache
    
    async def query(self, query_text: str, filters: Optional[Dict] = None) -> List[KnowledgeEntry]:
        """
        Query the knowledge base.
        
        Args:
            query_text: Natural language query
            filters: Optional filters (tags, verified_only, etc.)
        
        Returns:
            List of knowledge entries
        """
        # Check cache first
        cache_key = f"{query_text}:{filters}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/search",
                params={
                    'q': query_text,
                    **(filters or {})
                }
            )
            response.raise_for_status()
            data = response.json()
        
        # Parse results
        entries = []
        for item in data.get('results', []):
            entry = KnowledgeEntry(
                id=item['id'],
                title=item['title'],
                summary=item.get('summary', ''),
                content=item.get('content', ''),
                tags=item.get('tags', []),
                verified=item.get('verified', False),
                confidence=item.get('ai_confidence', 0.5),
                related_concepts=item.get('related', [])
            )
            entries.append(entry)
        
        # Cache results
        self.cache[cache_key] = entries
        
        return entries
    
    async def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """
        Get a specific knowledge entry by ID.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/entries/{entry_id}")
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            data = response.json()
        
        return KnowledgeEntry(
            id=data['id'],
            title=data['title'],
            summary=data.get('summary', ''),
            content=data.get('content', ''),
            tags=data.get('tags', []),
            verified=data.get('verified', False),
            confidence=data.get('ai_confidence', 0.5),
            related_concepts=data.get('related', [])
        )
    
    async def get_related(self, concept: str) -> Dict[str, Any]:
        """
        Get knowledge graph for a concept.
        Returns related concepts and relationships.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/graph/{concept}")
            response.raise_for_status()
            return response.json()
    
    def clear_cache(self):
        """Clear the query cache."""
        self.cache.clear()


# Synchronous wrapper functions for use in NexusLang programs

_knowledge_client = None


def get_knowledge_client() -> KnowledgeClient:
    """Get or create the global knowledge client."""
    global _knowledge_client
    if _knowledge_client is None:
        _knowledge_client = KnowledgeClient()
    return _knowledge_client


def knowledge(query: str, **filters) -> List[Dict[str, Any]]:
    """
    Synchronous knowledge query function for NexusLang.
    
    Example:
        let facts = knowledge("quantum physics")
        let verified_only = knowledge("AI", verified=true)
    """
    client = get_knowledge_client()
    
    # Run async query in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        entries = loop.run_until_complete(client.query(query, filters))
        return [entry.to_dict() for entry in entries]
    finally:
        loop.close()


def knowledge_get(entry_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific knowledge entry by ID.
    
    Example:
        let entry = knowledge_get("quantum-entanglement")
    """
    client = get_knowledge_client()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        entry = loop.run_until_complete(client.get_entry(entry_id))
        return entry.to_dict() if entry else None
    finally:
        loop.close()


def knowledge_related(concept: str) -> Dict[str, Any]:
    """
    Get related concepts from knowledge graph.
    
    Example:
        let related = knowledge_related("machine learning")
    """
    client = get_knowledge_client()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(client.get_related(concept))
    finally:
        loop.close()


# Helper functions for knowledge manipulation

def summarize_knowledge(entries: List[Dict]) -> str:
    """
    Create a summary from multiple knowledge entries.
    """
    if not entries:
        return "No knowledge found."
    
    summaries = []
    for entry in entries[:5]:  # Top 5 results
        title = entry.get('title', 'Unknown')
        summary = entry.get('summary', '')
        verified = "✓" if entry.get('verified') else "?"
        
        summaries.append(f"{verified} {title}: {summary}")
    
    return "\n".join(summaries)


def filter_verified(entries: List[Dict]) -> List[Dict]:
    """
    Filter to only verified knowledge entries.
    """
    return [e for e in entries if e.get('verified', False)]


def filter_by_confidence(entries: List[Dict], min_confidence: float = 0.7) -> List[Dict]:
    """
    Filter entries by minimum confidence score.
    """
    return [e for e in entries if e.get('confidence', 0) >= min_confidence]


def extract_facts(entries: List[Dict]) -> List[str]:
    """
    Extract key facts from knowledge entries.
    """
    facts = []
    for entry in entries:
        content = entry.get('content', '')
        # Simple extraction: split by sentences
        sentences = content.split('.')
        for sentence in sentences[:3]:  # First 3 sentences
            if len(sentence.strip()) > 20:
                facts.append(sentence.strip())
    
    return facts

