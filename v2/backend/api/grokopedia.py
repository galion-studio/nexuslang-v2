"""
Ultra-minimal Grokopedia API for testing
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"status": "working", "message": "Grokopedia router loaded"}

@router.get("/scientific-capabilities")
async def get_scientific_capabilities():
    """Get scientific capabilities"""
    return {
        "supported_domains": ["physics", "chemistry", "mathematics"],
        "first_principles_enabled": True,
        "multi_agent_system": True
    }
