"""
YouTube Platform Connector
Uses YouTube Data API v3
"""

from typing import Dict, Optional, List
import aiohttp
from datetime import datetime

from . import PlatformConnector, PlatformError, RateLimitError, AuthenticationError


class YouTubeConnector(PlatformConnector):
    """
    YouTube connector using Data API v3
    Supports video uploads, community posts
    """
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.platform_name = "youtube"
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.upload_url = "https://www.googleapis.com/upload/youtube/v3"
        self.access_token = credentials.get("access_token")
        self.api_key = credentials.get("api_key")
    
    async def authenticate(self) -> bool:
        """Authenticate with YouTube API"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }
                params = {
                    "part": "snippet",
                    "mine": "true"
                }
                async with session.get(
                    f"{self.base_url}/channels",
                    headers=headers,
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
        Post content to YouTube
        For videos: Uploads video with title/description
        For community posts: Creates community post (requires channel membership)
        """
        if not metadata:
            raise PlatformError(self.platform_name, "Metadata with title is required")
        
        title = metadata.get("title", "Untitled")
        description = self.format_content(content, max_length=5000)
        
        # Check if it's a video upload or community post
        if media_urls and len(media_urls) > 0:
            return await self._upload_video(title, description, media_urls[0], metadata)
        else:
            return await self._create_community_post(content, metadata)
    
    async def _upload_video(self, title: str, description: str, video_url: str, metadata: Dict) -> Dict:
        """Upload a video to YouTube"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                # Prepare video metadata
                video_metadata = {
                    "snippet": {
                        "title": title,
                        "description": description,
                        "categoryId": metadata.get("category_id", "22"),  # Default: People & Blogs
                        "tags": metadata.get("tags", [])
                    },
                    "status": {
                        "privacyStatus": metadata.get("privacy", "public"),  # public, private, unlisted
                        "selfDeclaredMadeForKids": metadata.get("made_for_kids", False)
                    }
                }
                
                # Note: Actual video upload requires multipart/form-data and video file
                # This is a simplified version - full implementation would use resumable upload
                
                async with session.post(
                    f"{self.upload_url}/videos",
                    headers=headers,
                    params={"part": "snippet,status"},
                    json=video_metadata
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        video_id = result.get("id")
                        
                        return {
                            "success": True,
                            "post_id": video_id,
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "platform": self.platform_name
                        }
                    elif resp.status == 429:
                        raise RateLimitError(self.platform_name)
                    else:
                        error_data = await resp.json()
                        raise PlatformError(self.platform_name, f"Failed to upload: {error_data}")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def _create_community_post(self, content: str, metadata: Dict) -> Dict:
        """Create a YouTube community post"""
        # Note: Community posts API is limited and may require special access
        raise PlatformError(self.platform_name, "Community posts require special API access")
    
    async def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a YouTube video"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }
                
                # Get video statistics
                params = {
                    "part": "statistics,snippet",
                    "id": post_id
                }
                
                async with session.get(
                    f"{self.base_url}/videos",
                    headers=headers,
                    params=params
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        if result.get("items"):
                            video = result["items"][0]
                            stats = video.get("statistics", {})
                            
                            views = int(stats.get("viewCount", 0))
                            likes = int(stats.get("likeCount", 0))
                            comments = int(stats.get("commentCount", 0))
                            
                            return {
                                "likes": likes,
                                "comments": comments,
                                "shares": 0,  # YouTube doesn't track shares via API
                                "views": views,
                                "engagement_rate": self._calculate_engagement(likes, comments, views),
                                "platform_specific_metrics": {
                                    "views": views,
                                    "favorites": int(stats.get("favoriteCount", 0)),
                                    "dislikes": 0  # No longer available in API
                                }
                            }
                        else:
                            raise PlatformError(self.platform_name, "Video not found")
                    else:
                        raise PlatformError(self.platform_name, "Failed to fetch analytics")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete a YouTube video"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }
                params = {"id": post_id}
                
                async with session.delete(
                    f"{self.base_url}/videos",
                    headers=headers,
                    params=params
                ) as resp:
                    return resp.status == 204
        
        except aiohttp.ClientError:
            return False
    
    async def validate_credentials(self) -> bool:
        """Validate YouTube credentials"""
        try:
            return await self.authenticate()
        except:
            return False
    
    def _calculate_engagement(self, likes: int, comments: int, views: int) -> float:
        """Calculate engagement rate for YouTube"""
        if views == 0:
            return 0.0
        total_engagement = likes + comments
        return (total_engagement / views) * 100

