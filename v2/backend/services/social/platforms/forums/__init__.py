"""
Forum Platform Connectors
Connectors for HackerNews, ProductHunt, dev.to, and generic forums
"""

from typing import Dict, Optional, List
from abc import ABC, abstractmethod


class ForumConnector(ABC):
    """
    Base class for forum connectors
    """
    
    def __init__(self, credentials: Dict):
        """
        Initialize forum connector
        
        Args:
            credentials: API keys, auth tokens
        """
        self.credentials = credentials
        self.platform_name = "forum"
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the forum"""
        pass
    
    @abstractmethod
    async def post_content(
        self,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Post content to the forum"""
        pass
    
    @abstractmethod
    async def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a forum post"""
        pass

