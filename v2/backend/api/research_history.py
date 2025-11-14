"""
Research history and bookmarks API routes.
Handles saving, retrieving, and managing research sessions and bookmarks.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..core.database import get_db
from ..api.auth import get_current_user
from ..models.user import User
from ..services.research_history.bookmark_manager import BookmarkManager

router = APIRouter()


# Request/Response Models

class SaveResearchRequest(BaseModel):
    """Request model for saving research sessions."""
    query: str = Field(..., description="The research query")
    persona: str = Field("default", description="Writing persona used")
    depth: str = Field("comprehensive", description="Research depth used")
    synthesized_answer: str = Field(..., description="Generated response")
    sources_used: List[Dict[str, Any]] = Field(default_factory=list, description="Sources used")
    confidence_score: float = Field(0.0, description="Confidence score")
    processing_time: float = Field(0.0, description="Processing time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    is_bookmarked: bool = Field(False, description="Whether to bookmark this session")


class SaveResearchResponse(BaseModel):
    """Response model for saving research."""
    success: bool
    session_id: Optional[str] = None
    created_at: Optional[str] = None
    query: Optional[str] = None
    error: Optional[str] = None


class ResearchHistoryFilters(BaseModel):
    """Filters for research history queries."""
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    persona: Optional[str] = None
    min_confidence: Optional[float] = None
    tags: Optional[List[str]] = None


class ResearchSessionSummary(BaseModel):
    """Summary of a research session."""
    id: str
    query: str
    persona: str
    depth: str
    synthesized_answer: str
    sources_count: int
    confidence_score: float
    processing_time: float
    created_at: str
    is_bookmarked: bool
    tags: List[str]


class ResearchHistoryResponse(BaseModel):
    """Response model for research history."""
    success: bool
    sessions: List[ResearchSessionSummary]
    total: int
    limit: int
    offset: int
    has_more: bool
    error: Optional[str] = None


class CreateBookmarkRequest(BaseModel):
    """Request model for creating bookmarks."""
    session_id: str = Field(..., description="Research session ID to bookmark")
    title: Optional[str] = Field(None, description="Custom bookmark title")
    description: str = Field("", description="Bookmark description")
    tags: List[str] = Field(default_factory=list, description="Bookmark tags")
    category: str = Field("general", description="Bookmark category")
    importance: str = Field("medium", description="Importance level: low, medium, high, critical")
    notes: Dict[str, Any] = Field(default_factory=dict, description="Personal notes")


class CreateBookmarkResponse(BaseModel):
    """Response model for bookmark creation."""
    success: bool
    bookmark_id: Optional[str] = None
    title: Optional[str] = None
    created_at: Optional[str] = None
    error: Optional[str] = None


class BookmarkSummary(BaseModel):
    """Summary of a bookmark."""
    id: str
    title: str
    description: str
    category: str
    importance: str
    tags: List[str]
    notes: Dict[str, Any]
    created_at: str
    research_session: Optional[Dict[str, Any]] = None


class BookmarksResponse(BaseModel):
    """Response model for bookmarks list."""
    success: bool
    bookmarks: List[BookmarkSummary]
    total: int
    error: Optional[str] = None


class UpdateBookmarkRequest(BaseModel):
    """Request model for updating bookmarks."""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    importance: Optional[str] = None
    notes: Optional[Dict[str, Any]] = None


class UpdateBookmarkResponse(BaseModel):
    """Response model for bookmark updates."""
    success: bool
    bookmark_id: Optional[str] = None
    updated_at: Optional[str] = None
    error: Optional[str] = None


class SearchHistoryRequest(BaseModel):
    """Request model for searching research history."""
    query: str = Field(..., description="Search query")
    limit: int = Field(50, description="Maximum results")


class SearchHistoryResponse(BaseModel):
    """Response model for history search."""
    success: bool
    query: str
    results: List[Dict[str, Any]]
    total: int
    error: Optional[str] = None


class ExportResearchRequest(BaseModel):
    """Request model for exporting research data."""
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ExportResearchResponse(BaseModel):
    """Response model for research data export."""
    success: bool
    export_data: Optional[Dict[str, Any]] = None
    sessions_count: int = 0
    bookmarks_count: int = 0
    error: Optional[str] = None


class UserStatsResponse(BaseModel):
    """Response model for user research statistics."""
    success: bool
    stats: Dict[str, Any]
    error: Optional[str] = None


# API Endpoints

@router.post("/save", response_model=SaveResearchResponse)
async def save_research_session(
    request: SaveResearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Save a research session for later retrieval.

    Automatically creates bookmarks for important findings and maintains
    research history with full context preservation.
    """
    try:
        bookmark_manager = BookmarkManager()

        research_data = {
            "query": request.query,
            "persona": request.persona,
            "depth": request.depth,
            "synthesized_answer": request.synthesized_answer,
            "sources_used": request.sources_used,
            "confidence_score": request.confidence_score,
            "processing_time": request.processing_time,
            "metadata": request.metadata,
            "tags": request.tags,
            "is_bookmarked": request.is_bookmarked
        }

        result = await bookmark_manager.save_research_session(db, current_user.id, research_data)

        return SaveResearchResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save research session: {str(e)}"
        )


@router.get("/history", response_model=ResearchHistoryResponse)
async def get_research_history(
    limit: int = Query(50, description="Maximum number of sessions to return"),
    offset: int = Query(0, description="Pagination offset"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    persona: Optional[str] = Query(None, description="Filter by persona"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence score"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's research history with optional filtering.

    Supports pagination and advanced filtering by date, persona,
    confidence score, and tags for efficient history browsing.
    """
    try:
        bookmark_manager = BookmarkManager()

        # Parse tags from comma-separated string
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        filters = {
            "date_from": date_from,
            "date_to": date_to,
            "persona": persona,
            "min_confidence": min_confidence,
            "tags": tag_list
        }

        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}

        result = await bookmark_manager.get_research_history(
            db, current_user.id, limit, offset, filters
        )

        return ResearchHistoryResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve research history: {str(e)}"
        )


@router.post("/bookmarks", response_model=CreateBookmarkResponse)
async def create_bookmark(
    request: CreateBookmarkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a bookmark from an existing research session.

    Allows users to save important research findings with custom
    titles, descriptions, categories, and personal notes.
    """
    try:
        bookmark_manager = BookmarkManager()

        bookmark_data = {
            "title": request.title,
            "description": request.description,
            "tags": request.tags,
            "category": request.category,
            "importance": request.importance,
            "notes": request.notes
        }

        result = await bookmark_manager.create_bookmark(
            db, current_user.id, request.session_id, bookmark_data
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create bookmark")
            )

        return CreateBookmarkResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bookmark: {str(e)}"
        )


@router.get("/bookmarks", response_model=BookmarksResponse)
async def get_bookmarks(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, description="Maximum number of bookmarks"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's bookmarks with optional category filtering.

    Returns all bookmarks with associated research session information
    for easy browsing and organization.
    """
    try:
        bookmark_manager = BookmarkManager()

        result = await bookmark_manager.get_bookmarks(
            db, current_user.id, category, limit
        )

        return BookmarksResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve bookmarks: {str(e)}"
        )


@router.put("/bookmarks/{bookmark_id}", response_model=UpdateBookmarkResponse)
async def update_bookmark(
    bookmark_id: str,
    request: UpdateBookmarkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing bookmark.

    Allows modification of bookmark metadata, organization,
    and personal notes without affecting the original research.
    """
    try:
        bookmark_manager = BookmarkManager()

        update_data = request.dict(exclude_unset=True)

        result = await bookmark_manager.update_bookmark(
            db, current_user.id, bookmark_id, update_data
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Bookmark not found")
            )

        return UpdateBookmarkResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update bookmark: {str(e)}"
        )


@router.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a bookmark.

    Removes the bookmark while preserving the original research session.
    If no other bookmarks reference the session, it becomes un-bookmarked.
    """
    try:
        bookmark_manager = BookmarkManager()

        result = await bookmark_manager.delete_bookmark(
            db, current_user.id, bookmark_id
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Bookmark not found")
            )

        return {"success": True, "message": "Bookmark deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete bookmark: {str(e)}"
        )


@router.post("/search", response_model=SearchHistoryResponse)
async def search_research_history(
    request: SearchHistoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search through research history using full-text search.

    Allows users to find previous research by content, queries,
    or any text within their research history.
    """
    try:
        bookmark_manager = BookmarkManager()

        result = await bookmark_manager.search_research_history(
            db, current_user.id, request.query, request.limit
        )

        return SearchHistoryResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search research history: {str(e)}"
        )


@router.post("/export", response_model=ExportResearchResponse)
async def export_research_data(
    request: ExportResearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export user's research data for backup or migration.

    Returns complete research history and bookmarks in a structured
    format suitable for backup, migration, or external analysis.
    """
    try:
        bookmark_manager = BookmarkManager()

        result = await bookmark_manager.export_research_data(
            db, current_user.id, request.date_from, request.date_to
        )

        return ExportResearchResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export research data: {str(e)}"
        )


@router.get("/stats", response_model=UserStatsResponse)
async def get_research_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive research statistics for the user.

    Provides insights into research patterns, performance metrics,
    and usage statistics to help optimize research workflows.
    """
    try:
        bookmark_manager = BookmarkManager()

        result = await bookmark_manager.get_user_stats(db, current_user.id)

        return UserStatsResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve research statistics: {str(e)}"
        )
