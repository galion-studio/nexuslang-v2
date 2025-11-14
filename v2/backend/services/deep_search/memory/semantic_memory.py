"""
Semantic Memory System for Deep Search
Based on MushroomFleet/deep-search-persona architecture

Provides intelligent storage and retrieval of research findings using:
- Embedding-based similarity search
- Tag-based organization
- Temporal decay and relevance scoring
- Memory consolidation and optimization
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np

from ...ai.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


@dataclass
class MemoryItem:
    """Represents a single item in semantic memory"""
    id: str
    content: str
    embedding: np.ndarray
    metadata: Dict[str, Any]
    importance_score: float
    access_count: int
    created_at: datetime
    last_accessed: datetime
    tags: List[str]
    source: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['embedding'] = self.embedding.tolist()
        data['created_at'] = self.created_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Create from dictionary"""
        data['embedding'] = np.array(data['embedding'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)


@dataclass
class SearchResult:
    """Result from semantic memory search"""
    item: MemoryItem
    similarity_score: float
    relevance_score: float


class SemanticMemory:
    """
    Semantic memory system for storing and retrieving research findings

    Features:
    - Vector-based similarity search
    - Importance-based memory management
    - Temporal relevance decay
    - Tag-based organization
    - Memory consolidation
    """

    def __init__(self, embedding_service: Optional[EmbeddingService] = None,
                 max_memory_items: int = 10000, cache_enabled: bool = True):
        self.embedding_service = embedding_service or EmbeddingService()
        self.max_memory_items = max_memory_items
        self.cache_enabled = cache_enabled

        # Memory storage
        self.memory_items: Dict[str, MemoryItem] = {}
        self.memory_index: Dict[str, np.ndarray] = {}  # For fast similarity search

        # Cache for recent searches
        self.search_cache: Dict[str, List[SearchResult]] = {}
        self.cache_timestamps: Dict[str, datetime] = {}

        logger.info(f"Initialized semantic memory with max {max_memory_items} items")

    async def store(self, content: str, metadata: Dict[str, Any] = None,
                   tags: List[str] = None, source: str = "unknown") -> str:
        """
        Store content in semantic memory

        Args:
            content: Text content to store
            metadata: Additional metadata
            tags: Tags for organization
            source: Source identifier

        Returns:
            Memory item ID
        """
        try:
            metadata = metadata or {}
            tags = tags or []

            # Generate embedding
            embedding = await self.embedding_service.encode_single(content)

            # Create memory item
            item_id = f"mem_{int(time.time())}_{hash(content) % 10000}"
            importance_score = self._calculate_importance(content, metadata, tags)

            item = MemoryItem(
                id=item_id,
                content=content,
                embedding=embedding,
                metadata=metadata,
                importance_score=importance_score,
                access_count=0,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                tags=tags,
                source=source
            )

            # Store in memory
            self.memory_items[item_id] = item
            self.memory_index[item_id] = embedding

            # Manage memory size
            await self._manage_memory_size()

            logger.info(f"Stored memory item: {item_id} (importance: {importance_score:.2f})")
            return item_id

        except Exception as e:
            logger.error(f"Failed to store memory item: {e}")
            raise

    async def search(self, query: str, top_k: int = 5, threshold: float = 0.0,
                    tags: List[str] = None, source_filter: str = None) -> List[SearchResult]:
        """
        Search semantic memory for similar content

        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            tags: Filter by tags
            source_filter: Filter by source

        Returns:
            List of search results ordered by relevance
        """
        try:
            # Check cache first
            cache_key = f"{query}_{top_k}_{threshold}_{tags}_{source_filter}"
            if self.cache_enabled and self._is_cache_valid(cache_key):
                return self.search_cache[cache_key]

            # Generate query embedding
            query_embedding = await self.embedding_service.encode_single(query)

            # Filter candidates
            candidates = self._filter_candidates(tags, source_filter)

            if not candidates:
                return []

            # Calculate similarities
            similarities = []
            for item_id, item in candidates.items():
                similarity = self._cosine_similarity(query_embedding, item.embedding)

                if similarity >= threshold:
                    # Calculate relevance score (combination of similarity and other factors)
                    relevance = self._calculate_relevance_score(item, similarity, query)
                    similarities.append((item, similarity, relevance))

            # Sort by relevance score
            similarities.sort(key=lambda x: x[2], reverse=True)

            # Convert to SearchResult objects
            results = []
            for item, similarity, relevance in similarities[:top_k]:
                result = SearchResult(
                    item=item,
                    similarity_score=similarity,
                    relevance_score=relevance
                )
                results.append(result)

                # Update access statistics
                await self._update_access_stats(item.id)

            # Cache results
            if self.cache_enabled:
                self.search_cache[cache_key] = results
                self.cache_timestamps[cache_key] = datetime.utcnow()

            logger.info(f"Semantic search completed: {len(results)} results for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    async def consolidate_memories(self) -> int:
        """
        Consolidate similar memories to reduce redundancy

        Returns:
            Number of memories consolidated
        """
        try:
            consolidated_count = 0

            # Group similar memories
            similarity_groups = await self._find_similar_groups(threshold=0.85)

            for group in similarity_groups:
                if len(group) > 1:
                    # Merge group into single consolidated memory
                    await self._consolidate_group(group)
                    consolidated_count += len(group) - 1  # Count removed items

            logger.info(f"Memory consolidation completed: {consolidated_count} items consolidated")
            return consolidated_count

        except Exception as e:
            logger.error(f"Memory consolidation failed: {e}")
            return 0

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        total_items = len(self.memory_items)
        if total_items == 0:
            return {"total_items": 0, "stats": "No items in memory"}

        # Calculate statistics
        importance_scores = [item.importance_score for item in self.memory_items.values()]
        access_counts = [item.access_count for item in self.memory_items.values()]

        # Tag distribution
        tag_counts = {}
        for item in self.memory_items.values():
            for tag in item.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Source distribution
        source_counts = {}
        for item in self.memory_items.values():
            source_counts[item.source] = source_counts.get(item.source, 0) + 1

        # Age distribution
        now = datetime.utcnow()
        age_days = [(now - item.created_at).days for item in self.memory_items.values()]

        return {
            "total_items": total_items,
            "average_importance": sum(importance_scores) / len(importance_scores),
            "max_importance": max(importance_scores),
            "min_importance": min(importance_scores),
            "total_accesses": sum(access_counts),
            "average_accesses": sum(access_counts) / len(access_counts),
            "tag_distribution": dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "source_distribution": dict(sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "average_age_days": sum(age_days) / len(age_days),
            "oldest_item_days": max(age_days),
            "newest_item_days": min(age_days)
        }

    def _calculate_importance(self, content: str, metadata: Dict[str, Any], tags: List[str]) -> float:
        """Calculate importance score for memory item"""
        base_score = 0.5

        # Content length factor
        length_factor = min(len(content) / 1000, 1.0) * 0.2

        # Metadata richness factor
        metadata_factor = min(len(metadata) / 5, 1.0) * 0.1

        # Tag factor
        tag_factor = min(len(tags) / 3, 1.0) * 0.1

        # Keyword importance (would be enhanced with domain knowledge)
        important_keywords = ['research', 'analysis', 'finding', 'conclusion', 'result']
        keyword_factor = 0.0
        content_lower = content.lower()
        for keyword in important_keywords:
            if keyword in content_lower:
                keyword_factor += 0.1
        keyword_factor = min(keyword_factor, 0.2)

        importance = base_score + length_factor + metadata_factor + tag_factor + keyword_factor
        return min(importance, 1.0)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def _filter_candidates(self, tags: List[str] = None, source_filter: str = None) -> Dict[str, MemoryItem]:
        """Filter memory items based on criteria"""
        candidates = self.memory_items.copy()

        # Filter by tags
        if tags:
            filtered = {}
            for item_id, item in candidates.items():
                if any(tag in item.tags for tag in tags):
                    filtered[item_id] = item
            candidates = filtered

        # Filter by source
        if source_filter:
            candidates = {
                item_id: item for item_id, item in candidates.items()
                if item.source == source_filter
            }

        return candidates

    def _calculate_relevance_score(self, item: MemoryItem, similarity: float, query: str) -> float:
        """Calculate relevance score combining multiple factors"""
        # Base similarity score
        base_score = similarity * 0.5

        # Importance factor
        importance_factor = item.importance_score * 0.2

        # Recency factor (newer items get slight boost)
        days_old = (datetime.utcnow() - item.created_at).days
        recency_factor = max(0, 0.1 - (days_old / 365) * 0.1)

        # Access frequency factor
        access_factor = min(item.access_count / 10, 1.0) * 0.1

        # Tag relevance (would be enhanced with query analysis)
        tag_factor = 0.1 if item.tags else 0.0

        relevance = base_score + importance_factor + recency_factor + access_factor + tag_factor
        return min(relevance, 1.0)

    async def _update_access_stats(self, item_id: str):
        """Update access statistics for memory item"""
        if item_id in self.memory_items:
            item = self.memory_items[item_id]
            item.access_count += 1
            item.last_accessed = datetime.utcnow()

    async def _manage_memory_size(self):
        """Manage memory size by removing least important items if needed"""
        if len(self.memory_items) <= self.max_memory_items:
            return

        # Sort by importance score (considering recency and access)
        def importance_key(item):
            base_importance = item.importance_score
            recency_bonus = min((datetime.utcnow() - item.created_at).days / 30, 1.0) * 0.1
            access_bonus = min(item.access_count / 5, 1.0) * 0.1
            return base_importance + recency_bonus + access_bonus

        sorted_items = sorted(self.memory_items.values(), key=importance_key, reverse=True)

        # Keep top items, remove others
        items_to_keep = sorted_items[:self.max_memory_items]
        items_to_remove = sorted_items[self.max_memory_items:]

        # Remove from storage
        for item in items_to_remove:
            del self.memory_items[item.id]
            del self.memory_index[item.id]

        logger.info(f"Memory management: removed {len(items_to_remove)} items, kept {len(items_to_keep)}")

    async def _find_similar_groups(self, threshold: float = 0.85) -> List[List[MemoryItem]]:
        """Find groups of similar memories for consolidation"""
        groups = []
        processed_ids = set()

        for item_id, item in self.memory_items.items():
            if item_id in processed_ids:
                continue

            group = [item]
            processed_ids.add(item_id)

            # Find similar items
            for other_id, other_item in self.memory_items.items():
                if other_id not in processed_ids:
                    similarity = self._cosine_similarity(item.embedding, other_item.embedding)
                    if similarity >= threshold:
                        group.append(other_item)
                        processed_ids.add(other_id)

            if len(group) > 1:
                groups.append(group)

        return groups

    async def _consolidate_group(self, group: List[MemoryItem]):
        """Consolidate a group of similar memories into one"""
        if len(group) <= 1:
            return

        # Sort by importance and recency
        group.sort(key=lambda x: (x.importance_score, x.created_at), reverse=True)
        primary_item = group[0]

        # Combine content and metadata
        combined_content = primary_item.content
        combined_tags = list(set(primary_item.tags))
        combined_metadata = primary_item.metadata.copy()

        # Merge information from other items
        for item in group[1:]:
            if len(combined_content) + len(item.content) < 2000:  # Reasonable limit
                combined_content += f"\n\nAdditional info: {item.content}"
            combined_tags.extend(item.tags)
            combined_metadata.update(item.metadata)

        # Remove duplicates from tags
        combined_tags = list(set(combined_tags))

        # Update primary item
        primary_item.content = combined_content
        primary_item.tags = combined_tags
        primary_item.metadata = combined_metadata
        primary_item.importance_score = min(primary_item.importance_score + 0.1, 1.0)  # Slight boost

        # Regenerate embedding for consolidated content
        new_embedding = await self.embedding_service.encode_single(combined_content)
        primary_item.embedding = new_embedding
        self.memory_index[primary_item.id] = new_embedding

        # Remove other items
        for item in group[1:]:
            del self.memory_items[item.id]
            del self.memory_index[item.id]

        logger.info(f"Consolidated {len(group)} memories into one")

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache_timestamps:
            return False

        # Cache valid for 5 minutes
        cache_age = datetime.utcnow() - self.cache_timestamps[cache_key]
        return cache_age < timedelta(minutes=5)
