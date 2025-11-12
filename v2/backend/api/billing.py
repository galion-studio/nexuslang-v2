"""
Billing API routes.
Handles subscriptions, credits, and Shopify integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime
import uuid

from ..core.database import get_db
from ..models.user import User
from ..models.billing import Subscription, Credit, Transaction, SubscriptionTier, TransactionType, TransactionStatus
from ..api.auth import get_current_user

router = APIRouter()


# Request/Response Models
class SubscribeRequest(BaseModel):
    tier: str  # 'free', 'pro', 'enterprise'


class PurchaseCreditsRequest(BaseModel):
    package: str  # 'starter', 'pro', 'business', 'enterprise'


class SubscriptionResponse(BaseModel):
    id: str
    tier: str
    status: str
    credits_included: int
    credits_remaining: int
    price_monthly: float
    starts_at: datetime
    ends_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CreditBalanceResponse(BaseModel):
    balance: int
    used_this_month: int
    included_credits: int
    purchased_credits: int


class TransactionResponse(BaseModel):
    id: str
    type: str
    amount: float
    credits: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Subscription Endpoints
@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's current subscription information.
    """
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id
        ).order_by(Subscription.created_at.desc())
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        # Create default free subscription
        subscription = Subscription(
            user_id=current_user.id,
            tier=SubscriptionTier.FREE,
            status="active",
            credits_included=100,
            credits_remaining=100,
            price_monthly=0.0
        )
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
    
    return SubscriptionResponse(
        id=str(subscription.id),
        tier=subscription.tier.value,
        status=subscription.status,
        credits_included=subscription.credits_included,
        credits_remaining=subscription.credits_remaining,
        price_monthly=subscription.price_monthly,
        starts_at=subscription.starts_at,
        ends_at=subscription.ends_at
    )


@router.post("/subscribe")
async def subscribe(
    request: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Subscribe to a paid tier.
    Returns Shopify checkout URL.
    """
    # Validate tier
    tier_config = {
        "free": {"credits": 100, "price": 0},
        "pro": {"credits": 10000, "price": 19},
        "enterprise": {"credits": -1, "price": 199}  # -1 = unlimited
    }
    
    if request.tier not in tier_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier. Choose from: {list(tier_config.keys())}"
        )
    
    config = tier_config[request.tier]
    
    # For MVP: Create subscription directly without Shopify
    # In production: Generate Shopify checkout URL
    
    # Check if user already has active subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing and existing.tier != SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active subscription. Cancel it first."
        )
    
    # Create new subscription
    try:
        tier_enum = SubscriptionTier(request.tier)
    except ValueError:
        tier_enum = SubscriptionTier.FREE
    
    subscription = Subscription(
        user_id=current_user.id,
        tier=tier_enum,
        status="active",
        credits_included=config["credits"],
        credits_remaining=config["credits"],
        price_monthly=config["price"]
    )
    
    # Cancel existing free tier
    if existing:
        existing.status = "cancelled"
        existing.ends_at = datetime.utcnow()
    
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    
    # Create transaction record
    transaction = Transaction(
        user_id=current_user.id,
        type=TransactionType.SUBSCRIPTION,
        amount=config["price"],
        credits=config["credits"],
        status=TransactionStatus.COMPLETED,
        metadata={"tier": request.tier}
    )
    db.add(transaction)
    await db.commit()
    
    return {
        "subscription_id": str(subscription.id),
        "tier": request.tier,
        "status": "active",
        "message": f"Successfully subscribed to {request.tier} tier!"
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel current subscription.
    Subscription remains active until end of billing period.
    """
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    if subscription.tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel free tier"
        )
    
    # Mark as cancelled
    subscription.status = "cancelled"
    # Set end date (in real app, this would be end of billing period)
    subscription.ends_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "message": "Subscription cancelled successfully",
        "tier": subscription.tier.value,
        "ends_at": subscription.ends_at
    }


# Credit Endpoints
@router.get("/credits", response_model=CreditBalanceResponse)
async def get_credits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's credit balance.
    """
    # Get subscription
    sub_result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        )
    )
    subscription = sub_result.scalar_one_or_none()
    
    # Get purchased credits
    credit_result = await db.execute(
        select(Credit).where(Credit.user_id == current_user.id)
    )
    credits = credit_result.scalars().all()
    
    total_purchased = sum(c.amount for c in credits if c.amount > 0)
    total_used = sum(abs(c.amount) for c in credits if c.amount < 0)
    
    included_credits = subscription.credits_remaining if subscription else 0
    
    return CreditBalanceResponse(
        balance=included_credits + total_purchased,
        used_this_month=total_used,
        included_credits=included_credits,
        purchased_credits=total_purchased
    )


@router.post("/credits/purchase")
async def purchase_credits(
    request: PurchaseCreditsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Purchase credit packages.
    Returns Shopify checkout URL.
    """
    packages = {
        "starter": {"credits": 1000, "price": 10, "bonus": 0},
        "pro": {"credits": 5000, "price": 45, "bonus": 500},
        "business": {"credits": 15000, "price": 120, "bonus": 2000},
        "enterprise": {"credits": 50000, "price": 350, "bonus": 10000}
    }
    
    if request.package not in packages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid package. Choose from: {list(packages.keys())}"
        )
    
    config = packages[request.package]
    total_credits = config["credits"] + config["bonus"]
    
    # Create credit record
    credit = Credit(
        user_id=current_user.id,
        amount=total_credits,
        source="purchase",
        description=f"Purchased {request.package} package"
    )
    
    db.add(credit)
    
    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        type=TransactionType.CREDIT_PURCHASE,
        amount=config["price"],
        credits=total_credits,
        status=TransactionStatus.COMPLETED,
        metadata={"package": request.package}
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(credit)
    
    return {
        "transaction_id": str(transaction.id),
        "credits_purchased": total_credits,
        "amount": config["price"],
        "package": request.package,
        "message": f"Successfully purchased {total_credits} credits!"
    }


@router.post("/credits/deduct")
async def deduct_credits(
    amount: int,
    description: str = "API usage",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deduct credits from user's balance (internal use).
    """
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )
    
    # Check balance
    balance_response = await get_credits(current_user, db)
    
    if balance_response.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Balance: {balance_response.balance}, Required: {amount}"
        )
    
    # Deduct from subscription credits first
    sub_result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        )
    )
    subscription = sub_result.scalar_one_or_none()
    
    if subscription and subscription.credits_remaining > 0:
        deduct_from_sub = min(amount, subscription.credits_remaining)
        subscription.credits_remaining -= deduct_from_sub
        amount -= deduct_from_sub
    
    # Deduct remaining from purchased credits
    if amount > 0:
        credit = Credit(
            user_id=current_user.id,
            amount=-amount,
            source="usage",
            description=description
        )
        db.add(credit)
    
    await db.commit()
    
    return {
        "message": "Credits deducted successfully",
        "remaining_balance": balance_response.balance - amount
    }


# Transaction History
@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's transaction history.
    """
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
    )
    transactions = result.scalars().all()
    
    return [
        TransactionResponse(
            id=str(t.id),
            type=t.type.value,
            amount=t.amount,
            credits=t.credits,
            status=t.status.value,
            created_at=t.created_at
        )
        for t in transactions
    ]


# Usage Stats
@router.get("/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get usage statistics for current billing period.
    """
    # Get all credit usage this month
    credit_result = await db.execute(
        select(Credit).where(
            Credit.user_id == current_user.id,
            Credit.amount < 0,
            Credit.created_at >= datetime.utcnow().replace(day=1)
        )
    )
    usage_credits = credit_result.scalars().all()
    
    total_used = sum(abs(c.amount) for c in usage_credits)
    
    # Breakdown by source
    by_source = {}
    for credit in usage_credits:
        source = credit.description or "other"
        by_source[source] = by_source.get(source, 0) + abs(credit.amount)
    
    return {
        "total_used": total_used,
        "breakdown": by_source,
        "period": "current_month"
    }

