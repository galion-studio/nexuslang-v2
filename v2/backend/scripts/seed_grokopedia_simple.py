#!/usr/bin/env python3
"""
Simple seed script for Grokopedia knowledge base.
Run this from the backend directory.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Set up basic environment
os.environ.setdefault('ENVIRONMENT', 'development')

from core.database import get_db, init_db
from models.knowledge import KnowledgeEntry
from services.grokopedia.search import get_search_engine


async def seed_entries():
    """Seed some basic entries."""
    await init_db()

    async for db in get_db():
        try:
            search_engine = get_search_engine()

            # Simple test entry
            test_entry = {
                "title": "Test Entry",
                "summary": "A test knowledge entry",
                "content": "This is a test entry to verify the seeding functionality works.",
                "tags": ["test", "seed"],
                "verified": True
            }

            # Check if already exists
            from sqlalchemy import select
            result = await db.execute(
                select(KnowledgeEntry).where(KnowledgeEntry.title == test_entry["title"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print("Test entry already exists!")
                return

            # Create embedding
            embedding_text = f"{test_entry['title']}\n\n{test_entry['summary']}\n\n{test_entry['content']}"
            embedding = await search_engine.create_embedding(embedding_text)

            # Create entry
            entry = KnowledgeEntry(
                title=test_entry["title"],
                slug="test-entry",
                summary=test_entry["summary"],
                content=test_entry["content"],
                embeddings=embedding,
                tags=test_entry["tags"],
                verified=test_entry["verified"]
            )

            db.add(entry)
            await db.commit()
            print("Test entry created successfully!")

        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(seed_entries())
