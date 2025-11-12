"""
N8n Integration Service
Handles N8n workflow triggers and callbacks
"""

from typing import Dict, Optional
import aiohttp
import json
from datetime import datetime


async def trigger_webhook(
    webhook_url: str,
    payload: Dict,
    method: str = "POST"
) -> bool:
    """
    Trigger an N8n webhook
    
    Args:
        webhook_url: N8n webhook URL
        payload: Data to send
        method: HTTP method (POST or GET)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json"
            }
            
            if method.upper() == "POST":
                async with session.post(
                    webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    return resp.status in [200, 201, 202]
            elif method.upper() == "GET":
                async with session.get(
                    webhook_url,
                    params=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    return resp.status == 200
            else:
                return False
    
    except Exception as e:
        print(f"N8n webhook trigger error: {e}")
        return False


class N8nWorkflows:
    """
    Pre-defined N8n workflow templates and triggers
    """
    
    @staticmethod
    async def trigger_cross_platform_post(
        webhook_url: str,
        content: str,
        platforms: list,
        brand: str
    ) -> Dict:
        """
        Trigger N8n workflow for cross-platform posting
        """
        payload = {
            "event": "cross_platform_post",
            "content": content,
            "platforms": platforms,
            "brand": brand,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        success = await trigger_webhook(webhook_url, payload)
        
        return {
            "success": success,
            "workflow": "cross_platform_post",
            "platforms": platforms
        }
    
    @staticmethod
    async def trigger_analytics_sync(
        webhook_url: str,
        post_ids: list
    ) -> Dict:
        """
        Trigger N8n workflow for analytics synchronization
        """
        payload = {
            "event": "analytics_sync",
            "post_ids": post_ids,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        success = await trigger_webhook(webhook_url, payload)
        
        return {
            "success": success,
            "workflow": "analytics_sync",
            "post_count": len(post_ids)
        }
    
    @staticmethod
    async def trigger_content_variations(
        webhook_url: str,
        base_content: str,
        target_platforms: list
    ) -> Dict:
        """
        Trigger N8n workflow to generate platform-specific content variations
        """
        payload = {
            "event": "generate_variations",
            "base_content": base_content,
            "target_platforms": target_platforms,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        success = await trigger_webhook(webhook_url, payload)
        
        return {
            "success": success,
            "workflow": "content_variations",
            "platforms": target_platforms
        }
    
    @staticmethod
    async def trigger_engagement_alert(
        webhook_url: str,
        post_id: str,
        engagement_data: Dict
    ) -> Dict:
        """
        Trigger N8n workflow when a post gets high engagement
        """
        payload = {
            "event": "high_engagement_alert",
            "post_id": post_id,
            "engagement_data": engagement_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        success = await trigger_webhook(webhook_url, payload)
        
        return {
            "success": success,
            "workflow": "engagement_alert",
            "post_id": post_id
        }

