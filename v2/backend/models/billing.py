"""
Billing and subscription models.
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
import enum

from ..core.database import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tier options."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status options."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAUSED = "paused"


class TransactionType(str, enum.Enum):
    """Transaction type options."""
    SUBSCRIPTION = "subscription"
    CREDIT_PURCHASE = "credit_purchase"
    USAGE = "usage"
    REFUND = "refund"
    BONUS = "bonus"


class TransactionStatus(str, enum.Enum):
    """Transaction status options."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Subscription(Base):
    """User subscription model."""
    
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tier = Column(SQLEnum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE)
    status = Column(String(20), nullable=False, default="active")
    credits_included = Column(Integer, default=100)
    credits_remaining = Column(Integer, default=100)
    price_monthly = Column(Integer, default=0)
    shopify_subscription_id = Column(String(255), index=True)
    shopify_customer_id = Column(String(255))
    starts_at = Column(DateTime, default=datetime.utcnow)
    ends_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Credit(Base):
    """User credit transaction model."""
    
    __tablename__ = "credits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # Positive for add, negative for deduct
    source = Column(String(100))  # 'purchase', 'usage', 'bonus', etc.
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    """Payment transaction history."""
    
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # In dollars
    credits = Column(Integer, nullable=False)  # Credits involved
    status = Column(SQLEnum(TransactionStatus), nullable=False, default=TransactionStatus.COMPLETED)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

