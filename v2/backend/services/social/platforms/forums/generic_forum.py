"""
Generic Forum Connector
Flexible connector for custom/niche forums using common patterns
"""

from typing import Dict, Optional, List
import aiohttp
from datetime import datetime
import re

from . import ForumConnector
from .. import PlatformError, AuthenticationError


class GenericForumConnector(ForumConnector):
    """
    Generic forum connector for custom forums
    Supports common REST API patterns and basic web scraping
    
    Configuration via credentials dict:
    - base_url: Forum base URL
    - auth_type: 'api_key', 'bearer', 'basic', 'session'
    - api_key / bearer_token / username / password
    - post_endpoint: Endpoint for posting
    - analytics_endpoint: Endpoint for fetching analytics
    - custom_headers: Additional headers
    """
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.platform_name = credentials.get("platform_name", "generic_forum")
        self.base_url = credentials.get("base_url", "")
        self.auth_type = credentials.get("auth_type", "api_key")
        self.api_key = credentials.get("api_key")
        self.bearer_token = credentials.get("bearer_token")
        self.username = credentials.get("username")
        self.password = credentials.get("password")
        self.custom_headers = credentials.get("custom_headers", {})
        self.post_endpoint = credentials.get("post_endpoint", "/api/posts")
        self.analytics_endpoint = credentials.get("analytics_endpoint", "/api/posts/{id}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Build headers based on auth type"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "GalionStudio-ContentManager/1.0"
        }
        
        # Add authentication
        if self.auth_type == "api_key" and self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.auth_type == "bearer" and self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        elif self.auth_type == "basic" and self.username and self.password:
            import base64
            auth_string = f"{self.username}:{self.password}"
            encoded = base64.b64encode(auth_string.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
        
        # Add custom headers
        headers.update(self.custom_headers)
        
        return headers
    
    async def authenticate(self) -> bool:
        """
        Authenticate with the forum
        For session-based auth, this would handle login
        """
        if not self.base_url:
            raise AuthenticationError(self.platform_name, "Base URL not configured")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = self._get_headers()
                
                # Try a simple GET request to verify connectivity
                async with session.get(
                    f"{self.base_url}/health",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    return resp.status in [200, 404]  # 404 is ok, means server is up
        except Exception as e:
            # If health check fails, try base URL
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.base_url,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as resp:
                        return resp.status == 200
            except:
                return False
    
    async def post_content(
        self,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Post content to generic forum
        
        metadata can include:
        - title: Post title
        - category: Forum category/section
        - tags: List of tags
        - Any other forum-specific fields
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = self._get_headers()
                
                # Prepare post data (flexible structure)
                post_data = {
                    "content": content,
                    "body": content,  # Some forums use 'body'
                    "text": content,  # Some forums use 'text'
                }
                
                # Add metadata fields
                if metadata:
                    post_data.update(metadata)
                
                # Post to forum
                post_url = f"{self.base_url}{self.post_endpoint}"
                
                async with session.post(
                    post_url,
                    headers=headers,
                    json=post_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status in [200, 201]:
                        try:
                            result = await resp.json()
                            
                            # Try to extract post ID (common field names)
                            post_id = (
                                result.get("id") or
                                result.get("post_id") or
                                result.get("thread_id") or
                                str(result.get("data", {}).get("id", "unknown"))
                            )
                            
                            # Try to build URL
                            post_url = (
                                result.get("url") or
                                result.get("permalink") or
                                f"{self.base_url}/posts/{post_id}"
                            )
                            
                            return {
                                "success": True,
                                "post_id": str(post_id),
                                "url": post_url,
                                "platform": self.platform_name,
                                "raw_response": result
                            }
                        except:
                            # If response isn't JSON, return basic success
                            return {
                                "success": True,
                                "post_id": "unknown",
                                "url": post_url,
                                "platform": self.platform_name
                            }
                    else:
                        error_text = await resp.text()
                        raise PlatformError(
                            self.platform_name,
                            f"Failed to post (HTTP {resp.status}): {error_text}"
                        )
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a generic forum post"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = self._get_headers()
                
                # Build analytics URL
                analytics_url = f"{self.base_url}{self.analytics_endpoint.replace('{id}', post_id)}"
                
                async with session.get(
                    analytics_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        # Try to extract common metrics
                        likes = (
                            result.get("likes") or
                            result.get("upvotes") or
                            result.get("score") or
                            result.get("reactions") or
                            0
                        )
                        
                        comments = (
                            result.get("comments") or
                            result.get("replies") or
                            result.get("comment_count") or
                            0
                        )
                        
                        views = (
                            result.get("views") or
                            result.get("view_count") or
                            result.get("impressions") or
                            0
                        )
                        
                        shares = result.get("shares", 0)
                        
                        return {
                            "likes": likes,
                            "comments": comments,
                            "shares": shares,
                            "views": views,
                            "engagement_rate": self._calculate_engagement(likes, comments, views),
                            "platform_specific_metrics": result
                        }
                    else:
                        raise PlatformError(self.platform_name, "Failed to fetch analytics")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    def _calculate_engagement(self, likes: int, comments: int, views: int) -> float:
        """Calculate engagement for generic forum"""
        if views == 0:
            return 0.0
        total_engagement = likes + comments
        return (total_engagement / views) * 100

