"""
Grokopedia API routes.
Handles knowledge base search, entries, and contributions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Optional, List
from datetime import datetime
import uuid
import re

from ..core.database import get_db
from ..models.user import User
from ..models.knowledge import KnowledgeEntry, KnowledgeGraph, Contribution, RelationshipType, ContributionType
from ..api.auth import get_current_user, get_optional_user
from ..services.grokopedia.search import get_search_engine

router = APIRouter()


# Request/Response Models
class SearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 10
    verified_only: Optional[bool] = False
    tags: Optional[List[str]] = None


class CreateEntryRequest(BaseModel):
    title: str
    summary: Optional[str] = None
    content: str
    tags: Optional[List[str]] = None


class UpdateEntryRequest(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class EntryResponse(BaseModel):
    id: str
    title: str
    slug: str
    summary: Optional[str]
    content: str
    tags: List[str]
    verified: bool
    views_count: int
    upvotes_count: int
    created_at: datetime
    updated_at: datetime
    similarity: Optional[float] = None
    
    class Config:
        from_attributes = True


class KnowledgeGraphNode(BaseModel):
    id: str
    title: str
    summary: Optional[str]


class KnowledgeGraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    weight: float


class KnowledgeGraphResponse(BaseModel):
    center_node: KnowledgeGraphNode
    nodes: List[KnowledgeGraphNode]
    edges: List[KnowledgeGraphEdge]


# Search Endpoints
@router.get("/search")
async def search_knowledge(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    verified_only: bool = False,
    tags: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Search the knowledge base using semantic search.
    
    Uses OpenAI embeddings and vector similarity for intelligent search results.
    """
    search_engine = get_search_engine()
    
    # Parse tags if provided
    tag_list = tags.split(',') if tags else None
    
    try:
        results = await search_engine.search(
            query=q,
            db=db,
            limit=limit,
            verified_only=verified_only,
            tags=tag_list
        )
        
        return {
            "results": results,
            "total": len(results),
            "query": q
        }
    except Exception as e:
        # Fallback to full-text search if semantic search fails
        print(f"Semantic search failed: {e}. Falling back to full-text search.")
        results = await search_engine.search_fulltext(q, db, limit)
        return {
            "results": results,
            "total": len(results),
            "query": q,
            "fallback": True
        }


@router.get("/suggest")
async def suggest_queries(
    q: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=10)
):
    """
    Get query suggestions based on partial input.
    """
    search_engine = get_search_engine()
    suggestions = await search_engine.suggest_queries(q, limit)
    
    return {"suggestions": suggestions}


# Entry Endpoints
@router.get("/entries/{entry_id}", response_model=EntryResponse)
async def get_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get a knowledge entry by ID.
    Increments view count.
    """
    result = await db.execute(
        select(KnowledgeEntry).where(KnowledgeEntry.id == uuid.UUID(entry_id))
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )
    
    # Increment view count
    entry.views_count += 1
    await db.commit()
    
    return EntryResponse(
        id=str(entry.id),
        title=entry.title,
        slug=entry.slug,
        summary=entry.summary,
        content=entry.content,
        tags=entry.tags or [],
        verified=entry.verified,
        views_count=entry.views_count,
        upvotes_count=entry.upvotes_count,
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )


@router.get("/entries/slug/{slug}", response_model=EntryResponse)
async def get_entry_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get a knowledge entry by slug (URL-friendly identifier).
    """
    result = await db.execute(
        select(KnowledgeEntry).where(KnowledgeEntry.slug == slug)
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )
    
    # Increment view count
    entry.views_count += 1
    await db.commit()
    
    return EntryResponse(
        id=str(entry.id),
        title=entry.title,
        slug=entry.slug,
        summary=entry.summary,
        content=entry.content,
        tags=entry.tags or [],
        verified=entry.verified,
        views_count=entry.views_count,
        upvotes_count=entry.upvotes_count,
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )


@router.post("/entries", response_model=EntryResponse)
async def create_entry(
    request: CreateEntryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new knowledge entry.
    Automatically generates embedding for semantic search.
    """
    # Generate slug from title
    slug = re.sub(r'[^a-z0-9]+', '-', request.title.lower()).strip('-')
    
    # Check if slug already exists
    existing = await db.execute(
        select(KnowledgeEntry).where(KnowledgeEntry.slug == slug)
    )
    if existing.scalar_one_or_none():
        # Add a suffix to make it unique
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"
    
    # Generate embedding
    search_engine = get_search_engine()
    embedding_text = f"{request.title}\n\n{request.summary or ''}\n\n{request.content}"
    embedding = await search_engine.create_embedding(embedding_text)
    
    # Create entry
    entry = KnowledgeEntry(
        title=request.title,
        slug=slug,
        summary=request.summary,
        content=request.content,
        embeddings=embedding,
        tags=request.tags or [],
        created_by=current_user.id,
        verified=False  # Requires verification
    )
    
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    
    # Create contribution record
    contribution = Contribution(
        entry_id=entry.id,
        user_id=current_user.id,
        type=ContributionType.CREATE,
        changes={"action": "created"}
    )
    db.add(contribution)
    await db.commit()
    
    return EntryResponse(
        id=str(entry.id),
        title=entry.title,
        slug=entry.slug,
        summary=entry.summary,
        content=entry.content,
        tags=entry.tags or [],
        verified=entry.verified,
        views_count=entry.views_count,
        upvotes_count=entry.upvotes_count,
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )


@router.put("/entries/{entry_id}", response_model=EntryResponse)
async def update_entry(
    entry_id: str,
    request: UpdateEntryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a knowledge entry.
    Regenerates embedding if content changes.
    """
    result = await db.execute(
        select(KnowledgeEntry).where(KnowledgeEntry.id == uuid.UUID(entry_id))
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )
    
    changes = {}
    
    # Update fields
    if request.title and request.title != entry.title:
        changes['title'] = {'from': entry.title, 'to': request.title}
        entry.title = request.title
        # Regenerate slug
        entry.slug = re.sub(r'[^a-z0-9]+', '-', request.title.lower()).strip('-')
    
    if request.summary is not None and request.summary != entry.summary:
        changes['summary'] = {'from': entry.summary, 'to': request.summary}
        entry.summary = request.summary
    
    if request.content and request.content != entry.content:
        changes['content'] = {'from': entry.content[:100] + '...', 'to': request.content[:100] + '...'}
        entry.content = request.content
    
    if request.tags is not None:
        changes['tags'] = {'from': entry.tags, 'to': request.tags}
        entry.tags = request.tags
    
    # Regenerate embedding if content changed
    if request.content or request.title or request.summary:
        search_engine = get_search_engine()
        embedding_text = f"{entry.title}\n\n{entry.summary or ''}\n\n{entry.content}"
        entry.embeddings = await search_engine.create_embedding(embedding_text)
    
    entry.updated_at = datetime.utcnow()
    # Reset verification after edit
    entry.verified = False
    
    await db.commit()
    await db.refresh(entry)
    
    # Create contribution record
    contribution = Contribution(
        entry_id=entry.id,
        user_id=current_user.id,
        type=ContributionType.EDIT,
        changes=changes
    )
    db.add(contribution)
    await db.commit()
    
    return EntryResponse(
        id=str(entry.id),
        title=entry.title,
        slug=entry.slug,
        summary=entry.summary,
        content=entry.content,
        tags=entry.tags or [],
        verified=entry.verified,
        views_count=entry.views_count,
        upvotes_count=entry.upvotes_count,
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )


# Related Entries
@router.get("/entries/{entry_id}/related")
async def get_related_entries(
    entry_id: str,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Get entries related to a given entry via knowledge graph.
    """
    search_engine = get_search_engine()
    related = await search_engine.get_related_entries(entry_id, db, limit)
    
    return {"related": related, "total": len(related)}


# Knowledge Graph
@router.get("/graph/{entry_id}", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(
    entry_id: str,
    depth: int = Query(1, ge=1, le=3),
    db: AsyncSession = Depends(get_db)
):
    """
    Get knowledge graph visualization data for an entry.
    Returns nodes and edges for visualization.
    """
    # Get center entry
    result = await db.execute(
        select(KnowledgeEntry).where(KnowledgeEntry.id == uuid.UUID(entry_id))
    )
    center_entry = result.scalar_one_or_none()
    
    if not center_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )
    
    # Get connected nodes
    graph_result = await db.execute(
        select(KnowledgeGraph).where(
            KnowledgeGraph.source_id == uuid.UUID(entry_id)
        ).limit(20)
    )
    graph_edges = graph_result.scalars().all()
    
    # Fetch target entries
    target_ids = [edge.target_id for edge in graph_edges]
    if target_ids:
        entries_result = await db.execute(
            select(KnowledgeEntry).where(KnowledgeEntry.id.in_(target_ids))
        )
        target_entries = entries_result.scalars().all()
    else:
        target_entries = []
    
    # Build response
    center_node = KnowledgeGraphNode(
        id=str(center_entry.id),
        title=center_entry.title,
        summary=center_entry.summary
    )
    
    nodes = [
        KnowledgeGraphNode(
            id=str(entry.id),
            title=entry.title,
            summary=entry.summary
        )
        for entry in target_entries
    ]
    
    edges = [
        KnowledgeGraphEdge(
            source=str(edge.source_id),
            target=str(edge.target_id),
            relationship=edge.relationship.value,
            weight=edge.weight
        )
        for edge in graph_edges
    ]
    
    return KnowledgeGraphResponse(
        center_node=center_node,
        nodes=nodes,
        edges=edges
    )


# Tags
@router.get("/tags")
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get popular tags from the knowledge base.
    """
    # Query to get all tags and count occurrences
    result = await db.execute(
        select(func.unnest(KnowledgeEntry.tags).label('tag'), func.count().label('count'))
        .group_by('tag')
        .order_by(func.count().desc())
        .limit(limit)
    )
    tags = result.all()
    
    return {
        "tags": [{"name": tag.tag, "count": tag.count} for tag in tags]
    }


# Upvote Entry
@router.post("/entries/{entry_id}/upvote")
async def upvote_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upvote a knowledge entry.
    """
    result = await db.execute(
        select(KnowledgeEntry).where(KnowledgeEntry.id == uuid.UUID(entry_id))
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )
    
    # TODO: Check if user already upvoted (requires upvotes table)
    # For now, just increment
    entry.upvotes_count += 1
    await db.commit()
    
    return {"upvotes_count": entry.upvotes_count}

