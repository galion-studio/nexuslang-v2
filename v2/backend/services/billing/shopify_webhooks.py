"""
Shopify Webhook Handlers
Processes webhook events from Shopify.
"""

import hmac
import hashlib
from typing import Dict, Any
from fastapi import Request, HTTPException

from ...core.config import settings


def verify_webhook(request: Request, body: bytes) -> bool:
    """
    Verify Shopify webhook signature.
    """
    if not settings.SHOPIFY_WEBHOOK_SECRET:
        # In development, allow unverified webhooks
        return settings.DEBUG
    
    hmac_header = request.headers.get("X-Shopify-Hmac-SHA256")
    if not hmac_header:
        return False
    
    # Calculate HMAC
    calculated_hmac = hmac.new(
        settings.SHOPIFY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(calculated_hmac, hmac_header)


async def handle_subscription_created(data: Dict[str, Any], db):
    """
    Handle subscription creation webhook.
    """
    from ...models.billing import Subscription
    from sqlalchemy import select
    
    shopify_id = data.get("id")
    customer_id = data.get("customer_id")
    status = data.get("status")
    
    # Find user by Shopify customer ID
    # (Assuming we store this in user metadata)
    # TODO: Implement user lookup
    
    # Create subscription record
    subscription = Subscription(
        user_id="user_id_here",  # TODO: Get from customer_id
        tier="pro",  # TODO: Determine from plan
        status="active" if status == "active" else "pending",
        shopify_subscription_id=str(shopify_id)
    )
    db.add(subscription)
    await db.commit()
    
    return {"status": "processed"}


async def handle_subscription_updated(data: Dict[str, Any], db):
    """
    Handle subscription update webhook.
    """
    from ...models.billing import Subscription
    from sqlalchemy import select, update
    
    shopify_id = data.get("id")
    status = data.get("status")
    
    # Update subscription
    stmt = (
        update(Subscription)
        .where(Subscription.shopify_subscription_id == str(shopify_id))
        .values(
            status="active" if status == "active" else status,
            updated_at=datetime.utcnow()
        )
    )
    await db.execute(stmt)
    await db.commit()
    
    return {"status": "processed"}


async def handle_subscription_cancelled(data: Dict[str, Any], db):
    """
    Handle subscription cancellation webhook.
    """
    from ...models.billing import Subscription
    from sqlalchemy import select, update
    
    shopify_id = data.get("id")
    
    # Update subscription status
    stmt = (
        update(Subscription)
        .where(Subscription.shopify_subscription_id == str(shopify_id))
        .values(
            status="cancelled",
            cancel_at=datetime.utcnow()
        )
    )
    await db.execute(stmt)
    await db.commit()
    
    # TODO: Send cancellation email
    
    return {"status": "processed"}


async def handle_payment_received(data: Dict[str, Any], db):
    """
    Handle payment received webhook.
    """
    from ...models.billing import Transaction
    
    amount = float(data.get("amount", 0))
    customer_id = data.get("customer_id")
    
    # TODO: Get user_id from customer_id
    
    # Record transaction
    transaction = Transaction(
        user_id="user_id_here",  # TODO: Get from customer_id
        amount=int(amount * 100),  # Convert to credits
        type="purchase",
        description="Payment received from Shopify"
    )
    db.add(transaction)
    await db.commit()
    
    return {"status": "processed"}


# Webhook handler map
WEBHOOK_HANDLERS = {
    "subscription/created": handle_subscription_created,
    "subscription/updated": handle_subscription_updated,
    "subscription/cancelled": handle_subscription_cancelled,
    "payment/received": handle_payment_received,
}


async def process_webhook(topic: str, data: Dict[str, Any], db) -> Dict[str, Any]:
    """
    Process a webhook based on its topic.
    """
    handler = WEBHOOK_HANDLERS.get(topic)
    
    if not handler:
        return {"status": "ignored", "reason": f"No handler for topic: {topic}"}
    
    try:
        result = await handler(data, db)
        return result
    except Exception as e:
        print(f"Error processing webhook {topic}: {e}")
        return {"status": "error", "error": str(e)}

