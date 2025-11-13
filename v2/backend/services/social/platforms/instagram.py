"""
Instagram Platform Connector
Uses Instagram Graph API
"""

from typing import Dict, Optional, List
import aiohttp
from datetime import datetime

from . import PlatformConnector, PlatformError, RateLimitError, AuthenticationError


class InstagramConnector(PlatformConnector):
    """
    Instagram connector using Graph API
    Supports posts, stories, reels (requires Business/Creator account)
    """
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.platform_name = "instagram"
        self.base_url = "https://graph.facebook.com/v18.0"
        self.access_token = credentials.get("access_token")
        self.instagram_account_id = credentials.get("instagram_account_id")
    
    async def authenticate(self) -> bool:
        """Authenticate with Instagram Graph API"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "fields": "id,username",
                    "access_token": self.access_token
                }
                async with session.get(
                    f"{self.base_url}/{self.instagram_account_id}",
                    params=params
                ) as resp:
                    return resp.status == 200
        except Exception as e:
            raise AuthenticationError(self.platform_name, str(e))
    
    async def post_content(
        self,
        content: str,
        media_urls: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Post content to Instagram
        Instagram requires at least one image or video
        Caption limit: 2,200 characters
        """
        if not media_urls or len(media_urls) == 0:
            raise PlatformError(self.platform_name, "Instagram requires at least one media item")
        
        content = self.format_content(content, max_length=2200)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Step 1: Create media container
                container_params = {
                    "image_url": media_urls[0],  # Use first image
                    "caption": content,
                    "access_token": self.access_token
                }
                
                # Add location if provided
                if metadata and metadata.get("location_id"):
                    container_params["location_id"] = metadata["location_id"]
                
                async with session.post(
                    f"{self.base_url}/{self.instagram_account_id}/media",
                    data=container_params
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        container_id = result.get("id")
                    elif resp.status == 429:
                        raise RateLimitError(self.platform_name)
                    else:
                        error_data = await resp.json()
                        raise PlatformError(self.platform_name, f"Failed to create container: {error_data}")
                
                # Step 2: Publish the media container
                publish_params = {
                    "creation_id": container_id,
                    "access_token": self.access_token
                }
                
                async with session.post(
                    f"{self.base_url}/{self.instagram_account_id}/media_publish",
                    data=publish_params
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        post_id = result.get("id")
                        
                        return {
                            "success": True,
                            "post_id": post_id,
                            "url": f"https://www.instagram.com/p/{post_id}/",
                            "platform": self.platform_name
                        }
                    else:
                        error_data = await resp.json()
                        raise PlatformError(self.platform_name, f"Failed to publish: {error_data}")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for an Instagram post"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "fields": "like_count,comments_count,media_type,permalink",
                    "access_token": self.access_token
                }
                
                async with session.get(
                    f"{self.base_url}/{post_id}/insights",
                    params=params
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        # Get basic metrics
                        like_count = result.get("like_count", 0)
                        comments_count = result.get("comments_count", 0)
                        
                        # Get insights (reach, impressions, engagement)
                        insights = result.get("data", [])
                        reach = 0
                        impressions = 0
                        engagement = 0
                        
                        for insight in insights:
                            if insight.get("name") == "reach":
                                reach = insight.get("values", [{}])[0].get("value", 0)
                            elif insight.get("name") == "impressions":
                                impressions = insight.get("values", [{}])[0].get("value", 0)
                            elif insight.get("name") == "engagement":
                                engagement = insight.get("values", [{}])[0].get("value", 0)
                        
                        return {
                            "likes": like_count,
                            "comments": comments_count,
                            "shares": 0,  # Instagram doesn't expose share count
                            "views": impressions,
                            "reach": reach,
                            "engagement_rate": (engagement / impressions * 100) if impressions > 0 else 0.0,
                            "platform_specific_metrics": {
                                "reach": reach,
                                "impressions": impressions,
                                "saves": 0  # Requires additional API call
                            }
                        }
                    else:
                        raise PlatformError(self.platform_name, "Failed to fetch analytics")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete an Instagram post"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {"access_token": self.access_token}
                
                async with session.delete(
                    f"{self.base_url}/{post_id}",
                    params=params
                ) as resp:
                    return resp.status == 200
        
        except aiohttp.ClientError:
            return False
    
    async def validate_credentials(self) -> bool:
        """Validate Instagram credentials"""
        try:
            return await self.authenticate()
        except:
            return False

