"""
Facebook Platform Connector
Uses Facebook Graph API
"""

from typing import Dict, Optional, List
import aiohttp
from datetime import datetime

from . import PlatformConnector, PlatformError, RateLimitError, AuthenticationError


class FacebookConnector(PlatformConnector):
    """
    Facebook connector using Graph API
    Supports posting to pages, groups, and timelines
    """
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.platform_name = "facebook"
        self.base_url = "https://graph.facebook.com/v18.0"
        self.access_token = credentials.get("access_token")
        self.page_id = credentials.get("page_id")  # Optional, for page posting
    
    async def authenticate(self) -> bool:
        """Authenticate with Facebook Graph API"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {"access_token": self.access_token}
                async with session.get(f"{self.base_url}/me", params=params) as resp:
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
        Post content to Facebook
        Can post to page, group, or user timeline
        """
        # Determine target (page, group, or user)
        target_id = self.page_id or "me"
        if metadata and metadata.get("group_id"):
            target_id = metadata["group_id"]
        elif metadata and metadata.get("page_id"):
            target_id = metadata["page_id"]
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "message": content,
                    "access_token": self.access_token
                }
                
                # Add link if provided
                if metadata and metadata.get("link"):
                    params["link"] = metadata["link"]
                
                # Determine endpoint based on media
                if media_urls and len(media_urls) > 0:
                    # Post with photo
                    endpoint = f"{self.base_url}/{target_id}/photos"
                    params["url"] = media_urls[0]
                else:
                    # Text post
                    endpoint = f"{self.base_url}/{target_id}/feed"
                
                async with session.post(endpoint, data=params) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        post_id = result.get("id")
                        
                        return {
                            "success": True,
                            "post_id": post_id,
                            "url": f"https://www.facebook.com/{post_id}",
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
        """Get analytics for a Facebook post"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "fields": "reactions.summary(true),comments.summary(true),shares,insights",
                    "access_token": self.access_token
                }
                
                async with session.get(
                    f"{self.base_url}/{post_id}",
                    params=params
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        reactions = result.get("reactions", {}).get("summary", {}).get("total_count", 0)
                        comments = result.get("comments", {}).get("summary", {}).get("total_count", 0)
                        shares = result.get("shares", {}).get("count", 0)
                        
                        # Get insights if available (page posts only)
                        reach = 0
                        impressions = 0
                        if "insights" in result:
                            for insight in result["insights"].get("data", []):
                                if insight.get("name") == "post_impressions":
                                    impressions = insight.get("values", [{}])[0].get("value", 0)
                                elif insight.get("name") == "post_reach":
                                    reach = insight.get("values", [{}])[0].get("value", 0)
                        
                        total_engagement = reactions + comments + shares
                        engagement_rate = (total_engagement / impressions * 100) if impressions > 0 else 0.0
                        
                        return {
                            "likes": reactions,
                            "comments": comments,
                            "shares": shares,
                            "views": impressions,
                            "reach": reach,
                            "engagement_rate": engagement_rate,
                            "platform_specific_metrics": {
                                "reactions": reactions,
                                "reach": reach,
                                "impressions": impressions
                            }
                        }
                    else:
                        raise PlatformError(self.platform_name, "Failed to fetch analytics")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete a Facebook post"""
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
        """Validate Facebook credentials"""
        try:
            return await self.authenticate()
        except:
            return False

