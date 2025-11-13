"""
Billing API Endpoints
Subscription management, credit purchases, and transaction history.

Endpoints:
- GET /subscriptions - List available subscription tiers
- POST /subscribe - Subscribe to a tier
- POST /cancel - Cancel subscription
- GET /credits - Get credit balance
- POST /credits/purchase - Purchase credits
- GET /transactions - Get transaction history
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..api.auth import get_current_user
from ..core.database import get_db
from ..models.user import User

router = APIRouter(prefix="/billing", tags=["Billing"])


# Request/Response Models
class SubscriptionTier(BaseModel):
    """Subscription tier information."""
    id: str
    name: str
    price: float
    interval: str  # monthly, yearly
    credits_per_month: int
    features: List[str]
    limits: dict


class SubscribeRequest(BaseModel):
    """Subscription request."""
    tier_id: str = Field(..., description="Subscription tier ID")
    payment_method: Optional[str] = Field(None, description="Payment method ID")


class CreditPurchaseRequest(BaseModel):
    """Credit purchase request."""
    amount: int = Field(..., ge=100, description="Number of credits to purchase")
    payment_method: Optional[str] = Field(None, description="Payment method ID")


# Subscription tiers (from PROJECT_STATE_COMPLETE.md)
SUBSCRIPTION_TIERS = {
    "free": {
        "id": "free",
        "name": "Free",
        "price": 0,
        "interval": "monthly",
        "credits_per_month": 100,
        "features": [
            "100 free credits",
            "Basic AI models",
            "Community support",
            "3 projects max"
        ],
        "limits": {
            "max_projects": 3,
            "api_calls_per_day": 100,
            "storage_gb": 1
        }
    },
    "creator": {
        "id": "creator",
        "name": "Creator",
        "price": 20,
        "interval": "monthly",
        "credits_per_month": 1000,
        "features": [
            "1,000 credits/month",
            "All AI models",
            "Priority support",
            "10 projects",
            "Commercial license"
        ],
        "limits": {
            "max_projects": 10,
            "api_calls_per_day": 1000,
            "storage_gb": 10
        }
    },
    "professional": {
        "id": "professional",
        "name": "Professional",
        "price": 50,
        "interval": "monthly",
        "credits_per_month": 5000,
        "features": [
            "5,000 credits/month",
            "All AI models",
            "Priority support",
            "50 projects",
            "Team features (5 members)",
            "Advanced analytics"
        ],
        "limits": {
            "max_projects": 50,
            "api_calls_per_day": 10000,
            "storage_gb": 100,
            "team_members": 5
        }
    },
    "business": {
        "id": "business",
        "name": "Business",
        "price": 200,
        "interval": "monthly",
        "credits_per_month": 25000,
        "features": [
            "25,000 credits/month",
            "All AI models",
            "Dedicated support",
            "200 projects",
            "Team features (20 members)",
            "White-label options",
            "Custom integrations"
        ],
        "limits": {
            "max_projects": 200,
            "api_calls_per_day": 100000,
            "storage_gb": 500,
            "team_members": 20
        }
    },
    "enterprise": {
        "id": "enterprise",
        "name": "Enterprise",
        "price": 2500,
        "interval": "monthly",
        "credits_per_month": -1,  # Unlimited
        "features": [
            "Unlimited credits",
            "All AI models",
            "24/7 dedicated support",
            "Unlimited projects",
            "Unlimited team members",
            "White-label",
            "Custom SLA",
            "On-premise deployment"
        ],
        "limits": {
            "max_projects": -1,
            "api_calls_per_day": -1,
            "storage_gb": -1,
            "team_members": -1
        }
    }
}


# Endpoints

@router.get("/subscriptions", response_model=List[SubscriptionTier])
async def list_subscriptions():
    """
    List all available subscription tiers.
    
    Returns pricing and features for each tier.
    """
    return list(SUBSCRIPTION_TIERS.values())


@router.get("/subscription")
async def get_current_subscription(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's subscription details.
    
    Returns active subscription information.
    """
    tier_info = SUBSCRIPTION_TIERS.get(current_user.subscription_tier, SUBSCRIPTION_TIERS["free"])
    
    return {
        "tier": tier_info,
        "status": current_user.subscription_status,
        "start_date": current_user.subscription_start.isoformat() if current_user.subscription_start else None,
        "end_date": current_user.subscription_end.isoformat() if current_user.subscription_end else None,
        "is_active": current_user.is_subscription_active()
    }


@router.post("/subscribe")
async def subscribe(
    request: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Subscribe to a tier.
    
    Note: Payment processing not yet implemented.
    This endpoint updates subscription tier for testing.
    """
    # Validate tier
    if request.tier_id not in SUBSCRIPTION_TIERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {request.tier_id}"
        )
    
    tier = SUBSCRIPTION_TIERS[request.tier_id]
    
    # TODO: Implement Shopify/Stripe payment processing
    
    # Update user subscription
    current_user.subscription_tier = request.tier_id
    current_user.subscription_status = "active"
    current_user.subscription_start = datetime.utcnow()
    current_user.subscription_end = datetime.utcnow() + timedelta(days=30)
    
    # Add credits for new tier
    current_user.add_credits(tier["credits_per_month"])
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Subscribed to {tier['name']} plan",
        "tier": tier,
        "credits_added": tier["credits_per_month"]
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel current subscription.
    
    Subscription remains active until end of billing period.
    """
    if current_user.subscription_tier == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Free tier cannot be canceled"
        )
    
    current_user.subscription_status = "canceled"
    db.commit()
    
    return {
        "success": True,
        "message": "Subscription canceled. Access remains until end of billing period.",
        "end_date": current_user.subscription_end.isoformat() if current_user.subscription_end else None
    }


@router.get("/credits")
async def get_credits(current_user: User = Depends(get_current_user)):
    """
    Get current credit balance and usage statistics.
    
    Returns credits available, used, and monthly allocation.
    """
    tier_info = SUBSCRIPTION_TIERS.get(current_user.subscription_tier, SUBSCRIPTION_TIERS["free"])
    
    return {
        "credits_available": current_user.credits,
        "credits_used_total": current_user.credits_used,
        "monthly_allocation": tier_info["credits_per_month"],
        "subscription_tier": current_user.subscription_tier
    }


@router.post("/credits/purchase")
async def purchase_credits(
    request: CreditPurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Purchase additional credits.
    
    Credit packages:
    - 100 credits = $10
    - 500 credits = $45 (10% discount)
    - 1000 credits = $80 (20% discount)
    
    Note: Payment processing not yet implemented.
    """
    # Calculate cost (simplified pricing)
    cost_per_credit = 0.10  # $0.10 per credit
    if request.amount >= 1000:
        cost_per_credit = 0.08  # 20% discount
    elif request.amount >= 500:
        cost_per_credit = 0.09  # 10% discount
    
    total_cost = request.amount * cost_per_credit
    
    # TODO: Implement actual payment processing
    
    # Add credits
    current_user.add_credits(request.amount)
    db.commit()
    
    return {
        "success": True,
        "credits_purchased": request.amount,
        "cost": total_cost,
        "new_balance": current_user.credits
    }


@router.get("/transactions")
async def get_transactions(
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """
    Get transaction history.
    
    Returns recent billing transactions.
    Note: Full implementation requires transaction tracking model.
    """
    # TODO: Implement transaction history from database
    
    return {
        "transactions": [],
        "message": "Transaction history coming soon"
    }
