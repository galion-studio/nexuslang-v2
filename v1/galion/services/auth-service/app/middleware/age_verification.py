"""
Age Verification Middleware - 18+ Requirement
Ensures all users accessing the platform are adults (18+)
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.user import User


class AgeVerificationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce 18+ age requirement across the platform.
    
    All routes except public ones require age verification.
    """
    
    # Routes that don't require age verification
    EXEMPT_ROUTES = [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/register",  # Users verify age during registration
        "/api/v1/auth/login"
    ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Check if user is age-verified for protected routes.
        """
        
        # Skip age check for exempt routes
        if self._is_exempt_route(request.url.path):
            return await call_next(request)
        
        # Skip for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Check if user is authenticated and age-verified
        # Note: This assumes authentication middleware runs first
        if hasattr(request.state, "user"):
            user = request.state.user
            
            # Check if user has verified their age
            if not user.age_verified:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "AGE_VERIFICATION_REQUIRED",
                        "message": "You must verify your age (18+) to access this platform",
                        "required_age": 18
                    }
                )
            
            # Additional check: Verify date of birth is set and user is adult
            if user.date_of_birth:
                today = datetime.now().date()
                age = today.year - user.date_of_birth.year - (
                    (today.month, today.day) < (user.date_of_birth.month, user.date_of_birth.day)
                )
                
                if age < 18:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={
                            "code": "UNDERAGE_USER",
                            "message": "Access denied. You must be at least 18 years old.",
                            "required_age": 18
                        }
                    )
        
        # Continue with request
        return await call_next(request)
    
    def _is_exempt_route(self, path: str) -> bool:
        """Check if route is exempt from age verification."""
        return any(path.startswith(route) for route in self.EXEMPT_ROUTES)


def require_adult(user: User) -> User:
    """
    Dependency to require adult verification for specific endpoints.
    
    Usage in routes:
        @app.get("/adult-content")
        def adult_content(user: User = Depends(require_adult)):
            ...
    """
    if not user.age_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Age verification required (18+)"
        )
    
    if user.date_of_birth:
        today = datetime.now().date()
        age = today.year - user.date_of_birth.year - (
            (today.month, today.day) < (user.date_of_birth.month, user.date_of_birth.day)
        )
        
        if age < 18:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be at least 18 years old to access this content"
            )
    
    return user

