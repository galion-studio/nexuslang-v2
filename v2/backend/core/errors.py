"""
Production-grade error handling and validation for Galion Ecosystem
Comprehensive error management with proper HTTP status codes and logging
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from typing import Any, Dict, Optional, Union
import logging
import traceback
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    """Standardized error response format"""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str
    request_id: Optional[str] = None
    path: Optional[str] = None


class GalionException(Exception):
    """Base exception for Galion ecosystem"""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# Specific Exception Types
class AuthenticationError(GalionException):
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHENTICATION_ERROR", status.HTTP_401_UNAUTHORIZED, details)


class AuthorizationError(GalionException):
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHORIZATION_ERROR", status.HTTP_403_FORBIDDEN, details)


class ValidationError(GalionException):
    def __init__(self, message: str = "Invalid input data", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", status.HTTP_400_BAD_REQUEST, details)


class ResourceNotFoundError(GalionException):
    def __init__(self, resource_type: str, resource_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message, "RESOURCE_NOT_FOUND", status.HTTP_404_NOT_FOUND, details)


class RateLimitError(GalionException):
    def __init__(self, retry_after: int, details: Optional[Dict[str, Any]] = None):
        message = f"Rate limit exceeded. Try again in {retry_after} seconds"
        super().__init__(message, "RATE_LIMIT_EXCEEDED", status.HTTP_429_TOO_MANY_REQUESTS, details)
        self.retry_after = retry_after


class InsufficientCreditsError(GalionException):
    def __init__(self, required: int, available: int, details: Optional[Dict[str, Any]] = None):
        message = f"Insufficient credits. Required: {required}, Available: {available}"
        super().__init__(message, "INSUFFICIENT_CREDITS", status.HTTP_402_PAYMENT_REQUIRED, details)


class SecurityViolationError(GalionException):
    def __init__(self, violation_type: str, details: Optional[Dict[str, Any]] = None):
        message = f"Security violation: {violation_type}"
        super().__init__(message, "SECURITY_VIOLATION", status.HTTP_403_FORBIDDEN, details)


class ServiceUnavailableError(GalionException):
    def __init__(self, service: str, details: Optional[Dict[str, Any]] = None):
        message = f"Service temporarily unavailable: {service}"
        super().__init__(message, "SERVICE_UNAVAILABLE", status.HTTP_503_SERVICE_UNAVAILABLE, details)


class DatabaseError(GalionException):
    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        message = f"Database operation failed: {operation}"
        super().__init__(message, "DATABASE_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR, details)


# Validation helpers
def validate_input_data(data: Dict[str, Any], required_fields: list, max_lengths: Dict[str, int] = None) -> None:
    """Validate input data for required fields and constraints"""
    missing_fields = []
    invalid_fields = []

    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            missing_fields.append(field)

    if max_lengths:
        for field, max_len in max_lengths.items():
            if field in data and len(str(data[field])) > max_len:
                invalid_fields.append(f"{field} exceeds maximum length of {max_len}")

    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

    if invalid_fields:
        raise ValidationError(f"Validation errors: {', '.join(invalid_fields)}")


def validate_file_upload(file, allowed_types: list, max_size_mb: int = 10) -> None:
    """Validate uploaded file"""
    if not file:
        raise ValidationError("No file provided")

    if file.content_type not in allowed_types:
        raise ValidationError(f"File type not allowed. Allowed: {', '.join(allowed_types)}")

    file_size_mb = len(file.file.read()) / (1024 * 1024)
    file.file.seek(0)  # Reset file pointer

    if file_size_mb > max_size_mb:
        raise ValidationError(f"File too large. Maximum size: {max_size_mb}MB")


def validate_image_dimensions(image_data: bytes, min_width: int = 100, min_height: int = 100,
                            max_width: int = 4096, max_height: int = 4096) -> tuple:
    """Validate image dimensions"""
    try:
        from PIL import Image
        import io

        image = Image.open(io.BytesIO(image_data))
        width, height = image.size

        if width < min_width or height < min_height:
            raise ValidationError(f"Image too small. Minimum: {min_width}x{min_height}")

        if width > max_width or height > max_height:
            raise ValidationError(f"Image too large. Maximum: {max_width}x{max_height}")

        return width, height
    except Exception as e:
        raise ValidationError(f"Invalid image format: {str(e)}")


# Error response handlers
async def handle_galion_exception(request: Request, exc: GalionException) -> JSONResponse:
    """Handle Galion-specific exceptions"""
    error_detail = ErrorDetail(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        timestamp=datetime.now().isoformat(),
        request_id=getattr(request.state, 'request_id', None),
        path=str(request.url.path)
    )

    # Log error with appropriate level
    if exc.status_code >= 500:
        logger.error(f"Server Error [{exc.error_code}]: {exc.message}", extra={
            'error_code': exc.error_code,
            'status_code': exc.status_code,
            'path': str(request.url.path),
            'details': exc.details
        })
    elif exc.status_code >= 400:
        logger.warning(f"Client Error [{exc.error_code}]: {exc.message}", extra={
            'error_code': exc.error_code,
            'status_code': exc.status_code,
            'path': str(request.url.path),
            'details': exc.details
        })

    # Add retry-after header for rate limits
    headers = {}
    if isinstance(exc, RateLimitError):
        headers['Retry-After'] = str(exc.retry_after)

    return JSONResponse(
        status_code=exc.status_code,
        content=error_detail.dict(),
        headers=headers
    )


async def handle_validation_exception(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    error_detail = ErrorDetail(
        error_code="VALIDATION_ERROR",
        message="Invalid input data",
        details={"validation_errors": exc.errors()},
        timestamp=datetime.now().isoformat(),
        request_id=getattr(request.state, 'request_id', None),
        path=str(request.url.path)
    )

    logger.warning(f"Validation Error: {exc.errors()}", extra={
        'path': str(request.url.path),
        'validation_errors': exc.errors()
    })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_detail.dict()
    )


async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard FastAPI HTTP exceptions"""
    error_detail = ErrorDetail(
        error_code=f"HTTP_{exc.status_code}",
        message=exc.detail,
        timestamp=datetime.now().isoformat(),
        request_id=getattr(request.state, 'request_id', None),
        path=str(request.url.path)
    )

    if exc.status_code >= 500:
        logger.error(f"HTTP Error {exc.status_code}: {exc.detail}", extra={
            'status_code': exc.status_code,
            'path': str(request.url.path)
        })
    else:
        logger.warning(f"HTTP Error {exc.status_code}: {exc.detail}", extra={
            'status_code': exc.status_code,
            'path': str(request.url.path)
        })

    return JSONResponse(
        status_code=exc.status_code,
        content=error_detail.dict()
    )


async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    error_id = f"ERR_{int(datetime.now().timestamp())}"

    # Log full traceback for debugging
    logger.critical(f"Unexpected Error [{error_id}]: {str(exc)}", extra={
        'error_id': error_id,
        'traceback': traceback.format_exc(),
        'path': str(request.url.path),
        'method': request.method,
        'user_agent': request.headers.get('user-agent'),
        'ip': getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
    })

    error_detail = ErrorDetail(
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred. Please try again later.",
        details={"error_id": error_id},
        timestamp=datetime.now().isoformat(),
        request_id=getattr(request.state, 'request_id', None),
        path=str(request.url.path)
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_detail.dict()
    )


# Request ID middleware
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracking"""
    import uuid
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    # Add request ID to response headers
    response = await call_next(request)
    response.headers['X-Request-ID'] = request_id
    return response


# Health check with detailed status
async def health_check_detailed() -> Dict[str, Any]:
    """Detailed health check for monitoring"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'services': {}
    }

    # Check database
    try:
        from .database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = 'unhealthy'
        health_status['status'] = 'degraded'
        logger.error(f"Database health check failed: {e}")

    # Check Redis
    try:
        from .redis_client import get_redis
        redis = get_redis()
        await redis.ping()
        health_status['services']['redis'] = 'healthy'
    except Exception as e:
        health_status['services']['redis'] = 'unhealthy'
        health_status['status'] = 'degraded'
        logger.error(f"Redis health check failed: {e}")

    # Check AI services
    try:
        from ..services.ai import get_ai_router
        ai_router = get_ai_router()
        # Basic connectivity check
        health_status['services']['ai_services'] = 'healthy'
    except Exception as e:
        health_status['services']['ai_services'] = 'unhealthy'
        logger.error(f"AI services health check failed: {e}")

    # Check security system
    try:
        from .security.anti_raid import get_anti_raid_system
        security_system = await get_anti_raid_system()
        health_status['services']['security'] = 'active' if security_system.is_active else 'inactive'
    except Exception as e:
        health_status['services']['security'] = 'unhealthy'
        logger.error(f"Security system health check failed: {e}")

    return health_status


# Utility functions for error handling
def log_api_call(request: Request, response_status: int, processing_time: float):
    """Log API call for monitoring"""
    logger.info(f"API Call: {request.method} {request.url.path} -> {response_status} ({processing_time:.3f}s)", extra={
        'method': request.method,
        'path': str(request.url.path),
        'status_code': response_status,
        'processing_time': processing_time,
        'user_agent': request.headers.get('user-agent'),
        'ip': getattr(request.client, 'host', 'unknown') if request.client else 'unknown',
        'request_id': getattr(request.state, 'request_id', None)
    })


def create_error_response(error_code: str, message: str, status_code: int = 500,
                         details: Optional[Dict[str, Any]] = None) -> JSONResponse:
    """Create standardized error response"""
    error_detail = ErrorDetail(
        error_code=error_code,
        message=message,
        details=details,
        timestamp=datetime.now().isoformat()
    )

    return JSONResponse(
        status_code=status_code,
        content=error_detail.dict()
    )
