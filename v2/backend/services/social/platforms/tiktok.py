"""
TikTok Platform Connector
Uses TikTok Content Posting API
"""

from typing import Dict, Optional, List
import aiohttp
from datetime import datetime

from . import PlatformConnector, PlatformError, RateLimitError, AuthenticationError


class TikTokConnector(PlatformConnector):
    """
    TikTok connector using Content Posting API
    Supports video uploads with captions
    Requires TikTok for Developers account and app approval
    """
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.platform_name = "tiktok"
        self.base_url = "https://open.tiktokapis.com/v2"
        self.access_token = credentials.get("access_token")
        self.open_id = credentials.get("open_id")  # TikTok user's open ID
    
    async def authenticate(self) -> bool:
        """Authenticate with TikTok API"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                # Query user info to verify auth
                async with session.get(
                    f"{self.base_url}/user/info/",
                    headers=headers,
                    params={"fields": "open_id,display_name"}
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
        Post video content to TikTok
        TikTok requires video content
        Caption limit: 2,200 characters
        """
        if not media_urls or len(media_urls) == 0:
            raise PlatformError(self.platform_name, "TikTok requires video content")
        
        content = self.format_content(content, max_length=2200)
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                # Prepare post data
                post_data = {
                    "post_info": {
                        "title": content,
                        "privacy_level": metadata.get("privacy_level", "PUBLIC_TO_EVERYONE") if metadata else "PUBLIC_TO_EVERYONE",
                        "disable_duet": metadata.get("disable_duet", False) if metadata else False,
                        "disable_comment": metadata.get("disable_comment", False) if metadata else False,
                        "disable_stitch": metadata.get("disable_stitch", False) if metadata else False,
                        "video_cover_timestamp_ms": metadata.get("cover_timestamp", 1000) if metadata else 1000
                    },
                    "source_info": {
                        "source": "FILE_UPLOAD",
                        "video_url": media_urls[0]
                    }
                }
                
                # Add hashtags if provided
                if metadata and metadata.get("hashtags"):
                    post_data["post_info"]["hashtags"] = metadata["hashtags"]
                
                # Create post
                async with session.post(
                    f"{self.base_url}/post/publish/video/init/",
                    headers=headers,
                    json=post_data
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        if result.get("data"):
                            publish_id = result["data"].get("publish_id")
                            
                            return {
                                "success": True,
                                "post_id": publish_id,
                                "url": f"https://www.tiktok.com/@{self.open_id}/video/{publish_id}",
                                "platform": self.platform_name,
                                "status": "processing"  # TikTok processes videos asynchronously
                            }
                        else:
                            error = result.get("error", {})
                            raise PlatformError(self.platform_name, f"Failed to post: {error}")
                    elif resp.status == 429:
                        raise RateLimitError(self.platform_name)
                    else:
                        error_data = await resp.json()
                        raise PlatformError(self.platform_name, f"Failed to post: {error_data}")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def get_post_analytics(self, post_id: str) -> Dict:
        """
        Get analytics for a TikTok video
        Note: Analytics may take time to populate
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                # Get video info
                data = {
                    "filters": {
                        "video_ids": [post_id]
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/video/query/",
                    headers=headers,
                    json=data
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        if result.get("data", {}).get("videos"):
                            video = result["data"]["videos"][0]
                            
                            likes = video.get("like_count", 0)
                            comments = video.get("comment_count", 0)
                            shares = video.get("share_count", 0)
                            views = video.get("view_count", 0)
                            
                            return {
                                "likes": likes,
                                "comments": comments,
                                "shares": shares,
                                "views": views,
                                "engagement_rate": self._calculate_engagement(likes, comments, shares, views),
                                "platform_specific_metrics": {
                                    "play_count": views,
                                    "duration": video.get("duration", 0)
                                }
                            }
                        else:
                            raise PlatformError(self.platform_name, "Video not found")
                    else:
                        raise PlatformError(self.platform_name, "Failed to fetch analytics")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a TikTok video
        Note: Not all TikTok API versions support deletion
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                data = {"video_id": post_id}
                
                async with session.post(
                    f"{self.base_url}/post/publish/video/delete/",
                    headers=headers,
                    json=data
                ) as resp:
                    return resp.status == 200
        
        except aiohttp.ClientError:
            return False
    
    async def validate_credentials(self) -> bool:
        """Validate TikTok credentials"""
        try:
            return await self.authenticate()
        except:
            return False
    
    def _calculate_engagement(self, likes: int, comments: int, shares: int, views: int) -> float:
        """Calculate engagement rate for TikTok"""
        if views == 0:
            return 0.0
        total_engagement = likes + comments + shares
        return (total_engagement / views) * 100

