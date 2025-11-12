"""
FastAPI dependencies for authentication and authorization.
These are reusable functions that can be injected into endpoints.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth import verify_token

# HTTP Bearer token scheme - expects "Authorization: Bearer <token>" header
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    This is used in protected endpoints to ensure user is authenticated
    and to get their user object.
    
    Usage in endpoint:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}
    
    Args:
        credentials: HTTP Bearer credentials (JWT token)
        db: Database session
        
    Returns:
        User object if authentication successful
        
    Raises:
        401 Unauthorized: Invalid or expired token
        403 Forbidden: Account not active
    """
    
    token = credentials.credentials
    
    # Verify and decode token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get user from database
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Check account status
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status}"
        )
    
    return user


def require_role(required_role: str):
    """
    Dependency factory for role-based access control (RBAC).
    
    This creates a dependency that checks if user has the required role.
    
    Usage:
        @app.get("/admin-only", dependencies=[Depends(require_role("admin"))])
        def admin_route():
            return {"message": "Admin access granted"}
    
    Args:
        required_role: Role required to access endpoint ('admin', 'superadmin', etc.)
        
    Returns:
        Dependency function that checks role
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role"
            )
        return current_user
    return role_checker

