#!/usr/bin/env python3
"""
Test script to verify backend startup and basic functionality.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_backend_startup():
    """Test backend startup"""
    print("🚀 Testing Galion Backend Startup...")
    print("=" * 50)

    try:
        # Test imports
        print("📦 Testing imports...")
        from main import app
        print("✅ Main app imported")

        from core.config import settings
        print("✅ Settings imported")

        from core.database import get_db, create_tables
        print("✅ Database module imported")

        from core.redis_client import get_redis_client
        print("✅ Redis client imported")

        # Test configuration
        print("⚙️ Testing configuration...")
        print(f"   Environment: {settings.environment}")
        print(f"   Debug: {settings.debug}")
        print(f"   Host: {settings.host}:{settings.port}")
        print("✅ Configuration loaded")

        # Test database connection (simulated)
        print("🗄️ Testing database connection...")
        db = await get_db()
        await db.execute("SELECT 1")
        print("✅ Database connection working")

        # Test Redis connection (simulated)
        print("🔴 Testing Redis connection...")
        redis = await get_redis_client()
        await redis.ping()
        print("✅ Redis connection working")

        print("=" * 50)
        print("🎉 Backend startup test PASSED!")
        print("📊 Ready for API testing")
        print()
        print("🚀 To start the backend server:")
        print("   cd v2/backend")
        print("   python main.py")
        print()
        print("📍 API will be available at: http://localhost:8010")
        print("📖 API Documentation: http://localhost:8010/docs")

        return True

    except Exception as e:
        print(f"❌ Backend startup test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend_startup())
    sys.exit(0 if success else 1)
