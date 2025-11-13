#!/usr/bin/env python3
"""
Simple startup script for NexusLang v2 Backend
Directly creates the FastAPI app without relative imports
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routers
grokopedia_available = False
marketing_available = False
rbac_available = False
mail_available = False
errors_available = False

try:
    from api.grokopedia import router as grokopedia_router
    grokopedia_available = True
    logger.info("✅ Grokopedia router loaded")
except ImportError as e:
    logger.warning(f"❌ Grokopedia router not available: {e}")

try:
    from api.marketing import router as marketing_router
    marketing_available = True
    logger.info("✅ Marketing router loaded")
except ImportError as e:
    logger.warning(f"❌ Marketing router not available: {e}")

try:
    from api.rbac import router as rbac_router
    rbac_available = True
    logger.info("✅ RBAC router loaded")
except ImportError as e:
    logger.warning(f"❌ RBAC router not available: {e}")

try:
    from api.mail import router as mail_router
    mail_available = True
    logger.info("✅ Mail router loaded")
except ImportError as e:
    logger.warning(f"❌ Mail router not available: {e}")

try:
    from api.errors import router as errors_router
    errors_available = True
    logger.info("✅ Errors router loaded")
except ImportError as e:
    logger.warning(f"❌ Errors router not available: {e}")

# Create FastAPI app
app = FastAPI(
    title="NexusLang v2 API",
    description="Complete backend for Galion Ecosystem",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration - Allow all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "https://developer.galion.app",
        "https://galion.studio",
        "https://*.proxy.runpod.net",
        "https://*.loca.lt",
        "https://*.trycloudflare.com"
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

# Include routers
if grokopedia_available:
    app.include_router(grokopedia_router, prefix="/api/v2", tags=["Grokopedia"])
else:
    logger.warning("❌ Grokopedia router not available")

if marketing_available:
    app.include_router(marketing_router, prefix="/api/v2", tags=["Marketing"])
else:
    logger.warning("❌ Marketing router not available")

if rbac_available:
    app.include_router(rbac_router, prefix="/api/v2", tags=["RBAC"])
else:
    logger.warning("❌ RBAC router not available")

if mail_available:
    app.include_router(mail_router, prefix="/api/v2", tags=["Mail"])
else:
    logger.warning("❌ Mail router not available")

if errors_available:
    app.include_router(errors_router, prefix="/api/v2", tags=["Errors"])
else:
    logger.warning("❌ Errors router not available")



# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("👋 NexusLang v2 API shutting down...")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
