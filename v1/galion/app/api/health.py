"""
Health check endpoints for GALION applications
Implements comprehensive health and readiness checks
"""
from fastapi import APIRouter, status, Response
from typing import Dict, Any
import time
import asyncio
import shutil

router = APIRouter()

# Track service start time for uptime calculation
SERVICE_START_TIME = time.time()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check - returns 200 if app is running
    Used by: Docker healthcheck, load balancers
    
    Returns:
        dict: Basic health status
    """
    return {
        "status": "healthy",
        "service": "galion-api",
        "uptime_seconds": int(time.time() - SERVICE_START_TIME)
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check(response: Response) -> Dict[str, Any]:
    """
    Readiness check - verifies app can serve traffic
    Checks: database, redis, disk space
    Used by: Load balancers, Kubernetes readiness probes
    
    Returns:
        dict: Detailed readiness status
    """
    checks = {}
    
    # Run all health checks concurrently
    checks["database"] = await check_database()
    checks["redis"] = await check_redis()
    checks["disk_space"] = await check_disk_space()
    
    # Service is ready if all checks pass
    all_healthy = all(checks.values())
    
    # Set appropriate status code
    if not all_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": time.time()
    }


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check - app is alive and not deadlocked
    Used by: Kubernetes liveness probes
    
    Returns:
        dict: Liveness status
    """
    return {
        "status": "alive",
        "service": "galion-api",
        "uptime_seconds": int(time.time() - SERVICE_START_TIME)
    }


async def check_database() -> bool:
    """
    Check database connectivity
    
    Returns:
        bool: True if database is accessible
    """
    try:
        from app.core.database import engine
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False


async def check_redis() -> bool:
    """
    Check Redis connectivity
    
    Returns:
        bool: True if Redis is accessible
    """
    try:
        from app.core.cache import get_redis
        redis = await get_redis()
        await redis.ping()
        return True
    except Exception as e:
        print(f"Redis health check failed: {e}")
        return False


async def check_disk_space() -> bool:
    """
    Check if sufficient disk space is available (>10%)
    
    Returns:
        bool: True if disk space is sufficient
    """
    try:
        stat = shutil.disk_usage("/")
        free_percent = (stat.free / stat.total) * 100
        return free_percent > 10.0
    except Exception as e:
        print(f"Disk space health check failed: {e}")
        return False


@router.get("/health/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with performance metrics
    Used by: Monitoring dashboards, debugging
    
    Returns:
        dict: Comprehensive health and performance data
    """
    checks = {}
    metrics = {}
    
    # Run health checks
    checks["database"] = await check_database()
    checks["redis"] = await check_redis()
    checks["disk_space"] = await check_disk_space()
    
    # Get performance metrics
    try:
        # Disk usage
        stat = shutil.disk_usage("/")
        metrics["disk"] = {
            "total_gb": round(stat.total / (1024**3), 2),
            "used_gb": round(stat.used / (1024**3), 2),
            "free_gb": round(stat.free / (1024**3), 2),
            "free_percent": round((stat.free / stat.total) * 100, 2)
        }
        
        # Redis stats
        try:
            from app.core.cache import CacheManager
            redis_stats = await CacheManager.get_stats()
            metrics["redis"] = redis_stats
        except:
            metrics["redis"] = {"error": "Unable to fetch Redis stats"}
        
        # Database stats
        try:
            from app.core.database import engine
            async with engine.begin() as conn:
                result = await conn.execute(
                    """
                    SELECT 
                        count(*) as active_connections,
                        max(extract(epoch from (now() - backend_start))) as max_connection_age
                    FROM pg_stat_activity 
                    WHERE state = 'active'
                    """
                )
                row = result.fetchone()
                metrics["database"] = {
                    "active_connections": row[0],
                    "max_connection_age_seconds": round(row[1] or 0, 2)
                }
        except:
            metrics["database"] = {"error": "Unable to fetch database stats"}
            
    except Exception as e:
        metrics["error"] = str(e)
    
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "service": "galion-api",
        "uptime_seconds": int(time.time() - SERVICE_START_TIME),
        "checks": checks,
        "metrics": metrics,
        "timestamp": time.time()
    }

