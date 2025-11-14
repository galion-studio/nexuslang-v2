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

# Import error handlers - using absolute imports for uvicorn compatibility
try:
    from core.errors import (
        handle_galion_exception,
        handle_validation_exception,
        handle_http_exception,
        handle_unexpected_exception,
        add_request_id,
        GalionException
    )
    from core.performance import performance_middleware, setup_db_monitoring
    from core.monitoring import monitoring_middleware, get_monitoring_system
    from core.backup import get_backup_manager
    print("✅ Core imports successful")
except ImportError as e:
    print(f"⚠️  Core imports failed, using fallbacks: {e}")
    handle_galion_exception = None
    performance_middleware = None
    monitoring_middleware = None
    get_backup_manager = None

# Import routers individually - using absolute imports for uvicorn compatibility
try:
    from api.auth import router as auth_router
    from api.ai import router as ai_router
    from api.nexuslang import router as nexuslang_router
    from api.billing import router as billing_router
    from api.video import router as video_router
    from api.projects import router as projects_router
    from api.teams import router as teams_router
    from api.analytics import router as analytics_router
    from api.grokopedia import router as grokopedia_router
    from api.marketing import router as marketing_router
    from api.errors import router as errors_router
    from api.rbac import router as rbac_router
    from api.mail import router as mail_router
    from api.workplace import router as workplace_router
    print("✅ Router imports successful")
except ImportError as e:
    print(f"⚠️  Router imports failed: {e}")
    auth_router = ai_router = nexuslang_router = billing_router = video_router = None
    projects_router = teams_router = analytics_router = grokopedia_router = None
    marketing_router = errors_router = rbac_router = mail_router = workplace_router = None

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


# Include routers - only include if available
if auth_router:
    app.include_router(auth_router, prefix="/api/v2/auth", tags=["Authentication"])
    print("✅ Auth router included")
else:
    print("⚠️  Auth router not available")

if ai_router:
    app.include_router(ai_router, prefix="/api/v2", tags=["AI"])
    print("✅ AI router included")
else:
    print("⚠️  AI router not available")

if nexuslang_router:
    app.include_router(nexuslang_router, prefix="/api/v2", tags=["NexusLang"])
    print("✅ NexusLang router included")
else:
    print("⚠️  NexusLang router not available")

if billing_router:
    app.include_router(billing_router, prefix="/api/v2/billing", tags=["Billing"])
    print("✅ Billing router included")
else:
    print("⚠️  Billing router not available")

if video_router:
    app.include_router(video_router, prefix="/api/v2/video", tags=["Video"])
    print("✅ Video router included")
else:
    print("⚠️  Video router not available")

if projects_router:
    app.include_router(projects_router, prefix="/api/v2/projects", tags=["Projects"])
    print("✅ Projects router included")
else:
    print("⚠️  Projects router not available")

if teams_router:
    app.include_router(teams_router, prefix="/api/v2/teams", tags=["Teams"])
    print("✅ Teams router included")
else:
    print("⚠️  Teams router not available")

if analytics_router:
    app.include_router(analytics_router, prefix="/api/v2/analytics", tags=["Analytics"])
    print("✅ Analytics router included")
else:
    print("⚠️  Analytics router not available")

if grokopedia_router:
    app.include_router(grokopedia_router, prefix="/api/v2", tags=["Grokopedia"])
    print("✅ Grokopedia router included")
else:
    print("⚠️  Grokopedia router not available")

if marketing_router:
    app.include_router(marketing_router, prefix="/api/v2", tags=["Marketing"])
    print("✅ Marketing router included")
else:
    print("⚠️  Marketing router not available")

if errors_router:
    app.include_router(errors_router, prefix="/api/v2", tags=["Errors"])
    print("✅ Errors router included")
else:
    print("⚠️  Errors router not available")

if rbac_router:
    app.include_router(rbac_router, prefix="/api/v2", tags=["RBAC"])
    print("✅ RBAC router included")
else:
    print("⚠️  RBAC router not available")

if mail_router:
    app.include_router(mail_router, prefix="/api/v2", tags=["Mail Integration"])
    print("✅ Mail router included")
else:
    print("⚠️  Mail router not available")

if workplace_router:
    app.include_router(workplace_router, prefix="/api/v1", tags=["Workplace Service"])
    print("✅ Workplace router included")
else:
    print("⚠️  Workplace router not available")


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
if add_request_id:
    app.middleware("http")(add_request_id)

# Add performance monitoring middleware
if performance_middleware:
    app.middleware("http")(performance_middleware)

# Add comprehensive monitoring middleware
if monitoring_middleware:
    app.middleware("http")(monitoring_middleware)

# Exception handlers - only add if handlers are available
if GalionException and handle_galion_exception:
    @app.exception_handler(GalionException)
    async def galion_exception_handler(request, exc: GalionException):
        return await handle_galion_exception(request, exc)

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    if handle_validation_exception:
        return await handle_validation_exception(request, exc)
    else:
        return JSONResponse(
            status_code=422,
            content={"error": "Validation error", "details": str(exc)}
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    if handle_http_exception:
        return await handle_http_exception(request, exc)
    else:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )

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
        from core.database import engine
        if setup_db_monitoring:
            setup_db_monitoring(engine)
            logger.info("✅ Database performance monitoring enabled")
        else:
            logger.warning("Database monitoring setup not available")
    except Exception as e:
        logger.warning(f"Failed to setup database monitoring: {e}")

    # Initialize monitoring system
    try:
        if get_monitoring_system:
            monitoring_system = get_monitoring_system()
            logger.info("✅ Comprehensive monitoring system initialized")
        else:
            logger.warning("Monitoring system not available")
    except Exception as e:
        logger.warning(f"Failed to initialize monitoring system: {e}")

    # Initialize backup system
    try:
        if get_backup_manager:
            backup_manager = get_backup_manager()
            logger.info("✅ Backup system initialized")
        else:
            logger.warning("Backup manager not available")
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
