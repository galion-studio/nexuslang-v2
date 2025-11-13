"""
Error reporting API endpoint
Handles client-side error reporting and monitoring
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from ..core.database import get_db

router = APIRouter(prefix="/errors", tags=["Errors"])

logger = logging.getLogger(__name__)


class ErrorReport(BaseModel):
    error_id: str
    message: str
    stack: Optional[str] = None
    component_stack: Optional[str] = None
    timestamp: str
    url: str
    user_agent: str
    viewport: Optional[Dict[str, int]] = None
    additional_data: Optional[Dict[str, Any]] = None


@router.post("/report")
async def report_error(report: ErrorReport):
    """
    Report a client-side error for monitoring and debugging
    """
    try:
        # Log the error for monitoring
        logger.warning(f"Client Error Report [{report.error_id}]: {report.message}", extra={
            'error_id': report.error_id,
            'url': report.url,
            'user_agent': report.user_agent,
            'timestamp': report.timestamp,
            'stack': report.stack,
            'component_stack': report.component_stack,
            'viewport': report.viewport,
            'additional_data': report.additional_data
        })

        # In production, you might want to:
        # 1. Store in database for analysis
        # 2. Send to error monitoring service (Sentry, Rollbar, etc.)
        # 3. Trigger alerts for critical errors
        # 4. Aggregate error patterns for debugging

        # For now, just acknowledge receipt
        return {
            "acknowledged": True,
            "error_id": report.error_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to process error report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process error report"
        )


@router.get("/stats")
async def get_error_stats():
    """
    Get error statistics for monitoring dashboard
    """
    # In production, this would query actual error data
    # For now, return mock statistics
    return {
        "total_errors": 42,
        "errors_today": 7,
        "errors_this_week": 28,
        "top_error_types": [
            {"type": "TypeError", "count": 15},
            {"type": "NetworkError", "count": 12},
            {"type": "ValidationError", "count": 8},
            {"type": "ReferenceError", "count": 7}
        ],
        "most_affected_pages": [
            {"page": "/grokopedia", "errors": 18},
            {"page": "/developer/marketing", "errors": 12},
            {"page": "/auth/login", "errors": 8},
            {"page": "/", "errors": 4}
        ],
        "error_trends": {
            "daily": [2, 5, 3, 7, 4, 6, 7],
            "weekly": [45, 52, 48, 61, 55, 49, 42]
        }
    }
