# API Package

# Import all routers for main app registration
try:
    from .grokopedia import router as grokopedia_router
    print("✅ API package: Grokopedia router imported")
except ImportError as e:
    print(f"⚠️  API package: Grokopedia router import failed: {e}")
    grokopedia_router = None

# Export routers for main app
__all__ = ["grokopedia_router"]
