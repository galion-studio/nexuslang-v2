"""
NexusLang v2 - Main FastAPI Application
Complete backend API serving developer.galion.app and galion.studio

Features:
- Authentication & Authorization
- AI Integration (30+ models via OpenRouter)
- NexusLang code execution
- Billing & subscriptions
- Analytics & monitoring
- WebSocket support
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Import routers
from .api import auth, ai, nexuslang, billing, video, projects, teams, analytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NexusLang v2 API",
    description="Complete backend for Galion Ecosystem",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://developer.galion.app",
        "https://galion.studio",
        "https://*.proxy.runpod.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "NexusLang v2 API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "platforms": [
            "developer.galion.app",
            "galion.studio"
        ]
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": "2025-01-01T00:00:00Z"
    }


# Include routers
app.include_router(auth.router, prefix="/api/v2/auth", tags=["Authentication"])
app.include_router(ai.router, prefix="/api/v2", tags=["AI"])
app.include_router(nexuslang.router, prefix="/api/v2", tags=["NexusLang"])
app.include_router(billing.router, prefix="/api/v2/billing", tags=["Billing"])
app.include_router(video.router, prefix="/api/v2/video", tags=["Video"])
app.include_router(projects.router, prefix="/api/v2/projects", tags=["Projects"])
app.include_router(teams.router, prefix="/api/v2/teams", tags=["Teams"])
app.include_router(analytics.router, prefix="/api/v2/analytics", tags=["Analytics"])


# WebSocket endpoint for real-time features
@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    """
    WebSocket endpoint for real-time communication.
    
    Channels: chat, notifications, analytics, logs
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            # Echo back for now (implement proper handling)
            await websocket.send_text(f"Echo {channel}: {data}")
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected from channel: {channel}")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("🚀 NexusLang v2 API starting up...")
    logger.info("✅ API documentation: http://localhost:8000/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("👋 NexusLang v2 API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
