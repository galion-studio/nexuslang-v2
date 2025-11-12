"""
Main FastAPI application entry point for Auth Service.
This file sets up the FastAPI app with all middleware, routes, and configurations.
"""

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid

from app.config import settings
from app.api.v1 import auth, twofa
from app.database import engine, Base
from app.dependencies import get_current_user
from app.models.user import User

# Create database tables on startup
# In production, use Alembic migrations instead
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Nexus Core Authentication Service - Handles user registration, login, and JWT token management",
    docs_url="/docs",  # Swagger UI documentation
    redoc_url="/redoc"  # ReDoc documentation
)

# CORS middleware - allows frontend to make requests from different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),  # Parse from comma-separated string
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Request ID middleware - adds unique ID to every request for tracing
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """
    Add a unique request ID to every request for distributed tracing.
    
    If client sends X-Request-ID header, use it; otherwise generate new one.
    This allows tracing a request across multiple services.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Add request ID to response headers so client can reference it
    response.headers["X-Request-ID"] = request_id
    return response


# Security headers middleware - adds security headers to all responses
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Add security headers to all responses.
    Protects against common web vulnerabilities.
    """
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Allow microphone for voice features, allow geolocation for location-based services
    response.headers["Permissions-Policy"] = "geolocation=(self), microphone=(self), camera=(self)"
    
    # Remove server header to avoid information disclosure
    try:
        del response.headers["Server"]
    except KeyError:
        pass
    
    return response


# Logging middleware - log all requests with timing information
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log every request with timing information.
    
    In production, use structured logging (JSON) and send to aggregation service.
    This helps with debugging and performance monitoring.
    """
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log request (in production, use proper logging library)
    print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler - catch any unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch any unhandled exceptions and return a standard error response.
    
    This prevents internal errors from exposing sensitive information like:
    - Stack traces
    - Database connection strings
    - Internal file paths
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Log the error (in production, use proper logging and alerting)
    print(f"ERROR: {request_id} - {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred. Please try again later.",
                "request_id": request_id
            }
        }
    )


# Health check endpoint - for load balancers and monitoring
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns 200 if service is healthy and ready to handle traffic.
    Load balancers use this to know if they should send traffic to this instance.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT
    }


# Protected endpoint example - requires authentication
@app.get("/api/v1/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    
    This endpoint requires a valid JWT token in the Authorization header.
    Example: Authorization: Bearer <your-jwt-token>
    """
    return {
        "success": True,
        "data": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role,
            "email_verified": current_user.email_verified,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None
        }
    }


# Include API routes
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["authentication"]
)

app.include_router(
    twofa.router,
    prefix="/api/v1/2fa",
    tags=["two-factor-authentication"]
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Run tasks when application starts.
    
    Examples:
    - Initialize database connections
    - Load ML models
    - Connect to external services (Redis, Kafka)
    - Warm up caches
    """
    print(f"Starting {settings.APP_NAME}...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Run cleanup tasks when application stops.
    
    Examples:
    - Close database connections
    - Flush logs
    - Save state
    - Send shutdown notifications
    """
    print(f"Shutting down {settings.APP_NAME}...")


# Run with: python -m app.main (from services/auth-service directory)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes (development only)
    )

