"""
Shopify Payment Integration
Handles subscriptions, payments, and credit management.
"""

from typing import Dict, Any, Optional
import httpx
from datetime import datetime, timedelta

from ...core.config import settings


class ShopifyClient:
    """
    Client for Shopify Admin API.
    Manages subscriptions, payments, and customers.
    """
    
    def __init__(self):
        self.api_url = f"https://{settings.SHOPIFY_STORE_URL}/admin/api/2024-01"
        self.access_token = settings.SHOPIFY_ACCESS_TOKEN
        self.api_key = settings.SHOPIFY_API_KEY
        self.api_secret = settings.SHOPIFY_API_SECRET
        
    async def create_customer(self, email: str, name: str) -> Dict[str, Any]:
        """
        Create a customer in Shopify.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/customers.json",
                headers={
                    "X-Shopify-Access-Token": self.access_token,
                    "Content-Type": "application/json"
                },
                json={
                    "customer": {
                        "email": email,
                        "first_name": name.split()[0] if name else "",
                        "last_name": name.split()[1] if len(name.split()) > 1 else "",
                        "verified_email": True,
                        "tags": "nexuslang-user"
                    }
                }
            )
            response.raise_for_status()
            return response.json()["customer"]
    
    async def create_subscription(
        self,
        customer_id: str,
        tier: str,
        billing_interval: str = "month"
    ) -> Dict[str, Any]:
        """
        Create a subscription for a customer.
        
        Args:
            customer_id: Shopify customer ID
            tier: Subscription tier (free, pro, enterprise)
            billing_interval: month or year
        """
        # Subscription plans
        plans = {
            "free": {
                "price": "0.00",
                "credits": settings.FREE_TIER_CREDITS,
                "name": "NexusLang Free"
            },
            "pro": {
                "price": "19.00",
                "credits": settings.PRO_TIER_CREDITS,
                "name": "NexusLang Pro"
            },
            "enterprise": {
                "price": "199.00",
                "credits": settings.ENTERPRISE_TIER_CREDITS,
                "name": "NexusLang Enterprise"
            }
        }
        
        plan = plans.get(tier.lower())
        if not plan:
            raise ValueError(f"Invalid tier: {tier}")
        
        # For free tier, no Shopify subscription needed
        if tier.lower() == "free":
            return {
                "id": f"free-{customer_id}",
                "status": "active",
                "tier": "free",
                "credits": plan["credits"]
            }
        
        # Create recurring charge for paid tiers
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/recurring_application_charges.json",
                headers={
                    "X-Shopify-Access-Token": self.access_token,
                    "Content-Type": "application/json"
                },
                json={
                    "recurring_application_charge": {
                        "name": plan["name"],
                        "price": plan["price"],
                        "return_url": f"https://nexuslang.dev/billing/confirm",
                        "test": settings.DEBUG,  # Test mode in development
                        "trial_days": 7 if tier.lower() == "pro" else 0
                    }
                }
            )
            response.raise_for_status()
            charge = response.json()["recurring_application_charge"]
            
            return {
                "id": charge["id"],
                "confirmation_url": charge["confirmation_url"],
                "status": charge["status"],
                "tier": tier,
                "credits": plan["credits"]
            }
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """
        Cancel a subscription.
        """
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.api_url}/recurring_application_charges/{subscription_id}.json",
                headers={
                    "X-Shopify-Access-Token": self.access_token
                }
            )
            return response.status_code == 204
    
    async def create_one_time_charge(
        self,
        customer_id: str,
        amount: float,
        description: str
    ) -> Dict[str, Any]:
        """
        Create a one-time charge (for buying additional credits).
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/application_charges.json",
                headers={
                    "X-Shopify-Access-Token": self.access_token,
                    "Content-Type": "application/json"
                },
                json={
                    "application_charge": {
                        "name": description,
                        "price": str(amount),
                        "return_url": "https://nexuslang.dev/billing/credits-purchased",
                        "test": settings.DEBUG
                    }
                }
            )
            response.raise_for_status()
            return response.json()["application_charge"]
    
    async def get_subscription_status(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get current subscription status.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/recurring_application_charges/{subscription_id}.json",
                headers={
                    "X-Shopify-Access-Token": self.access_token
                }
            )
            response.raise_for_status()
            return response.json()["recurring_application_charge"]


class CreditManager:
    """
    Manages user credits and usage tracking.
    """
    
    @staticmethod
    async def get_balance(user_id: str, db) -> int:
        """Get user's credit balance."""
        from ...models.billing import Credit
        from sqlalchemy import select
        
        stmt = select(Credit).where(Credit.user_id == user_id)
        result = await db.execute(stmt)
        credit = result.scalar_one_or_none()
        
        if not credit:
            # Create default free tier credits
            credit = Credit(
                user_id=user_id,
                balance=settings.FREE_TIER_CREDITS,
                total_purchased=0,
                total_used=0
            )
            db.add(credit)
            await db.commit()
        
        return credit.balance
    
    @staticmethod
    async def add_credits(user_id: str, amount: int, db) -> int:
        """Add credits to user's account."""
        from ...models.billing import Credit, Transaction
        from sqlalchemy import select
        
        stmt = select(Credit).where(Credit.user_id == user_id)
        result = await db.execute(stmt)
        credit = result.scalar_one()
        
        credit.balance += amount
        credit.total_purchased += amount
        
        # Record transaction
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type="purchase",
            description=f"Purchased {amount} credits"
        )
        db.add(transaction)
        
        await db.commit()
        return credit.balance
    
    @staticmethod
    async def use_credits(user_id: str, amount: int, db, description: str = "") -> bool:
        """
        Use credits from user's account.
        Returns True if successful, False if insufficient credits.
        """
        from ...models.billing import Credit, Transaction
        from sqlalchemy import select
        
        stmt = select(Credit).where(Credit.user_id == user_id)
        result = await db.execute(stmt)
        credit = result.scalar_one()
        
        if credit.balance < amount:
            return False
        
        credit.balance -= amount
        credit.total_used += amount
        
        # Record transaction
        transaction = Transaction(
            user_id=user_id,
            amount=-amount,
            type="usage",
            description=description or "Credit usage"
        )
        db.add(transaction)
        
        await db.commit()
        return True
    
    @staticmethod
    async def refill_subscription_credits(user_id: str, tier: str, db) -> int:
        """
        Refill credits based on subscription tier (monthly).
        """
        credits_map = {
            "free": settings.FREE_TIER_CREDITS,
            "pro": settings.PRO_TIER_CREDITS,
            "enterprise": settings.ENTERPRISE_TIER_CREDITS
        }
        
        credits = credits_map.get(tier.lower(), 0)
        
        from ...models.billing import Credit, Transaction
        from sqlalchemy import select
        
        stmt = select(Credit).where(Credit.user_id == user_id)
        result = await db.execute(stmt)
        credit = result.scalar_one()
        
        credit.balance = credits  # Reset to tier amount
        credit.last_refill_at = datetime.utcnow()
        
        # Record transaction
        transaction = Transaction(
            user_id=user_id,
            amount=credits,
            type="refill",
            description=f"Monthly {tier} tier credit refill"
        )
        db.add(transaction)
        
        await db.commit()
        return credits
    
    @staticmethod
    def calculate_credit_cost(service: str, amount: int) -> int:
        """
        Calculate credit cost for a service usage.
        
        Args:
            service: Service name (nexuslang, grokopedia, voice, etc.)
            amount: Amount of usage (tokens, queries, seconds, etc.)
        
        Returns:
            Credit cost
        """
        # Pricing per 1000 units
        pricing = {
            "nexuslang": 1,      # 1 credit per 1000 tokens
            "grokopedia": 2,     # 2 credits per query
            "voice_stt": 5,      # 5 credits per minute
            "voice_tts": 5,      # 5 credits per minute
            "api": 1             # 1 credit per 1000 API calls
        }
        
        rate = pricing.get(service, 1)
        
        if service in ["voice_stt", "voice_tts"]:
            # Amount is in seconds, convert to minutes
            minutes = amount / 60
            return int(minutes * rate)
        else:
            # Amount is in units, divide by 1000
            return int((amount / 1000) * rate)


# Global instances
_shopify_client = None
_credit_manager = CreditManager()


def get_shopify_client() -> ShopifyClient:
    """Get or create global Shopify client."""
    global _shopify_client
    if _shopify_client is None:
        _shopify_client = ShopifyClient()
    return _shopify_client


def get_credit_manager() -> CreditManager:
    """Get global credit manager."""
    return _credit_manager

