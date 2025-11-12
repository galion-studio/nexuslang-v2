"""
Social Media Platform Connectors
Base classes and utilities for platform integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from datetime import datetime


class PlatformConnector(ABC):
    """
    Base class for all social media platform connectors
    Each platform implements this interface
    """
    
    def __init__(self, credentials: Dict):
        """
        Initialize connector with platform credentials
        
        Args:
            credentials: OAuth tokens, API keys, etc.
        """
        self.credentials = credentials
        self.platform_name = "base"
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the platform
        Returns True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def post_content(
        self,
        content: str,
        media_urls: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Post content to the platform
        
        Args:
            content: Text content to post
            media_urls: Optional list of media URLs
            metadata: Platform-specific metadata (hashtags, mentions, etc.)
        
        Returns:
            Dict with post_id, url, and status
        """
        pass
    
    @abstractmethod
    async def get_post_analytics(self, post_id: str) -> Dict:
        """
        Get analytics for a specific post
        
        Args:
            post_id: Platform-specific post ID
        
        Returns:
            Dict with likes, comments, shares, views, etc.
        """
        pass
    
    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a post from the platform
        
        Args:
            post_id: Platform-specific post ID
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate that credentials are still valid
        
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def format_content(self, content: str, max_length: Optional[int] = None) -> str:
        """
        Format content for platform-specific requirements
        
        Args:
            content: Original content
            max_length: Maximum character length
        
        Returns:
            Formatted content
        """
        if max_length and len(content) > max_length:
            return content[:max_length-3] + "..."
        return content
    
    def extract_hashtags(self, content: str) -> List[str]:
        """
        Extract hashtags from content
        
        Args:
            content: Content to parse
        
        Returns:
            List of hashtags
        """
        import re
        return re.findall(r'#\w+', content)
    
    def extract_mentions(self, content: str, mention_pattern: str = r'@\w+') -> List[str]:
        """
        Extract mentions from content
        
        Args:
            content: Content to parse
            mention_pattern: Regex pattern for mentions
        
        Returns:
            List of mentions
        """
        import re
        return re.findall(mention_pattern, content)


class PlatformError(Exception):
    """Custom exception for platform-related errors"""
    
    def __init__(self, platform: str, message: str, details: Optional[Dict] = None):
        self.platform = platform
        self.message = message
        self.details = details or {}
        super().__init__(f"{platform}: {message}")


class RateLimitError(PlatformError):
    """Exception for rate limit errors"""
    
    def __init__(self, platform: str, retry_after: Optional[int] = None):
        message = f"Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(platform, message, {"retry_after": retry_after})


class AuthenticationError(PlatformError):
    """Exception for authentication errors"""
    
    def __init__(self, platform: str, message: str = "Authentication failed"):
        super().__init__(platform, message)

