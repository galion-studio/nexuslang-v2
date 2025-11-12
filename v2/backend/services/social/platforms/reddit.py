"""
Reddit Platform Connector
Uses PRAW (Python Reddit API Wrapper) or direct API calls
"""

from typing import Dict, Optional, List
import asyncio
import aiohttp
from datetime import datetime

from . import PlatformConnector, PlatformError, RateLimitError, AuthenticationError


class RedditConnector(PlatformConnector):
    """
    Reddit connector using OAuth2
    Supports posting to subreddits, tracking karma, comments
    """
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.platform_name = "reddit"
        self.base_url = "https://oauth.reddit.com"
        self.access_token = credentials.get("access_token")
        self.refresh_token = credentials.get("refresh_token")
        self.client_id = credentials.get("client_id")
        self.client_secret = credentials.get("client_secret")
        self.username = credentials.get("username")
    
    async def authenticate(self) -> bool:
        """
        Authenticate with Reddit OAuth2
        """
        try:
            # If we have a refresh token, use it to get a new access token
            if self.refresh_token:
                await self._refresh_access_token()
            
            # Verify the access token works
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "User-Agent": "GalionStudio-ContentManager/1.0"
                }
                async with session.get(f"{self.base_url}/api/v1/me", headers=headers) as resp:
                    if resp.status == 200:
                        return True
                    elif resp.status == 401:
                        raise AuthenticationError(self.platform_name, "Invalid access token")
                    else:
                        return False
        except Exception as e:
            raise AuthenticationError(self.platform_name, str(e))
    
    async def _refresh_access_token(self):
        """
        Refresh the OAuth2 access token
        """
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
            headers = {"User-Agent": "GalionStudio-ContentManager/1.0"}
            
            async with session.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    self.access_token = result.get("access_token")
                else:
                    raise AuthenticationError(self.platform_name, "Failed to refresh token")
    
    async def post_content(
        self,
        content: str,
        media_urls: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Post content to Reddit (text post or link)
        
        metadata should include:
        - subreddit: Name of subreddit (required)
        - title: Post title (required)
        - kind: 'self' for text post or 'link' for link post
        - flair_id: Optional flair ID
        """
        if not metadata or not metadata.get("subreddit") or not metadata.get("title"):
            raise PlatformError(self.platform_name, "Subreddit and title are required")
        
        subreddit = metadata.get("subreddit")
        title = metadata.get("title")
        kind = metadata.get("kind", "self")  # 'self' for text post, 'link' for link
        flair_id = metadata.get("flair_id")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "User-Agent": "GalionStudio-ContentManager/1.0"
                }
                
                # Prepare submission data
                data = {
                    "sr": subreddit,
                    "title": title,
                    "kind": kind,
                    "api_type": "json"
                }
                
                if kind == "self":
                    data["text"] = content
                elif kind == "link" and media_urls:
                    data["url"] = media_urls[0]
                
                if flair_id:
                    data["flair_id"] = flair_id
                
                # Submit post
                async with session.post(
                    f"{self.base_url}/api/submit",
                    headers=headers,
                    data=data
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        # Check for errors
                        if result.get("json", {}).get("errors"):
                            errors = result["json"]["errors"]
                            raise PlatformError(self.platform_name, f"Post failed: {errors}")
                        
                        # Extract post data
                        post_data = result.get("json", {}).get("data", {})
                        post_id = post_data.get("id")
                        post_url = post_data.get("url")
                        
                        return {
                            "success": True,
                            "post_id": post_id,
                            "url": post_url,
                            "platform": self.platform_name
                        }
                    elif resp.status == 429:
                        raise RateLimitError(self.platform_name)
                    else:
                        error_text = await resp.text()
                        raise PlatformError(self.platform_name, f"Failed to post: {error_text}")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def get_post_analytics(self, post_id: str) -> Dict:
        """
        Get analytics for a Reddit post
        Returns karma (upvotes), comments, awards
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "User-Agent": "GalionStudio-ContentManager/1.0"
                }
                
                # Get post info
                async with session.get(
                    f"{self.base_url}/api/info",
                    headers=headers,
                    params={"id": f"t3_{post_id}"}  # t3_ prefix for submissions
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        if result.get("data", {}).get("children"):
                            post = result["data"]["children"][0]["data"]
                            
                            return {
                                "likes": post.get("ups", 0),  # Upvotes
                                "comments": post.get("num_comments", 0),
                                "shares": 0,  # Reddit doesn't track shares directly
                                "views": 0,  # Reddit doesn't provide view counts via API
                                "engagement_rate": self._calculate_engagement(
                                    post.get("ups", 0),
                                    post.get("num_comments", 0)
                                ),
                                "platform_specific_metrics": {
                                    "karma": post.get("score", 0),
                                    "upvote_ratio": post.get("upvote_ratio", 0),
                                    "awards": post.get("total_awards_received", 0),
                                    "crossposts": post.get("num_crossposts", 0)
                                }
                            }
                        else:
                            raise PlatformError(self.platform_name, "Post not found")
                    else:
                        raise PlatformError(self.platform_name, "Failed to fetch analytics")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a Reddit post
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "User-Agent": "GalionStudio-ContentManager/1.0"
                }
                
                data = {"id": f"t3_{post_id}"}
                
                async with session.post(
                    f"{self.base_url}/api/del",
                    headers=headers,
                    data=data
                ) as resp:
                    return resp.status == 200
        
        except aiohttp.ClientError:
            return False
    
    async def validate_credentials(self) -> bool:
        """
        Validate Reddit OAuth credentials
        """
        try:
            return await self.authenticate()
        except:
            return False
    
    def _calculate_engagement(self, upvotes: int, comments: int) -> float:
        """
        Calculate engagement rate for Reddit
        (upvotes + comments) as a percentage
        """
        total_engagement = upvotes + comments
        # Normalize to a percentage (simple heuristic)
        # Assume 1000 is "good" engagement for baseline
        return min((total_engagement / 1000.0) * 100, 100.0)

