"""
Main FastAPI Application for CMS
Entry point for the Content Management System API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth_router, category_router, content_router

# Create database tables
# This automatically creates all tables defined in models.py
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Simple CMS API",
    description="A clean and simple Content Management System",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI documentation
    redoc_url="/redoc"  # ReDoc documentation
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows the frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers for different API sections
app.include_router(auth_router.router)
app.include_router(category_router.router)
app.include_router(content_router.router)

# Root endpoint
@app.get("/")
def root():
    """
    Welcome endpoint
    Returns basic API information
    """
    return {
        "message": "Welcome to Simple CMS API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint
    Used to verify the API is running
    """
    return {
        "status": "healthy",
        "service": "cms-api"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Runs when the application starts
    Good place for initialization tasks
    """
    print("🚀 CMS API starting up...")
    print("📚 Documentation available at /docs")
    print("✅ API is ready to accept requests")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs when the application shuts down
    Good place for cleanup tasks
    """
    print("👋 CMS API shutting down...")

