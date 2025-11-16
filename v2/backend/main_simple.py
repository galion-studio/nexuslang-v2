"""
Galion Voice API - Simple Starter
Minimal FastAPI app to get the Voice API running
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Galion Voice API",
    description="Ultimate Voice API for 22nd century voice-first interaction",
    version="2.0.0-alpha"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3003",
        "https://galion.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "galion-voice-api",
        "version": "2.0.0-alpha"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Galion Voice API",
        "docs": "/docs",
        "health": "/health"
    }

# Try to import voice WebSocket (optional for now)
try:
    from api.voice_websocket import router as voice_router
    app.include_router(voice_router, prefix="/ws", tags=["voice"])
    print("✅ Voice WebSocket loaded")
except ImportError as e:
    print(f"⚠️  Voice WebSocket not available: {e}")

# Try to import voice services (optional for now)
try:
    from api.voice import router as voice_api_router
    app.include_router(voice_api_router, prefix="/api/v1", tags=["voice-api"])
    print("✅ Voice API endpoints loaded")
except ImportError as e:
    print(f"⚠️  Voice API endpoints not available: {e}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("=" * 60)
    print("🚀 GALION VOICE API STARTING")
    print("=" * 60)
    print(f"📡 Server: http://{host}:{port}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print(f"💓 Health: http://{host}:{port}/health")
    print("=" * 60)
    
    uvicorn.run(
        "main_simple:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
