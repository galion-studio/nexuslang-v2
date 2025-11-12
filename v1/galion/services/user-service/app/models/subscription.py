"""
Subscription and Badge models for the user service.
Handles subscription tiers, badges, and payment tracking.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Numeric, Date, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base


class SubscriptionPlan(Base):
    """
    Subscription Plans - Badge-based tiers.
    
    Each plan represents a subscription tier with:
    - Badge (Explorer, Pioneer, Master, Legend, Titan)
    - Pricing (monthly/yearly)
    - Features and limits
    """
    
    __tablename__ = "subscription_plans"
    __table_args__ = {"schema": "public"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    badge_name = Column(String(50), unique=True, nullable=False)
    badge_icon = Column(String(50))
    badge_color = Column(String(20))
    
    # Pricing
    price_monthly = Column(Numeric(10, 2), nullable=False)
    price_yearly = Column(Numeric(10, 2))
    
    # Features and limits (stored as JSONB for flexibility)
    features = Column(JSONB, nullable=False, default=[])
    limits = Column(JSONB, nullable=False, default={})
    
    # Status
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")


class UserSubscription(Base):
    """
    User Subscriptions - Tracks user's current and past subscriptions.
    """
    
    __tablename__ = "user_subscriptions"
    __table_args__ = {"schema": "public"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("public.subscription_plans.id"), nullable=False)
    
    # Subscription status
    status = Column(String(20), nullable=False, default="active", index=True)
    # Status options: active, cancelled, expired, suspended, trial
    
    billing_cycle = Column(String(20), nullable=False, default="monthly")
    # Billing options: monthly, yearly
    
    # Dates
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), index=True)
    cancelled_at = Column(DateTime(timezone=True))
    last_payment_at = Column(DateTime(timezone=True))
    next_billing_date = Column(Date)
    
    # Payment info
    payment_method = Column(String(50))  # stripe, paypal, crypto
    stripe_subscription_id = Column(String(255))
    stripe_customer_id = Column(String(255))
    
    # Settings
    auto_renew = Column(Boolean, default=True)
    metadata = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")


class PaymentHistory(Base):
    """
    Payment History - Tracks all payment transactions.
    """
    
    __tablename__ = "payment_history"
    __table_args__ = {"schema": "public"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("public.user_subscriptions.id"))
    
    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(20), nullable=False)
    # Status options: succeeded, failed, pending, refunded
    
    payment_method = Column(String(50))
    transaction_id = Column(String(255))
    stripe_payment_intent_id = Column(String(255))
    
    description = Column(Text)
    metadata = Column(JSONB, default={})
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class UsageTracking(Base):
    """
    Usage Tracking - Tracks resource usage for billing and limits.
    """
    
    __tablename__ = "usage_tracking"
    __table_args__ = {"schema": "public"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Resource tracking
    resource_type = Column(String(50), nullable=False)
    # Types: ai_requests, voice_minutes, api_calls, storage_gb, etc.
    
    amount = Column(Integer, nullable=False, default=1)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    metadata = Column(JSONB, default={})
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

