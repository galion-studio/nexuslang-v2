"""
Research history and bookmark management for Deep Search.
Allows users to save, organize, and revisit past research sessions.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
import json

from ...models.user import User
from ...models.research import ResearchSession, ResearchBookmark, ResearchTag

logger = logging.getLogger(__name__)


class BookmarkManager:
    """
    Manages research history, bookmarks, and user research sessions.

    Features:
    - Save research sessions with full context
    - Create bookmarks for important findings
    - Organize research with tags and folders
    - Search through research history
    - Export/import research data
    - Collaborative bookmark sharing
    """

    def __init__(self):
        self.max_sessions_per_user = 1000
        self.max_bookmarks_per_user = 5000
        self.session_retention_days = 365  # Keep sessions for 1 year

    async def save_research_session(self, session: AsyncSession, user_id: str,
                                   research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a complete research session for later retrieval.

        Args:
            session: Database session
            user_id: User identifier
            research_data: Complete research session data

        Returns:
            Saved session information
        """
        try:
            # Create research session record
            research_session = ResearchSession(
                user_id=user_id,
                query=research_data["query"],
                persona=research_data.get("persona", "default"),
                depth=research_data.get("depth", "comprehensive"),
                synthesized_answer=research_data["synthesized_answer"],
                sources_used=json.dumps(research_data.get("sources_used", [])),
                confidence_score=research_data.get("confidence_score", 0.0),
                processing_time=research_data.get("processing_time", 0.0),
                metadata=json.dumps(research_data.get("metadata", {})),
                tags=json.dumps(research_data.get("tags", [])),
                is_bookmarked=research_data.get("is_bookmarked", False)
            )

            session.add(research_session)
            await session.commit()
            await session.refresh(research_session)

            # Clean up old sessions if user has too many
            await self._cleanup_old_sessions(session, user_id)

            logger.info(f"Saved research session for user {user_id}: {research_session.id}")

            return {
                "success": True,
                "session_id": str(research_session.id),
                "created_at": research_session.created_at.isoformat(),
                "query": research_session.query
            }

        except Exception as e:
            logger.error(f"Failed to save research session: {e}")
            await session.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    async def get_research_history(self, session: AsyncSession, user_id: str,
                                  limit: int = 50, offset: int = 0,
                                  filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get user's research history with optional filtering.

        Args:
            session: Database session
            user_id: User identifier
            limit: Maximum number of results
            offset: Pagination offset
            filters: Optional filters (date_range, persona, tags, etc.)

        Returns:
            Research history with pagination
        """
        try:
            query = select(ResearchSession).where(ResearchSession.user_id == user_id)

            # Apply filters
            if filters:
                if filters.get("date_from"):
                    query = query.where(ResearchSession.created_at >= filters["date_from"])
                if filters.get("date_to"):
                    query = query.where(ResearchSession.created_at <= filters["date_to"])
                if filters.get("persona"):
                    query = query.where(ResearchSession.persona == filters["persona"])
                if filters.get("min_confidence"):
                    query = query.where(ResearchSession.confidence_score >= filters["min_confidence"])
                if filters.get("tags"):
                    # Filter by tags (simplified - you might want more complex tag matching)
                    tag_filters = [ResearchSession.tags.contains(tag) for tag in filters["tags"]]
                    query = query.where(or_(*tag_filters))

            # Order by creation date (newest first)
            query = query.order_by(desc(ResearchSession.created_at))

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_count = await session.execute(count_query)
            total = total_count.scalar()

            # Apply pagination
            query = query.limit(limit).offset(offset)

            result = await session.execute(query)
            research_sessions = result.scalars().all()

            # Format response
            sessions_data = []
            for rs in research_sessions:
                session_data = {
                    "id": str(rs.id),
                    "query": rs.query,
                    "persona": rs.persona,
                    "depth": rs.depth,
                    "synthesized_answer": rs.synthesized_answer[:500] + "..." if len(rs.synthesized_answer) > 500 else rs.synthesized_answer,
                    "sources_count": len(json.loads(rs.sources_used)) if rs.sources_used else 0,
                    "confidence_score": rs.confidence_score,
                    "processing_time": rs.processing_time,
                    "created_at": rs.created_at.isoformat(),
                    "is_bookmarked": rs.is_bookmarked,
                    "tags": json.loads(rs.tags) if rs.tags else []
                }
                sessions_data.append(session_data)

            return {
                "success": True,
                "sessions": sessions_data,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }

        except Exception as e:
            logger.error(f"Failed to get research history: {e}")
            return {
                "success": False,
                "error": str(e),
                "sessions": [],
                "total": 0
            }

    async def create_bookmark(self, session: AsyncSession, user_id: str,
                             session_id: str, bookmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a bookmark from a research session.

        Args:
            session: Database session
            user_id: User identifier
            session_id: Research session ID to bookmark
            bookmark_data: Bookmark metadata

        Returns:
            Bookmark creation result
        """
        try:
            # Verify the research session exists and belongs to the user
            research_session = await session.execute(
                select(ResearchSession).where(
                    and_(
                        ResearchSession.id == session_id,
                        ResearchSession.user_id == user_id
                    )
                )
            )
            rs = research_session.scalar_one_or_none()

            if not rs:
                return {
                    "success": False,
                    "error": "Research session not found or access denied"
                }

            # Create bookmark
            bookmark = ResearchBookmark(
                user_id=user_id,
                session_id=session_id,
                title=bookmark_data.get("title", rs.query[:100]),
                description=bookmark_data.get("description", ""),
                tags=json.dumps(bookmark_data.get("tags", [])),
                category=bookmark_data.get("category", "general"),
                importance=bookmark_data.get("importance", "medium"),
                notes=json.dumps(bookmark_data.get("notes", ""))
            )

            session.add(bookmark)

            # Mark the research session as bookmarked
            rs.is_bookmarked = True

            await session.commit()
            await session.refresh(bookmark)

            logger.info(f"Created bookmark for user {user_id}: {bookmark.id}")

            return {
                "success": True,
                "bookmark_id": str(bookmark.id),
                "title": bookmark.title,
                "created_at": bookmark.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to create bookmark: {e}")
            await session.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    async def get_bookmarks(self, session: AsyncSession, user_id: str,
                           category: str = None, limit: int = 100) -> Dict[str, Any]:
        """
        Get user's bookmarks with optional category filtering.

        Args:
            session: Database session
            user_id: User identifier
            category: Optional category filter
            limit: Maximum number of results

        Returns:
            User's bookmarks
        """
        try:
            query = select(ResearchBookmark).where(ResearchBookmark.user_id == user_id)

            if category:
                query = query.where(ResearchBookmark.category == category)

            query = query.order_by(desc(ResearchBookmark.created_at)).limit(limit)

            result = await session.execute(query)
            bookmarks = result.scalars().all()

            bookmarks_data = []
            for bm in bookmarks:
                # Get associated research session data
                rs_query = select(ResearchSession).where(ResearchSession.id == bm.session_id)
                rs_result = await session.execute(rs_query)
                research_session = rs_result.scalar_one_or_none()

                bookmark_data = {
                    "id": str(bm.id),
                    "title": bm.title,
                    "description": bm.description,
                    "category": bm.category,
                    "importance": bm.importance,
                    "tags": json.loads(bm.tags) if bm.tags else [],
                    "notes": json.loads(bm.notes) if bm.notes else {},
                    "created_at": bm.created_at.isoformat(),
                    "research_session": {
                        "id": str(research_session.id) if research_session else None,
                        "query": research_session.query if research_session else None,
                        "persona": research_session.persona if research_session else None,
                        "confidence_score": research_session.confidence_score if research_session else None
                    } if research_session else None
                }
                bookmarks_data.append(bookmark_data)

            return {
                "success": True,
                "bookmarks": bookmarks_data,
                "total": len(bookmarks_data)
            }

        except Exception as e:
            logger.error(f"Failed to get bookmarks: {e}")
            return {
                "success": False,
                "error": str(e),
                "bookmarks": [],
                "total": 0
            }

    async def update_bookmark(self, session: AsyncSession, user_id: str,
                             bookmark_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing bookmark.

        Args:
            session: Database session
            user_id: User identifier
            bookmark_id: Bookmark ID to update
            update_data: Fields to update

        Returns:
            Update result
        """
        try:
            # Find the bookmark
            bookmark_query = select(ResearchBookmark).where(
                and_(
                    ResearchBookmark.id == bookmark_id,
                    ResearchBookmark.user_id == user_id
                )
            )
            result = await session.execute(bookmark_query)
            bookmark = result.scalar_one_or_none()

            if not bookmark:
                return {
                    "success": False,
                    "error": "Bookmark not found or access denied"
                }

            # Update fields
            if "title" in update_data:
                bookmark.title = update_data["title"]
            if "description" in update_data:
                bookmark.description = update_data["description"]
            if "tags" in update_data:
                bookmark.tags = json.dumps(update_data["tags"])
            if "category" in update_data:
                bookmark.category = update_data["category"]
            if "importance" in update_data:
                bookmark.importance = update_data["importance"]
            if "notes" in update_data:
                bookmark.notes = json.dumps(update_data["notes"])

            bookmark.updated_at = datetime.utcnow()

            await session.commit()

            return {
                "success": True,
                "bookmark_id": str(bookmark.id),
                "updated_at": bookmark.updated_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to update bookmark: {e}")
            await session.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    async def delete_bookmark(self, session: AsyncSession, user_id: str,
                             bookmark_id: str) -> Dict[str, Any]:
        """
        Delete a bookmark.

        Args:
            session: Database session
            user_id: User identifier
            bookmark_id: Bookmark ID to delete

        Returns:
            Deletion result
        """
        try:
            # Find and delete the bookmark
            bookmark_query = select(ResearchBookmark).where(
                and_(
                    ResearchBookmark.id == bookmark_id,
                    ResearchBookmark.user_id == user_id
                )
            )
            result = await session.execute(bookmark_query)
            bookmark = result.scalar_one_or_none()

            if not bookmark:
                return {
                    "success": False,
                    "error": "Bookmark not found or access denied"
                }

            await session.delete(bookmark)
            await session.commit()

            # Check if we should un-bookmark the research session
            session_bookmarks_query = select(func.count()).select_from(
                select(ResearchBookmark).where(ResearchBookmark.session_id == bookmark.session_id).subquery()
            )
            bookmarks_count_result = await session.execute(session_bookmarks_query)
            bookmarks_count = bookmarks_count_result.scalar()

            if bookmarks_count == 0:
                # No more bookmarks for this session, un-bookmark it
                rs_query = select(ResearchSession).where(ResearchSession.id == bookmark.session_id)
                rs_result = await session.execute(rs_query)
                research_session = rs_result.scalar_one_or_none()

                if research_session:
                    research_session.is_bookmarked = False
                    await session.commit()

            return {
                "success": True,
                "bookmark_id": bookmark_id
            }

        except Exception as e:
            logger.error(f"Failed to delete bookmark: {e}")
            await session.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    async def search_research_history(self, session: AsyncSession, user_id: str,
                                     search_query: str, limit: int = 50) -> Dict[str, Any]:
        """
        Search through research history using full-text search.

        Args:
            session: Database session
            user_id: User identifier
            search_query: Search query
            limit: Maximum results

        Returns:
            Search results
        """
        try:
            # Use PostgreSQL full-text search on query and answer
            search_vector = func.to_tsvector('english',
                func.concat(ResearchSession.query, ' ', ResearchSession.synthesized_answer)
            )
            search_query_ts = func.plainto_tsquery('english', search_query)

            query = select(ResearchSession).where(
                and_(
                    ResearchSession.user_id == user_id,
                    search_vector.op('@@')(search_query_ts)
                )
            ).order_by(
                func.ts_rank_cd(search_vector, search_query_ts).desc()
            ).limit(limit)

            result = await session.execute(query)
            research_sessions = result.scalars().all()

            # Format results
            results_data = []
            for rs in research_sessions:
                result_data = {
                    "id": str(rs.id),
                    "query": rs.query,
                    "synthesized_answer": rs.synthesized_answer[:300] + "..." if len(rs.synthesized_answer) > 300 else rs.synthesized_answer,
                    "persona": rs.persona,
                    "confidence_score": rs.confidence_score,
                    "created_at": rs.created_at.isoformat(),
                    "relevance_score": 0.0  # Could be calculated based on search ranking
                }
                results_data.append(result_data)

            return {
                "success": True,
                "query": search_query,
                "results": results_data,
                "total": len(results_data)
            }

        except Exception as e:
            logger.error(f"Failed to search research history: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "total": 0
            }

    async def export_research_data(self, session: AsyncSession, user_id: str,
                                  date_from: datetime = None, date_to: datetime = None) -> Dict[str, Any]:
        """
        Export user's research data for backup or migration.

        Args:
            session: Database session
            user_id: User identifier
            date_from: Start date for export
            date_to: End date for export

        Returns:
            Export data
        """
        try:
            # Get research sessions
            sessions_query = select(ResearchSession).where(ResearchSession.user_id == user_id)

            if date_from:
                sessions_query = sessions_query.where(ResearchSession.created_at >= date_from)
            if date_to:
                sessions_query = sessions_query.where(ResearchSession.created_at <= date_to)

            sessions_result = await session.execute(sessions_query)
            research_sessions = sessions_result.scalars().all()

            # Get bookmarks
            bookmarks_query = select(ResearchBookmark).where(ResearchBookmark.user_id == user_id)
            bookmarks_result = await session.execute(bookmarks_query)
            bookmarks = bookmarks_result.scalars().all()

            # Format export data
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "date_range": {
                    "from": date_from.isoformat() if date_from else None,
                    "to": date_to.isoformat() if date_to else None
                },
                "research_sessions": [
                    {
                        "id": str(rs.id),
                        "query": rs.query,
                        "persona": rs.persona,
                        "depth": rs.depth,
                        "synthesized_answer": rs.synthesized_answer,
                        "sources_used": json.loads(rs.sources_used) if rs.sources_used else [],
                        "confidence_score": rs.confidence_score,
                        "processing_time": rs.processing_time,
                        "metadata": json.loads(rs.metadata) if rs.metadata else {},
                        "tags": json.loads(rs.tags) if rs.tags else [],
                        "is_bookmarked": rs.is_bookmarked,
                        "created_at": rs.created_at.isoformat(),
                        "updated_at": rs.updated_at.isoformat() if rs.updated_at else None
                    }
                    for rs in research_sessions
                ],
                "bookmarks": [
                    {
                        "id": str(bm.id),
                        "session_id": str(bm.session_id),
                        "title": bm.title,
                        "description": bm.description,
                        "category": bm.category,
                        "importance": bm.importance,
                        "tags": json.loads(bm.tags) if bm.tags else [],
                        "notes": json.loads(bm.notes) if bm.notes else {},
                        "created_at": bm.created_at.isoformat(),
                        "updated_at": bm.updated_at.isoformat() if bm.updated_at else None
                    }
                    for bm in bookmarks
                ]
            }

            return {
                "success": True,
                "export_data": export_data,
                "sessions_count": len(export_data["research_sessions"]),
                "bookmarks_count": len(export_data["bookmarks"])
            }

        except Exception as e:
            logger.error(f"Failed to export research data: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _cleanup_old_sessions(self, session: AsyncSession, user_id: str):
        """
        Clean up old research sessions to maintain storage limits.

        Args:
            session: Database session
            user_id: User identifier
        """
        try:
            # Count current sessions
            count_query = select(func.count()).select_from(
                select(ResearchSession).where(ResearchSession.user_id == user_id).subquery()
            )
            result = await session.execute(count_query)
            session_count = result.scalar()

            if session_count > self.max_sessions_per_user:
                # Delete oldest sessions beyond the limit
                delete_count = session_count - self.max_sessions_per_user

                # Get IDs of sessions to delete (oldest first, excluding bookmarked)
                old_sessions_query = select(ResearchSession.id).where(
                    and_(
                        ResearchSession.user_id == user_id,
                        ResearchSession.is_bookmarked == False
                    )
                ).order_by(ResearchSession.created_at).limit(delete_count)

                result = await session.execute(old_sessions_query)
                session_ids_to_delete = [row[0] for row in result.fetchall()]

                if session_ids_to_delete:
                    # Delete the sessions
                    delete_query = ResearchSession.__table__.delete().where(
                        ResearchSession.id.in_(session_ids_to_delete)
                    )
                    await session.execute(delete_query)

                    logger.info(f"Cleaned up {len(session_ids_to_delete)} old sessions for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to cleanup old sessions for user {user_id}: {e}")

    async def get_user_stats(self, session: AsyncSession, user_id: str) -> Dict[str, Any]:
        """
        Get research statistics for a user.

        Args:
            session: Database session
            user_id: User identifier

        Returns:
            User research statistics
        """
        try:
            # Session statistics
            sessions_query = select(
                func.count(ResearchSession.id).label('total_sessions'),
                func.avg(ResearchSession.confidence_score).label('avg_confidence'),
                func.sum(ResearchSession.processing_time).label('total_processing_time'),
                func.count(func.distinct(ResearchSession.persona)).label('unique_personas')
            ).where(ResearchSession.user_id == user_id)

            sessions_result = await session.execute(sessions_query)
            sessions_stats = sessions_result.first()

            # Bookmark statistics
            bookmarks_query = select(
                func.count(ResearchBookmark.id).label('total_bookmarks'),
                func.count(func.distinct(ResearchBookmark.category)).label('categories_used')
            ).where(ResearchBookmark.user_id == user_id)

            bookmarks_result = await session.execute(bookmarks_query)
            bookmarks_stats = bookmarks_result.first()

            # Recent activity
            recent_query = select(func.count()).select_from(
                select(ResearchSession).where(
                    and_(
                        ResearchSession.user_id == user_id,
                        ResearchSession.created_at >= datetime.utcnow() - timedelta(days=7)
                    )
                ).subquery()
            )
            recent_result = await session.execute(recent_query)
            recent_sessions = recent_result.scalar()

            return {
                "success": True,
                "stats": {
                    "total_sessions": sessions_stats.total_sessions or 0,
                    "total_bookmarks": bookmarks_stats.total_bookmarks or 0,
                    "avg_confidence_score": float(sessions_stats.avg_confidence) if sessions_stats.avg_confidence else 0.0,
                    "total_processing_time": float(sessions_stats.total_processing_time) if sessions_stats.total_processing_time else 0.0,
                    "unique_personas_used": sessions_stats.unique_personas or 0,
                    "categories_used": bookmarks_stats.categories_used or 0,
                    "recent_sessions_7d": recent_sessions or 0
                }
            }

        except Exception as e:
            logger.error(f"Failed to get user stats for {user_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
