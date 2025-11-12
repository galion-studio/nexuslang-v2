"""
LinkedIn Platform Connector
Uses LinkedIn API v2
"""

from typing import Dict, Optional, List
import aiohttp
from datetime import datetime

from . import PlatformConnector, PlatformError, RateLimitError, AuthenticationError


class LinkedInConnector(PlatformConnector):
    """
    LinkedIn connector using OAuth 2.0 and API v2
    Supports posting to personal profiles and company pages
    """
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.platform_name = "linkedin"
        self.base_url = "https://api.linkedin.com/v2"
        self.access_token = credentials.get("access_token")
        self.person_urn = credentials.get("person_urn")  # urn:li:person:XXXXX
        self.organization_urn = credentials.get("organization_urn")  # Optional, for company pages
    
    async def authenticate(self) -> bool:
        """Authenticate with LinkedIn API"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "X-Restli-Protocol-Version": "2.0.0"
                }
                async with session.get(f"{self.base_url}/me", headers=headers) as resp:
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
        Post content to LinkedIn
        Character limit: 3,000 for posts, 1,300 for comments
        """
        content = self.format_content(content, max_length=3000)
        
        # Determine author (person or organization)
        author_urn = self.organization_urn if (metadata and metadata.get("use_organization")) else self.person_urn
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0"
                }
                
                # Prepare share data
                share_data = {
                    "author": author_urn,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": content
                            },
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
                
                # Add media if provided (requires separate upload)
                if media_urls and metadata and metadata.get("media_urn"):
                    share_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                    share_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                        {
                            "status": "READY",
                            "media": metadata["media_urn"]
                        }
                    ]
                
                # Add article if link provided
                if metadata and metadata.get("link"):
                    share_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
                    share_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                        {
                            "status": "READY",
                            "originalUrl": metadata["link"]
                        }
                    ]
                
                # Post to LinkedIn
                async with session.post(
                    f"{self.base_url}/ugcPosts",
                    headers=headers,
                    json=share_data
                ) as resp:
                    if resp.status == 201:
                        result = await resp.json()
                        post_id = result.get("id")
                        
                        return {
                            "success": True,
                            "post_id": post_id,
                            "url": f"https://www.linkedin.com/feed/update/{post_id}/",
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
        """
        Get analytics for a LinkedIn post
        Note: Analytics require specific permissions and may have delays
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "X-Restli-Protocol-Version": "2.0.0"
                }
                
                # Get social actions (likes, comments, shares)
                async with session.get(
                    f"{self.base_url}/socialActions/{post_id}",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        likes = result.get("likesSummary", {}).get("totalLikes", 0)
                        comments = result.get("commentsSummary", {}).get("totalComments", 0)
                        shares = result.get("sharesSummary", {}).get("totalShares", 0)
                        
                        # Note: Impressions and reach require Organization Access
                        # and separate analytics API calls
                        
                        return {
                            "likes": likes,
                            "comments": comments,
                            "shares": shares,
                            "views": 0,  # Requires analytics API
                            "engagement_rate": self._calculate_engagement(likes, comments, shares),
                            "platform_specific_metrics": {
                                "likes": likes,
                                "comments": comments,
                                "shares": shares
                            }
                        }
                    else:
                        raise PlatformError(self.platform_name, "Failed to fetch analytics")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete a LinkedIn post"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "X-Restli-Protocol-Version": "2.0.0"
                }
                
                async with session.delete(
                    f"{self.base_url}/ugcPosts/{post_id}",
                    headers=headers
                ) as resp:
                    return resp.status == 204
        
        except aiohttp.ClientError:
            return False
    
    async def validate_credentials(self) -> bool:
        """Validate LinkedIn credentials"""
        try:
            return await self.authenticate()
        except:
            return False
    
    def _calculate_engagement(self, likes: int, comments: int, shares: int) -> float:
        """Calculate engagement rate for LinkedIn"""
        total_engagement = likes + comments + shares
        # Normalize (assume 100 is good engagement for baseline)
        return min((total_engagement / 100.0) * 100, 100.0)

