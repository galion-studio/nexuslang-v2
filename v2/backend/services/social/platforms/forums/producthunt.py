"""
ProductHunt Forum Connector
Uses ProductHunt API v2 (GraphQL)
"""

from typing import Dict, Optional, List
import aiohttp
from datetime import datetime

from . import ForumConnector
from .. import PlatformError, RateLimitError, AuthenticationError


class ProductHuntConnector(ForumConnector):
    """
    ProductHunt connector using GraphQL API
    Supports launching products and commenting
    """
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.platform_name = "producthunt"
        self.base_url = "https://api.producthunt.com/v2/api/graphql"
        self.access_token = credentials.get("access_token")
        self.api_key = credentials.get("api_key")
    
    async def authenticate(self) -> bool:
        """Authenticate with ProductHunt API"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                # Simple query to test authentication
                query = """
                query {
                    viewer {
                        id
                        name
                    }
                }
                """
                
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json={"query": query}
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return "errors" not in result
                    else:
                        return False
        except Exception as e:
            raise AuthenticationError(self.platform_name, str(e))
    
    async def post_content(
        self,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Post to ProductHunt (create product or comment)
        
        metadata should include:
        - product_id: For comments
        - name: For new product launch
        - tagline: For new product launch
        - url: Product website URL
        """
        if not metadata:
            raise PlatformError(self.platform_name, "Metadata is required for ProductHunt posts")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                # Check if it's a comment or product launch
                if metadata.get("product_id"):
                    # Create comment
                    query = """
                    mutation($productId: ID!, $body: String!) {
                        createComment(input: {productId: $productId, body: $body}) {
                            comment {
                                id
                                url
                            }
                        }
                    }
                    """
                    variables = {
                        "productId": metadata["product_id"],
                        "body": content
                    }
                else:
                    # Launch product (simplified - actual launch requires more fields)
                    query = """
                    mutation($name: String!, $tagline: String!, $url: String!, $description: String!) {
                        createPost(input: {name: $name, tagline: $tagline, url: $url, description: $description}) {
                            post {
                                id
                                url
                            }
                        }
                    }
                    """
                    variables = {
                        "name": metadata.get("name", "Product Name"),
                        "tagline": metadata.get("tagline", "Short tagline"),
                        "url": metadata.get("url", "https://example.com"),
                        "description": content
                    }
                
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json={"query": query, "variables": variables}
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        if "errors" in result:
                            raise PlatformError(self.platform_name, f"GraphQL errors: {result['errors']}")
                        
                        # Extract post/comment data
                        data = result.get("data", {})
                        post_data = data.get("createPost", {}).get("post") or data.get("createComment", {}).get("comment")
                        
                        if post_data:
                            return {
                                "success": True,
                                "post_id": post_data.get("id"),
                                "url": post_data.get("url"),
                                "platform": self.platform_name
                            }
                        else:
                            raise PlatformError(self.platform_name, "Failed to create post")
                    elif resp.status == 429:
                        raise RateLimitError(self.platform_name)
                    else:
                        error_data = await resp.json()
                        raise PlatformError(self.platform_name, f"Failed to post: {error_data}")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    async def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a ProductHunt post"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                query = """
                query($id: ID!) {
                    post(id: $id) {
                        votesCount
                        commentsCount
                        reviewsCount
                    }
                }
                """
                
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json={"query": query, "variables": {"id": post_id}}
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        if "errors" not in result:
                            post = result.get("data", {}).get("post", {})
                            
                            votes = post.get("votesCount", 0)
                            comments = post.get("commentsCount", 0)
                            reviews = post.get("reviewsCount", 0)
                            
                            return {
                                "likes": votes,  # Upvotes on ProductHunt
                                "comments": comments,
                                "shares": 0,
                                "views": 0,  # PH doesn't expose views
                                "engagement_rate": self._calculate_engagement(votes, comments, reviews),
                                "platform_specific_metrics": {
                                    "votes": votes,
                                    "reviews": reviews
                                }
                            }
                        else:
                            raise PlatformError(self.platform_name, "Failed to fetch analytics")
                    else:
                        raise PlatformError(self.platform_name, "Failed to fetch analytics")
        
        except aiohttp.ClientError as e:
            raise PlatformError(self.platform_name, f"Network error: {str(e)}")
    
    def _calculate_engagement(self, votes: int, comments: int, reviews: int) -> float:
        """Calculate engagement for ProductHunt"""
        total_engagement = votes + comments + reviews
        # Normalize (200 is good for PH)
        return min((total_engagement / 200.0) * 100, 100.0)

