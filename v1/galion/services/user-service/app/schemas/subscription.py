"""
Pydantic schemas for subscription management.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID


# ============================================================================
# SUBSCRIPTION PLAN SCHEMAS
# ============================================================================

class SubscriptionPlanBase(BaseModel):
    name: str
    display_name: str
    badge_name: str
    badge_icon: Optional[str] = None
    badge_color: Optional[str] = None
    price_monthly: Decimal
    price_yearly: Optional[Decimal] = None
    features: List[str] = []
    limits: Dict[str, Any] = {}
    is_active: bool = True


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass


class SubscriptionPlanUpdate(BaseModel):
    display_name: Optional[str] = None
    price_monthly: Optional[Decimal] = None
    price_yearly: Optional[Decimal] = None
    features: Optional[List[str]] = None
    limits: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SubscriptionPlanResponse(SubscriptionPlanBase):
    id: UUID
    sort_order: int
    created_at: datetime
    updated_at: datetime
    
    # Add computed fields
    yearly_savings: Optional[Decimal] = None
    recommended: bool = False
    
    class Config:
        from_attributes = True
    
    @validator('yearly_savings', always=True)
    def calculate_yearly_savings(cls, v, values):
        if 'price_yearly' in values and values['price_yearly']:
            monthly_equivalent = values['price_monthly'] * 12
            return monthly_equivalent - values['price_yearly']
        return None


# ============================================================================
# USER SUBSCRIPTION SCHEMAS
# ============================================================================

class UserSubscriptionBase(BaseModel):
    plan_id: UUID
    billing_cycle: str = Field(default="monthly", regex="^(monthly|yearly)$")
    payment_method: Optional[str] = None


class UserSubscriptionCreate(UserSubscriptionBase):
    pass


class UserSubscriptionUpdate(BaseModel):
    auto_renew: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class UserSubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan_id: UUID
    status: str
    billing_cycle: str
    started_at: datetime
    expires_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    next_billing_date: Optional[date]
    payment_method: Optional[str]
    auto_renew: bool
    created_at: datetime
    
    # Include plan details
    plan: Optional[SubscriptionPlanResponse] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# PAYMENT HISTORY SCHEMAS
# ============================================================================

class PaymentHistoryBase(BaseModel):
    amount: Decimal
    currency: str = "USD"
    payment_method: Optional[str] = None
    description: Optional[str] = None


class PaymentHistoryResponse(PaymentHistoryBase):
    id: UUID
    user_id: UUID
    subscription_id: Optional[UUID]
    status: str
    transaction_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# USAGE TRACKING SCHEMAS
# ============================================================================

class UsageTrackingResponse(BaseModel):
    resource_type: str
    amount: int
    period_start: date
    period_end: date
    
    class Config:
        from_attributes = True


class CurrentUsageResponse(BaseModel):
    """Current period usage summary."""
    user_id: UUID
    plan_name: str
    badge_name: str
    period_start: date
    period_end: date
    usage: Dict[str, int]
    limits: Dict[str, Any]
    usage_percentage: Dict[str, Optional[float]]


# ============================================================================
# SUBSCRIPTION CHECKOUT SCHEMAS
# ============================================================================

class CheckoutRequest(BaseModel):
    plan_id: UUID
    billing_cycle: str = Field(default="monthly", regex="^(monthly|yearly)$")
    payment_method: str = Field(default="stripe")
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str
    amount: Decimal
    currency: str = "USD"


# ============================================================================
# SUBSCRIPTION MANAGEMENT SCHEMAS
# ============================================================================

class CancelSubscriptionRequest(BaseModel):
    reason: Optional[str] = None
    feedback: Optional[str] = None


class UpgradeDowngradeRequest(BaseModel):
    new_plan_id: UUID
    billing_cycle: Optional[str] = None
    immediate: bool = False  # If False, changes at next billing


# ============================================================================
# PRICING COMPARISON SCHEMAS
# ============================================================================

class PricingComparisonResponse(BaseModel):
    """Response for pricing comparison page."""
    plans: List[SubscriptionPlanResponse]
    current_plan: Optional[str] = None
    recommended_plan: str = "pro"  # Default recommendation
    annual_discount_percentage: Decimal = Decimal("16.67")  # ~2 months free


# ============================================================================
# USER DASHBOARD SCHEMAS
# ============================================================================

class SubscriptionDashboardResponse(BaseModel):
    """Complete subscription dashboard data."""
    user_id: UUID
    current_subscription: Optional[UserSubscriptionResponse]
    usage: CurrentUsageResponse
    payment_history: List[PaymentHistoryResponse]
    available_plans: List[SubscriptionPlanResponse]
    can_upgrade: bool
    can_downgrade: bool

