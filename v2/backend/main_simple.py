"""
Simplified Nexus Lang V2 Server for RunPod Deployment
=======================================================

This is a simplified version that focuses on reliability and 
working imports. It will start successfully even if some 
optional modules are not available.

Author: Project Nexus Team
Date: 2025-11-14
"""

import os
import sys
import logging
import time
import traceback
from typing import Dict, Any, Optional

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# Try importing optional dependencies
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available - system info endpoint will be limited")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    logger.info("NEXUS LANG V2 SCIENTIFIC PLATFORM - Server started successfully")
    yield
    # Shutdown
    logger.info("Server shutting down")

# Create FastAPI application
app = FastAPI(
    title="Nexus Lang V2 Scientific Platform",
    description="Scientific knowledge enhancement and research platform",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS - allow all origins and subdomains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3030",

        # galion.studio domains
        "https://api.galion.studio",
        "https://studio.galion.studio",
        "https://app.galion.studio",
        "https://dev.galion.studio",
        "https://developer.galion.studio",
        "https://galion.studio",
        "https://www.galion.studio",

        # galion.app domains
        "https://galion.app",
        "https://www.galion.app",
        "https://api.galion.app",
        "https://studio.galion.app",
        "https://dev.galion.app",

        # HTTP versions (for development)
        "http://api.galion.studio",
        "http://studio.galion.studio",
        "http://app.galion.studio",
        "http://dev.galion.studio",
        "http://galion.studio",
        "http://www.galion.studio",
        "http://galion.app",
        "http://www.galion.app",
        "http://api.galion.app",
        "http://studio.galion.app",
        "http://dev.galion.app",

        # RunPod direct access
        "http://213.173.105.83:3000",
        "http://213.173.105.83:3001",
        "http://213.173.105.83:3003",
        "http://213.173.105.83:3030",

        # Wildcard for any subdomain (development)
        "*",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Pydantic Models
class HealthCheck(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]

class SystemInfo(BaseModel):
    """System information response model."""
    status: str
    version: str
    python_version: str
    platform: str
    memory_usage: Optional[Dict[str, Any]] = None
    cpu_usage: Optional[float] = None

class QueryRequest(BaseModel):
    """Basic query request model."""
    query: str = Field(..., description="Your question or query")
    domain: Optional[str] = Field(None, description="Domain focus (optional)")

class QueryResponse(BaseModel):
    """Query response model."""
    success: bool
    message: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None

# ============================================================================
# Core Endpoints
# ============================================================================

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information.
    Shows available endpoints and system status.
    """
    return {
        "message": "🧠 Nexus Lang V2 Scientific Platform",
        "description": "Advanced scientific knowledge enhancement system",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "system_info": "/system-info",
            "api_docs": "/docs",
            "openapi": "/openapi.json"
        },
        "api_endpoints": {
            "basic_query": "/api/v1/query",
            "grokopedia_test": "/api/v1/test",
            "scientific_capabilities": "/api/v1/scientific-capabilities"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    """
    Health check endpoint.
    Returns server status and available services.
    """
    # Check which services are available
    services_status = {
        "core_api": "available",
        "psutil": "available" if PSUTIL_AVAILABLE else "unavailable"
    }
    
    # Try to import and check optional services
    try:
        from api.grokopedia import router
        services_status["grokopedia"] = "available"
    except Exception:
        services_status["grokopedia"] = "unavailable"
    
    return HealthCheck(
        status="healthy",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        version="2.0.0",
        services=services_status
    )

@app.get("/system-info", response_model=SystemInfo, tags=["system"])
async def system_info():
    """
    Get system information.
    Returns details about server status, memory, CPU, etc.
    """
    memory_info = None
    cpu_usage = None
    
    # Get system info if psutil is available
    if PSUTIL_AVAILABLE:
        try:
            memory = psutil.virtual_memory()
            memory_info = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percent": memory.percent
            }
            cpu_usage = psutil.cpu_percent(interval=1)
        except Exception as e:
            logger.warning(f"Could not get system info: {e}")
    
    return SystemInfo(
        status="operational",
        version="2.0.0",
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        platform=sys.platform,
        memory_usage=memory_info,
        cpu_usage=cpu_usage
    )

# ============================================================================
# API V1 Endpoints
# ============================================================================

@app.get("/api/v1/test", tags=["api"])
async def api_test():
    """
    Simple API test endpoint.
    Confirms the API is working.
    """
    return {
        "status": "working",
        "message": "API v1 is operational",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

@app.get("/api/v1/scientific-capabilities", tags=["api"])
async def scientific_capabilities():
    """
    Get scientific capabilities of the system.
    Shows what domains and features are supported.
    """
    return {
        "supported_domains": [
            "physics",
            "chemistry",
            "mathematics",
            "biology",
            "computer_science",
            "history",
            "law"
        ],
        "features": {
            "first_principles_analysis": True,
            "multi_agent_collaboration": True,
            "deep_research": True,
            "citation_management": True,
            "knowledge_integration": True
        },
        "capabilities": {
            "extremely_deep_understanding": True,
            "causal_reasoning": True,
            "historical_analysis": True,
            "legal_analysis": True
        }
    }

@app.post("/api/v1/query", response_model=QueryResponse, tags=["api"])
async def basic_query(request: QueryRequest):
    """
    Basic query endpoint.
    Accepts a query and returns a response.
    
    This is a simplified version that returns mock data.
    In production, this would connect to the full AI system.
    """
    start_time = time.time()
    
    try:
        # In production, this would use the full agent orchestrator
        # For now, return a helpful response
        response_data = {
            "query": request.query,
            "domain": request.domain or "general",
            "response": f"Query received: '{request.query}'. Full AI system integration pending.",
            "processing_time": round(time.time() - start_time, 3),
            "confidence": 0.85,
            "note": "This is a simplified response. Full AI capabilities will be available when all services are configured."
        }
        
        return QueryResponse(
            success=True,
            message="Query processed successfully",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        logger.error(traceback.format_exc())
        
        return QueryResponse(
            success=False,
            message=f"Query failed: {str(e)}",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            data={"error": str(e)}
        )

# ============================================================================
# Try to include Grokopedia router if available
# ============================================================================

try:
    from api.grokopedia import router as grokopedia_router
    app.include_router(grokopedia_router, prefix="/api/v1/grokopedia", tags=["grokopedia"])
    logger.info("Grokopedia router loaded successfully")
except Exception as e:
    logger.warning(f"Could not load Grokopedia router: {e}")
    logger.info("Server will start without Grokopedia endpoints")

# ============================================================================
# Direct Grokopedia Endpoints (Backup Routes)
# ============================================================================

@app.get("/grokopedia/", tags=["grokopedia"])
async def grokopedia_home():
    """Grokopedia home endpoint."""
    return {
        "service": "grokopedia",
        "status": "available",
        "version": "1.0.0",
        "description": "Scientific Knowledge Graph and Research Platform",
        "endpoints": {
            "topics": "/grokopedia/topics",
            "search": "/grokopedia/search",
            "api": "/api/v1/grokopedia/"
        }
    }

@app.get("/grokopedia/topics", tags=["grokopedia"])
async def grokopedia_topics():
    """Get available Grokopedia topics."""
    return {
        "topics": [
            "Physics", "Chemistry", "Biology", "Mathematics",
            "Computer Science", "Engineering", "Medicine"
        ],
        "total": 7,
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

# ============================================================================
# Direct NexusLang Endpoints (Backup Routes)
# ============================================================================

@app.post("/nexuslang/compile", tags=["nexuslang"])
async def nexuslang_compile(request: Request):
    """NexusLang compile endpoint."""
    body = await request.json()
    code = body.get("code", "")
    
    return {
        "success": True,
        "message": "Compilation endpoint available",
        "code_length": len(code),
        "note": "Full compiler integration coming soon"
    }

@app.get("/nexuslang/", tags=["nexuslang"])
async def nexuslang_home():
    """NexusLang home endpoint."""
    return {
        "service": "nexuslang",
        "status": "available",
        "version": "2.0.0",
        "description": "NexusLang Compiler and Runtime",
        "endpoints": {
            "compile": "/nexuslang/compile",
            "execute": "/nexuslang/execute",
            "api": "/api/v1/nexuslang/"
        }
    }

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "status_code": exc.status_code
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred",
                "details": str(exc)
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    )

# ============================================================================
# Application Lifespan Handled Above
# ============================================================================

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("WORKERS", "2"))
    
    print(f"Starting Nexus Lang V2 Server")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Workers: {workers}")
    print("=" * 60)
    
    # Run server
    uvicorn.run(
        "main_simple:app",
        host=host,
        port=port,
        workers=workers,
        log_level="info",
        access_log=True
    )

