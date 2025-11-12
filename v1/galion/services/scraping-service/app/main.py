"""
NEXUS SCRAPING SERVICE - Minimal MVP
Built following Elon Musk's First Principles - MVP first, enhance later
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Nexus Scraping Service",
    description="AI-powered web scraping service",
    version="0.1.0"
)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint - MUST respond quickly"""
    return {
        "status": "healthy",
        "service": "scraping-service",
        "version": "0.1.0"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        "# HELP scraping_service_up Scraping Service status\n"
        "# TYPE scraping_service_up gauge\n"
        "scraping_service_up 1\n",
        media_type="text/plain"
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Nexus Scraping Service",
        "status": "operational",
        "message": "Scraping service is running. Use /docs for API documentation."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

