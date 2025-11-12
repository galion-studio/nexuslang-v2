"""
Dev.to Forum Connector
Uses Dev.to API
"""

from typing import Dict, Optional, List
import aiohttp
from datetime import datetime

from . import ForumConnector
from .. import PlatformError, RateLimitError, AuthenticationError


class DevToConnector(ForumConnector):
    """
    Dev.to connector using REST API
    Supports creating articles and comments
    """
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.platform_name = "devto"
        self.base_url = "https://dev.to/api"
        self.api_key = credentials.get("api_key")
    
    async def authenticate(self) -> bool:
        """Authenticate with Dev.to API"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "api-key": self.api_key,
                    "Content-Type": "application/json"
                }
                # Get user info to verify auth
                async with session.get(f"{self.base_url}/users/me", headers=headers) as resp:
                    return resp.status == 200
        except Exception as e:
            raise AuthenticationError(self.platform_name, str(e))
    
    async def post_content(
        self,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Post an article to Dev.to
        
        metadata should include:
        - title: Article title (required)
        - tags: List of tags (max 4)
        - published: Boolean (default false for draft)
        - main_image: Cover image URL
        - canonical_url: Original article URL if cross-posting
        - series: Series name
        """
        if not metadata or not metadata.get("title"):
            raise PlatformError(self.platform_name, "Title is required for Dev.to articles")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "api-key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                # Prepare article data
                article_data = {
                    "article": {
                        "title": metadata["title"],
                        "body_markdown": content,
                        "published": metadata.get("published", False),
                        "tags": metadata.get("tags", [])[:4],  # Max 4 tags
                    }
                }
                
                # Optional fields
                if metadata.get("main_image"):
                    article_data["article"]["main_image"] = metadata["main_image"]
                if metadata.get("canonical_url"):
                    article_data["article"]["canonical_url"] = metadata["canonical_url"]
                if metadata.get("series"):
                    article_data["article"]["series"] = metadata["series"]
                if metadata.get("description"):
                    article_data["article"]["description"] = metadata["description"]
                
                # Create article
                async with session.post(
                    f"{self.base_url}/articles",
                    headers=headers,
                    json=article_data
                ) as resp:
                    if resp.status == 201:
                        result = await resp.json()
                        
                        article_id = result.get("id")
                        article_url = result.get("url")
                        
                        return {
                            "success": True,
                            "post_id": str(article_id),
                            "url": article_url,
                            "platform": self.platform_name
                        }
                    elif resp.status == 429:
                        raise RateLimitError(self.platform_name)
                    else:
                        error_data = await resp.json()
                        raise PlatformError(self.platform_name, f"Failed to post: {error_data}")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a Dev.to article"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "api-key": self.api_key
                }
                
                # Get article by ID
                async with session.get(
                    f"{self.base_url}/articles/{post_id}",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        reactions = result.get("public_reactions_count", 0)
                        comments = result.get("comments_count", 0)
                        page_views = result.get("page_views_count", 0)
                        
                        return {
                            "likes": reactions,  # Dev.to uses reactions (hearts, unicorns, etc.)
                            "comments": comments,
                            "shares": 0,
                            "views": page_views,
                            "engagement_rate": self._calculate_engagement(reactions, comments, page_views),
                            "platform_specific_metrics": {
                                "reactions": reactions,
                                "positive_reactions_count": result.get("positive_reactions_count", 0),
                                "reading_time_minutes": result.get("reading_time_minutes", 0)
                            }
                        }
                    else:
                        raise PlatformError(self.platform_name, "Failed to fetch analytics")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def update_article(self, post_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Update an existing Dev.to article"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "api-key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                article_data = {
                    "article": {
                        "body_markdown": content
                    }
                }
                
                if metadata:
                    if metadata.get("title"):
                        article_data["article"]["title"] = metadata["title"]
                    if "published" in metadata:
                        article_data["article"]["published"] = metadata["published"]
                
                async with session.put(
                    f"{self.base_url}/articles/{post_id}",
                    headers=headers,
                    json=article_data
                ) as resp:
                    return resp.status == 200
        
        except aiohttp.ClientError:
            return False
    
    def _calculate_engagement(self, reactions: int, comments: int, views: int) -> float:
        """Calculate engagement for Dev.to"""
        if views == 0:
            return 0.0
        total_engagement = reactions + comments
        return (total_engagement / views) * 100

