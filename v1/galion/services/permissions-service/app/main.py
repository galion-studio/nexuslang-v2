"""
Permissions Service - RBAC System
FastAPI application for role-based access control
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import os

from app.routers import roles, permissions, assignments
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Prometheus metrics
REQUEST_COUNT = Counter('permissions_service_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('permissions_service_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
PERMISSION_CHECKS = Counter('permissions_service_checks_total', 'Total permission checks', ['result'])

app = FastAPI(
    title="Permissions Service",
    description="Role-based access control (RBAC) system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Record metrics
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routers
app.include_router(roles.router, prefix="/api/v1/permissions/roles", tags=["Roles"])
app.include_router(permissions.router, prefix="/api/v1/permissions", tags=["Permissions"])
app.include_router(assignments.router, prefix="/api/v1/permissions", tags=["Assignments"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "permissions-service",
        "version": "1.0.0"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import Response
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Permissions Service (RBAC)",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "roles": "/api/v1/permissions/roles",
            "permissions": "/api/v1/permissions"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)

