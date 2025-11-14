"""
Research Memory System for Deep Search
Tag-based memory for organizing research findings
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class ResearchMemory:
    """
    Tag-based memory system for organizing research findings

    Features:
    - Tag-based organization and retrieval
    - Research session management
    - Cross-referencing between findings
    - Temporal organization
    """

    def __init__(self, max_sessions: int = 100):
        self.max_sessions = max_sessions
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)  # tag -> session_ids
        self.session_tags: Dict[str, Set[str]] = defaultdict(set)  # session_id -> tags

        logger.info(f"Initialized research memory with max {max_sessions} sessions")

    async def create_session(self, session_id: str, metadata: Dict[str, Any] = None) -> bool:
        """Create a new research session"""
        if session_id in self.sessions:
            logger.warning(f"Session {session_id} already exists")
            return False

        self.sessions[session_id] = {
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow(),
            "metadata": metadata or {},
            "findings": [],
            "queries": [],
            "tags": set(),
            "cross_references": []
        }

        logger.info(f"Created research session: {session_id}")
        return True

    async def add_finding(self, session_id: str, finding: Dict[str, Any],
                         tags: List[str] = None) -> bool:
        """Add a finding to a research session"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} does not exist")
            return False

        finding_entry = {
            "id": f"finding_{len(self.sessions[session_id]['findings'])}",
            "content": finding,
            "tags": tags or [],
            "timestamp": datetime.utcnow(),
            "importance": finding.get("importance", 0.5)
        }

        self.sessions[session_id]["findings"].append(finding_entry)
        self.sessions[session_id]["last_updated"] = datetime.utcnow()

        # Update tag index
        for tag in finding_entry["tags"]:
            self.tag_index[tag].add(session_id)
            self.session_tags[session_id].add(tag)

        logger.info(f"Added finding to session {session_id}: {finding_entry['id']}")
        return True

    async def add_query(self, session_id: str, query: str, results: Dict[str, Any]) -> bool:
        """Add a query and its results to a research session"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} does not exist")
            return False

        query_entry = {
            "query": query,
            "results": results,
            "timestamp": datetime.utcnow(),
            "result_count": len(results.get("sources", []))
        }

        self.sessions[session_id]["queries"].append(query_entry)
        self.sessions[session_id]["last_updated"] = datetime.utcnow()

        logger.info(f"Added query to session {session_id}: {query[:50]}...")
        return True

    async def search_by_tags(self, tags: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """Search sessions by tags"""
        matching_sessions = set()

        for tag in tags:
            matching_sessions.update(self.tag_index.get(tag, set()))

        results = []
        for session_id in list(matching_sessions)[:limit]:
            session = self.sessions.get(session_id)
            if session:
                results.append({
                    "session_id": session_id,
                    "metadata": session["metadata"],
                    "finding_count": len(session["findings"]),
                    "query_count": len(session["queries"]),
                    "last_updated": session["last_updated"],
                    "tags": list(session["tags"])
                })

        return results

    async def get_session_findings(self, session_id: str, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Get findings from a specific session, optionally filtered by tags"""
        if session_id not in self.sessions:
            return []

        findings = self.sessions[session_id]["findings"]

        if tags:
            # Filter findings by tags
            filtered_findings = []
            for finding in findings:
                finding_tags = finding.get("tags", [])
                if any(tag in finding_tags for tag in tags):
                    filtered_findings.append(finding)
            return filtered_findings

        return findings

    async def cross_reference_sessions(self, session_ids: List[str]) -> Dict[str, Any]:
        """Create cross-references between sessions"""
        cross_refs = {}

        for i, session_id1 in enumerate(session_ids):
            for session_id2 in session_ids[i+1:]:
                # Find common tags
                tags1 = self.session_tags.get(session_id1, set())
                tags2 = self.session_tags.get(session_id2, set())
                common_tags = tags1.intersection(tags2)

                if common_tags:
                    ref_key = f"{session_id1}_{session_id2}"
                    cross_refs[ref_key] = {
                        "session1": session_id1,
                        "session2": session_id2,
                        "common_tags": list(common_tags),
                        "strength": len(common_tags)
                    }

        return cross_refs

    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a research session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}

        session = self.sessions[session_id]
        findings = session["findings"]
        queries = session["queries"]

        # Calculate tag distribution
        tag_counts = defaultdict(int)
        for finding in findings:
            for tag in finding.get("tags", []):
                tag_counts[tag] += 1

        return {
            "session_id": session_id,
            "created_at": session["created_at"],
            "last_updated": session["last_updated"],
            "finding_count": len(findings),
            "query_count": len(queries),
            "tag_distribution": dict(tag_counts),
            "total_tags": len(tag_counts),
            "average_findings_per_query": len(findings) / max(len(queries), 1),
            "session_duration": (session["last_updated"] - session["created_at"]).total_seconds()
        }

    async def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """Remove sessions older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        sessions_to_remove = []

        for session_id, session in self.sessions.items():
            if session["last_updated"] < cutoff_date:
                sessions_to_remove.append(session_id)

        # Remove sessions and clean up indexes
        for session_id in sessions_to_remove:
            # Remove from tag index
            for tag in self.session_tags.get(session_id, set()):
                self.tag_index[tag].discard(session_id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]

            # Remove session data
            del self.sessions[session_id]
            del self.session_tags[session_id]

        logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
        return len(sessions_to_remove)

    async def export_session(self, session_id: str) -> Dict[str, Any]:
        """Export a complete research session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}

        session = self.sessions[session_id].copy()

        # Convert sets to lists for JSON serialization
        session["tags"] = list(session.get("tags", set()))

        return {
            "session_id": session_id,
            "exported_at": datetime.utcnow().isoformat(),
            "data": session
        }

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get overall memory statistics"""
        total_sessions = len(self.sessions)
        total_findings = sum(len(session["findings"]) for session in self.sessions.values())
        total_queries = sum(len(session["queries"]) for session in self.sessions.values())

        # Tag statistics
        all_tags = set()
        for tags in self.session_tags.values():
            all_tags.update(tags)

        return {
            "total_sessions": total_sessions,
            "total_findings": total_findings,
            "total_queries": total_queries,
            "unique_tags": len(all_tags),
            "average_findings_per_session": total_findings / max(total_sessions, 1),
            "average_queries_per_session": total_queries / max(total_sessions, 1),
            "most_common_tags": sorted(
                [(tag, len(sessions)) for tag, sessions in self.tag_index.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
