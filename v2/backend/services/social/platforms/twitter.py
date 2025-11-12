"""
Twitter/X Platform Connector
Uses Twitter API v2
"""

from typing import Dict, Optional, List
import aiohttp
from datetime import datetime

from . import PlatformConnector, PlatformError, RateLimitError, AuthenticationError


class TwitterConnector(PlatformConnector):
    """
    Twitter/X connector using OAuth 2.0 and API v2
    Supports tweets, threads, media uploads
    """
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.platform_name = "twitter"
        self.base_url = "https://api.twitter.com/2"
        self.upload_url = "https://upload.twitter.com/1.1"
        self.access_token = credentials.get("access_token")
        self.bearer_token = credentials.get("bearer_token")
        self.api_key = credentials.get("api_key")
        self.api_secret = credentials.get("api_secret")
    
    async def authenticate(self) -> bool:
        """Authenticate with Twitter API v2"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.bearer_token}",
                    "User-Agent": "GalionStudio-ContentManager/1.0"
                }
                async with session.get(f"{self.base_url}/users/me", headers=headers) as resp:
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
        Post a tweet or thread
        Twitter character limit: 280 characters per tweet
        """
        content = self.format_content(content, max_length=280)
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.bearer_token}",
                    "Content-Type": "application/json"
                }
                
                # Prepare tweet data
                tweet_data = {"text": content}
                
                # Add media if provided (would need to upload first)
                if media_urls and metadata and metadata.get("media_ids"):
                    tweet_data["media"] = {"media_ids": metadata["media_ids"]}
                
                # Add poll if provided
                if metadata and metadata.get("poll"):
                    tweet_data["poll"] = metadata["poll"]
                
                # Post tweet
                async with session.post(
                    f"{self.base_url}/tweets",
                    headers=headers,
                    json=tweet_data
                ) as resp:
                    if resp.status == 201:
                        result = await resp.json()
                        tweet_id = result.get("data", {}).get("id")
                        
                        return {
                            "success": True,
                            "post_id": tweet_id,
                            "url": f"https://twitter.com/user/status/{tweet_id}",
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
        """Get analytics for a tweet"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.bearer_token}"
                }
                
                # Get tweet with metrics
                params = {
                    "tweet.fields": "public_metrics,created_at"
                }
                
                async with session.get(
                    f"{self.base_url}/tweets/{post_id}",
                    headers=headers,
                    params=params
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        metrics = result.get("data", {}).get("public_metrics", {})
                        
                        return {
                            "likes": metrics.get("like_count", 0),
                            "comments": metrics.get("reply_count", 0),
                            "shares": metrics.get("retweet_count", 0),
                            "views": metrics.get("impression_count", 0),
                            "engagement_rate": self._calculate_engagement(metrics),
                            "platform_specific_metrics": {
                                "retweets": metrics.get("retweet_count", 0),
                                "quote_tweets": metrics.get("quote_count", 0),
                                "bookmarks": metrics.get("bookmark_count", 0)
                            }
                        }
                    else:
                        raise PlatformError(self.platform_name, "Failed to fetch analytics")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete a tweet"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.bearer_token}"
                }
                
                async with session.delete(
                    f"{self.base_url}/tweets/{post_id}",
                    headers=headers
                ) as resp:
                    return resp.status == 200
        
        except aiohttp.ClientError:
            return False
    
    async def validate_credentials(self) -> bool:
        """Validate Twitter credentials"""
        try:
            return await self.authenticate()
        except:
            return False
    
    def _calculate_engagement(self, metrics: Dict) -> float:
        """Calculate engagement rate for Twitter"""
        likes = metrics.get("like_count", 0)
        replies = metrics.get("reply_count", 0)
        retweets = metrics.get("retweet_count", 0)
        impressions = metrics.get("impression_count", 1)  # Avoid division by zero
        
        total_engagement = likes + replies + retweets
        return (total_engagement / impressions) * 100 if impressions > 0 else 0.0

