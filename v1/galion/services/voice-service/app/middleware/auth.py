"""
Authentication middleware for voice service
"""

from fastapi import WebSocket
from jose import JWTError, jwt
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


async def verify_websocket_token(websocket: WebSocket, token: Optional[str] = None) -> Optional[str]:
    """
    Verify JWT token for WebSocket connection
    
    Args:
        websocket: WebSocket connection
        token: JWT token (from query param or message)
    
    Returns:
        str: User email if valid, None otherwise
    """
    try:
        if not token:
            # Try to get from query params
            token = websocket.query_params.get("token")
        
        if not token:
            logger.warning("❌ No authentication token provided")
            return None
        
        # Decode JWT
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_email = payload.get("sub")
        if not user_email:
            logger.warning("❌ Invalid token: no user email")
            return None
        
        logger.info(f"✅ Authenticated user: {user_email}")
        return user_email
        
    except JWTError as e:
        logger.error(f"❌ JWT verification error: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        return None

