"""
NexusLang v2 Platform - Main API Server
FastAPI application with all unified services
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from core.config import settings
from core.database import init_db
from core.redis_client import get_redis, close_redis
from core.security_middleware import (
    RateLimitMiddleware, 
    SecurityHeadersMiddleware,
    AuditLoggingMiddleware,
    RequestValidationMiddleware,
    get_audit_logger
)
from core.security import decode_access_token
from api import (
    auth, nexuslang, ide, grokopedia, voice, billing, community,
    password_reset, email_verification, security_monitoring, content_manager, ai, analytics
)
# Import Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting NexusLang v2 Platform...")
    
    # SECURITY: Validate configuration before doing anything else
    # This will exit the application if critical security settings are missing
    from core.security_validation import validate_all_secrets
    validate_all_secrets()
    
    # Initialize database
    try:
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Warning: Database initialization issue: {e}")
        print("   Server will still start, but database features may not work")
    
    # Initialize Redis
    try:
        redis = await get_redis()
        if redis.is_connected:
            print("✅ Redis connected - distributed features enabled")
        else:
            print("⚠️  Redis not available - using in-memory fallbacks")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("   Using in-memory fallbacks (not recommended for production)")
    
    yield
    
    # Shutdown
    print("👋 Shutting down NexusLang v2 Platform...")
    await close_redis()

# Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI requests',
    ['model', 'status']
)

ai_tokens_total = Counter(
    'ai_tokens_total',
    'Total AI tokens used',
    ['model']
)

# Create FastAPI app
app = FastAPI(
    title="NexusLang v2 API",
    description="Unified API for the NexusLang v2 Platform",
    version="2.0.0-beta",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security middleware stack (order matters!)
# 1. Request validation (first line of defense)
app.add_middleware(RequestValidationMiddleware)

# 2. Rate limiting (prevent abuse)
app.add_middleware(RateLimitMiddleware)

# 3. Security headers (protect responses)
app.add_middleware(SecurityHeadersMiddleware)

# 4. Audit logging (track security events)
app.add_middleware(AuditLoggingMiddleware)

# 5. CORS middleware (control cross-origin requests)
# Use explicit methods and headers for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "Accept"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns service status and version info.
    """
    return {
        "status": "healthy",
        "service": "nexuslang-v2-api",
        "version": "2.0.0-beta"
    }

# Detailed health check endpoint
@app.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with all component statuses.
    """
    from core.health_checks import get_health_check_system
    
    health_system = get_health_check_system()
    return await health_system.run_all_checks()

# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    Exposes metrics in Prometheus format.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to NexusLang v2 API",
        "version": "2.0.0-beta",
        "docs": "/docs",
        "health": "/health"
    }

# Include routers for different services
app.include_router(auth.router, prefix="/api/v2/auth", tags=["Authentication"])
app.include_router(password_reset.router, prefix="/api/v2/password", tags=["Password Management"])
app.include_router(email_verification.router, prefix="/api/v2/email", tags=["Email Verification"])
app.include_router(security_monitoring.router, prefix="/api/v2/security", tags=["Security Monitoring"])
app.include_router(nexuslang.router, prefix="/api/v2/nexuslang", tags=["NexusLang"])
app.include_router(ide.router, prefix="/api/v2/ide", tags=["IDE"])
app.include_router(grokopedia.router, prefix="/api/v2/grokopedia", tags=["Grokopedia"])
app.include_router(voice.router, prefix="/api/v2/voice", tags=["Voice"])
app.include_router(billing.router, prefix="/api/v2/billing", tags=["Billing"])
app.include_router(community.router, prefix="/api/v2/community", tags=["Community"])
app.include_router(content_manager.router, prefix="/api/v2", tags=["Content Manager"])
app.include_router(ai.router, prefix="/api/v2/ai", tags=["AI"])
app.include_router(analytics.router, prefix="/api/v2/analytics", tags=["Analytics"])

# WebSocket endpoint for real-time features
@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str, token: str = None):
    """
    WebSocket endpoint for real-time communication with authentication.
    
    Supports: ide, voice, notifications, live-coding
    
    Authentication: Send token as query parameter: /ws/channel?token=your_jwt_token
    """
    # Authenticate before accepting connection
    user_id = None
    if token:
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
    
    if not user_id:
        # Reject unauthenticated connections
        await websocket.close(code=1008, reason="Authentication required")
        return
    
    # Accept authenticated connection
    await websocket.accept()
    
    # Log connection for audit
    audit_logger = get_audit_logger()
    audit_logger.log_event(
        event_type="websocket_connect",
        user_id=user_id,
        request=websocket,
        details={"channel": channel},
        severity="info"
    )
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Log significant WebSocket activity
            if channel in ["voice", "code"]:
                audit_logger.log_event(
                    event_type="websocket_message",
                    user_id=user_id,
                    request=websocket,
                    details={"channel": channel, "data_length": len(data)},
                    severity="info"
                )
            
            # Route to appropriate handler based on channel
            # For now, echo back - implement proper handlers per channel
            await websocket.send_text(f"Authenticated Echo (User: {user_id}): {data}")
            
    except WebSocketDisconnect:
        audit_logger.log_event(
            event_type="websocket_disconnect",
            user_id=user_id,
            request=websocket,
            details={"channel": channel},
            severity="info"
        )
    except Exception as e:
        print(f"WebSocket error: {e}")
        audit_logger.log_event(
            event_type="websocket_error",
            user_id=user_id,
            request=websocket,
            details={"channel": channel, "error": str(e)},
            severity="error"
        )
    finally:
        await websocket.close()

# Error handlers (with audit logging for security events)
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "path": str(request.url.path)  # Don't leak full URL with query params
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    # Log internal errors for investigation
    audit_logger = get_audit_logger()
    audit_logger.log_event(
        event_type="internal_error",
        user_id=None,
        request=request,
        details={"error": str(exc)},
        severity="critical"
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

