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
from pydantic import ValidationError
import logging

# Import error handlers
from .core.errors import (
    handle_galion_exception,
    handle_validation_exception,
    handle_http_exception,
    handle_unexpected_exception,
    add_request_id,
    GalionException
)
from .core.performance import performance_middleware, setup_db_monitoring
from .core.monitoring import monitoring_middleware, get_monitoring_system
from .core.backup import get_backup_manager

# Import routers individually
from .api.auth import router as auth_router
from .api.ai import router as ai_router
from .api.nexuslang import router as nexuslang_router
from .api.billing import router as billing_router
from .api.video import router as video_router
from .api.projects import router as projects_router
from .api.teams import router as teams_router
from .api.analytics import router as analytics_router
from .api.grokopedia import router as grokopedia_router
from .api.marketing import router as marketing_router
from .api.errors import router as errors_router
from .api.rbac import router as rbac_router
from .api.mail import router as mail_router
from .api.workplace import router as workplace_router

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


# Include routers
app.include_router(auth_router, prefix="/api/v2/auth", tags=["Authentication"])
app.include_router(ai_router, prefix="/api/v2", tags=["AI"])
app.include_router(nexuslang_router, prefix="/api/v2", tags=["NexusLang"])
app.include_router(billing_router, prefix="/api/v2/billing", tags=["Billing"])
app.include_router(video_router, prefix="/api/v2/video", tags=["Video"])
app.include_router(projects_router, prefix="/api/v2/projects", tags=["Projects"])
app.include_router(teams_router, prefix="/api/v2/teams", tags=["Teams"])
app.include_router(analytics_router, prefix="/api/v2/analytics", tags=["Analytics"])
app.include_router(grokopedia_router, prefix="/api/v2", tags=["Grokopedia"])
app.include_router(marketing_router, prefix="/api/v2", tags=["Marketing"])
app.include_router(errors_router, prefix="/api/v2", tags=["Errors"])
app.include_router(rbac_router, prefix="/api/v2", tags=["RBAC"])
app.include_router(mail_router, prefix="/api/v2", tags=["Mail Integration"])
app.include_router(workplace_router, prefix="/api/v1", tags=["Workplace Service"])


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


# Add request ID middleware
app.middleware("http")(add_request_id)

# Add performance monitoring middleware
app.middleware("http")(performance_middleware)

# Add comprehensive monitoring middleware
app.middleware("http")(monitoring_middleware)

# Exception handlers
@app.exception_handler(GalionException)
async def galion_exception_handler(request, exc: GalionException):
    return await handle_galion_exception(request, exc)

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    return await handle_validation_exception(request, exc)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return await handle_http_exception(request, exc)

@app.exception_handler(Exception)
async def unexpected_exception_handler(request, exc: Exception):
    return await handle_unexpected_exception(request, exc)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("🚀 NexusLang v2 API starting up...")

    # Setup database performance monitoring
    try:
        from .core.database import engine
        setup_db_monitoring(engine)
        logger.info("✅ Database performance monitoring enabled")
    except Exception as e:
        logger.warning(f"Failed to setup database monitoring: {e}")

    # Initialize monitoring system
    try:
        monitoring_system = get_monitoring_system()
        logger.info("✅ Comprehensive monitoring system initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize monitoring system: {e}")

    # Initialize backup system
    try:
        backup_manager = get_backup_manager()
        logger.info("✅ Backup system initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize backup system: {e}")

    logger.info("✅ API documentation: http://localhost:8000/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("👋 NexusLang v2 API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
