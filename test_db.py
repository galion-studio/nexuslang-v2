#!/usr/bin/env python3
"""
Simple database connectivity test
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'v2', 'backend'))

async def test_db():
    try:
        from core.database import get_async_session_maker

        # Get session maker
        session_maker = get_async_session_maker()

        # Test connection
        async with session_maker() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Database connection successful: {row[0]}")

        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_db())
    sys.exit(0 if success else 1)
