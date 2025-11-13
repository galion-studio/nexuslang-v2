"""
Credit Service
==============

Comprehensive credit management system for NexusLang v2.

Features:
- Credit balance management
- Credit transaction tracking
- Credit purchase processing
- Credit usage analytics
- Credit limits and warnings
- Subscription credit allocation
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from decimal import Decimal

from ...models.user import User
from ...models.billing import Credit, Transaction, TransactionType, TransactionStatus
from ...core.database import get_db


class CreditService:
    """Credit management service."""

    # ACTUAL API COSTS (what we pay to providers)
    # Based on current market rates (2025)
    ACTUAL_API_COSTS = {
        # OpenAI GPT-4 Turbo: $0.01 per 1K input tokens, $0.03 per 1K output tokens
        # Claude 3.5 Sonnet: $0.015 per 1K input, $0.075 per 1K output
        # Average: $0.03 per 1K tokens
        "chat_per_1k_tokens": 0.03,     # $0.03 actual cost

        # Stability AI SDXL: $0.04 per image (512x512)
        "image_generation": 0.04,       # $0.04 actual cost

        # Runway ML Gen-3: $0.12 per second of video (5s video = $0.60)
        "video_generation_per_second": 0.12,  # $0.12 per second actual cost

        # ElevenLabs: $0.18 per 1K characters
        "tts_per_1k_chars": 0.18,       # $0.18 per 1K chars actual cost

        # OpenAI Whisper: $0.006 per minute
        "stt_per_minute": 0.006,        # $0.006 per minute actual cost

        # Code execution: negligible server costs
        "code_execution": 0.001,        # $0.001 actual cost
    }

    # CREDIT PRICING WITH 80%+ MARGIN
    # Formula: (Actual Cost × 5) = 80% margin
    # Example: $0.03 actual cost × 5 = $0.15 credit cost
    CREDIT_COSTS = {
        "chat_per_1k_tokens": 0.15,     # 5x markup: $0.15 per 1K tokens (80% margin)
        "image_generation": 0.20,       # 5x markup: $0.20 per image (80% margin)
        "video_generation_per_second": 0.60,  # 5x markup: $0.60 per second (80% margin)
        "tts_per_1k_chars": 0.90,       # 5x markup: $0.90 per 1K chars (80% margin)
        "stt_per_minute": 0.03,         # 5x markup: $0.03 per minute (80% margin)
        "code_execution": 0.005,        # 5x markup: $0.005 per execution (80% margin)
    }

    # CREDIT PACKAGES WITH VOLUME DISCOUNTS (maintaining high margins)
    CREDIT_PACKAGES = {
        # Starter packages
        50: {"price": 7.50, "margin": "87%", "description": "Getting started"},
        100: {"price": 12.00, "margin": "87%", "description": "Most popular"},

        # Small business packages
        500: {"price": 50.00, "margin": "90%", "description": "Small team"},
        1000: {"price": 85.00, "margin": "91%", "description": "Growing business"},
        2500: {"price": 187.50, "margin": "92%", "description": "Enterprise starter"},

        # Enterprise packages (highest margins due to volume)
        5000: {"price": 350.00, "margin": "93%", "description": "Large enterprise"},
        10000: {"price": 650.00, "margin": "93.5%", "description": "Enterprise unlimited"},
    }

    # SUBSCRIPTION PRICING WITH HIGH MARGINS
    # Since credits are our main revenue driver, subscriptions provide steady income
    SUBSCRIPTION_PRICING = {
        "free": {"price": 0, "credits": 50, "margin": "100%"},
        "creator": {"price": 29, "credits": 1000, "margin": "94%"},     # ~$0.029 per credit
        "professional": {"price": 79, "credits": 5000, "margin": "95%"}, # ~$0.016 per credit
        "business": {"price": 199, "credits": 15000, "margin": "96%"},   # ~$0.013 per credit
        "enterprise": {"price": 499, "credits": -1, "margin": "97%"},    # Unlimited
    }

    # Credit warning thresholds
    WARNING_THRESHOLDS = {
        "low": 10.0,      # Warn when credits drop below 10
        "critical": 1.0,  # Critical warning when credits drop below 1
    }

    def __init__(self, db: Session):
        self.db = db

    def get_credit_balance(self, user_id: int) -> Dict[str, float]:
        """Get user's current credit balance and usage statistics."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Get monthly usage (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        monthly_usage = self.db.query(func.sum(Credit.amount)).filter(
            Credit.user_id == user_id,
            Credit.amount < 0,  # Only usage transactions (negative amounts)
            Credit.created_at >= thirty_days_ago
        ).scalar() or 0

        monthly_usage = abs(monthly_usage)  # Convert to positive

        # Get credit history
        recent_transactions = self.db.query(Credit).filter(
            Credit.user_id == user_id
        ).order_by(desc(Credit.created_at)).limit(10).all()

        return {
            "current_balance": float(user.credits),
            "total_used": float(user.credits_used),
            "monthly_usage": float(monthly_usage),
            "subscription_tier": user.subscription_tier,
            "warning_level": self._get_warning_level(user.credits),
            "recent_transactions": [
                {
                    "id": str(tx.id),
                    "amount": float(tx.amount),
                    "source": tx.source,
                    "description": tx.description,
                    "created_at": tx.created_at.isoformat()
                } for tx in recent_transactions
            ]
        }

    def deduct_credits(self, user_id: int, amount: float, source: str, description: str = "") -> bool:
        """
        Deduct credits from user account.

        Args:
            user_id: User ID
            amount: Amount to deduct (positive value)
            source: Source of deduction (e.g., 'ai_chat', 'image_generation')
            description: Optional description

        Returns:
            True if successful, False if insufficient credits
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        if user.credits < amount:
            return False

        # Deduct from user balance
        user.credits -= amount
        user.credits_used += amount
        user.updated_at = datetime.utcnow()

        # Create credit transaction record
        transaction = Credit(
            user_id=user_id,
            amount=-amount,  # Negative for deductions
            source=source,
            description=description or f"Credit deduction for {source}",
            created_at=datetime.utcnow()
        )

        self.db.add(transaction)
        self.db.commit()

        return True

    def add_credits(self, user_id: int, amount: float, source: str, description: str = "") -> bool:
        """
        Add credits to user account.

        Args:
            user_id: User ID
            amount: Amount to add (positive value)
            source: Source of addition (e.g., 'purchase', 'bonus')
            description: Optional description

        Returns:
            True if successful
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Add to user balance
        user.credits += amount
        user.updated_at = datetime.utcnow()

        # Create credit transaction record
        transaction = Credit(
            user_id=user_id,
            amount=amount,  # Positive for additions
            source=source,
            description=description or f"Credit addition from {source}",
            created_at=datetime.utcnow()
        )

        self.db.add(transaction)
        self.db.commit()

        return True

    def purchase_credits(self, user_id: int, credit_amount: int, payment_method_id: Optional[str] = None) -> Tuple[bool, float, str]:
        """
        Process credit purchase with robust validation and error handling.

        Args:
            user_id: User ID
            credit_amount: Number of credits to purchase
            payment_method_id: Payment method ID (for future Stripe integration)

        Returns:
            (success, total_cost, message)
        """
        # Validate credit package
        if credit_amount not in self.CREDIT_PACKAGES:
            available_packages = list(self.CREDIT_PACKAGES.keys())
            return False, 0.0, f"Invalid credit amount. Available packages: {available_packages}"

        # Get package details
        package = self.CREDIT_PACKAGES[credit_amount]
        total_cost = package["price"]

        # Validate user exists and is active
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, 0.0, "User not found"

        if not user.is_active:
            return False, 0.0, "User account is not active"

        # Calculate actual cost and profit margin for tracking
        actual_cost_per_credit = sum(self.ACTUAL_API_COSTS.values()) / len(self.ACTUAL_API_COSTS)
        profit_margin = ((total_cost - (credit_amount * actual_cost_per_credit)) / total_cost) * 100

        # TODO: Implement actual payment processing with Stripe
        # For now, we'll simulate successful payment with proper transaction logging

        try:
            # Start transaction for atomicity
            # Add credits to user account
            success = self.add_credits(
                user_id=user_id,
                amount=credit_amount,
                source="purchase",
                description=f"Credit purchase: {credit_amount} credits for ${total_cost:.2f} ({profit_margin:.1f}% margin)"
            )

            if success:
                # Log the transaction for business analytics
                self._log_business_transaction(
                    user_id=user_id,
                    transaction_type="credit_purchase",
                    amount=total_cost,
                    credits=credit_amount,
                    profit_margin=profit_margin,
                    metadata={
                        "package_size": credit_amount,
                        "unit_price": total_cost / credit_amount,
                        "payment_method": payment_method_id or "simulated"
                    }
                )

                return True, total_cost, f"Successfully purchased {credit_amount} credits for ${total_cost:.2f} ({package.get('margin', 'High')} margin)"
            else:
                return False, 0.0, "Failed to add credits to account"

        except Exception as e:
            self.db.rollback()
            return False, 0.0, f"Transaction failed: {str(e)}"

    def calculate_ai_cost(self, operation: str, **kwargs) -> float:
        """
        Calculate credit cost for AI operations with 80%+ margin.

        Args:
            operation: Type of operation ('chat', 'image', 'video', 'tts', 'stt', 'code')
            **kwargs: Operation-specific parameters

        Returns:
            Credit cost
        """
        if operation == "chat":
            tokens = kwargs.get("tokens", 0)
            return (tokens / 1000) * self.CREDIT_COSTS["chat_per_1k_tokens"]

        elif operation == "image":
            return self.CREDIT_COSTS["image_generation"]

        elif operation == "video":
            # Video cost per second with 5x markup
            duration_seconds = kwargs.get("duration_seconds", 5)  # Default 5 seconds
            return duration_seconds * self.CREDIT_COSTS["video_generation_per_second"]

        elif operation == "tts":
            characters = kwargs.get("characters", 0)
            return (characters / 1000) * self.CREDIT_COSTS["tts_per_1k_chars"]

        elif operation == "stt":
            minutes = kwargs.get("minutes", 0)
            return minutes * self.CREDIT_COSTS["stt_per_minute"]

        elif operation == "code_execution":
            return self.CREDIT_COSTS["code_execution"]

        else:
            raise ValueError(f"Unknown operation: {operation}")

    def _log_business_transaction(self, user_id: int, transaction_type: str, amount: float,
                                 credits: int, profit_margin: float, metadata: Dict = None):
        """
        Log business transaction for analytics and reporting.

        This helps track profitability and business metrics.
        """
        try:
            # In a real implementation, this would log to a separate analytics database
            # For now, we'll just log to console/file
            transaction_data = {
                "user_id": user_id,
                "type": transaction_type,
                "amount": amount,
                "credits": credits,
                "profit_margin": profit_margin,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }

            # TODO: Implement proper analytics logging
            # For now, just print for debugging
            print(f"BUSINESS_TRANSACTION: {transaction_data}")

        except Exception as e:
            # Don't fail the main transaction if logging fails
            print(f"Warning: Failed to log business transaction: {e}")

    def validate_credit_purchase(self, credit_amount: int) -> Tuple[bool, str]:
        """
        Validate credit purchase parameters.

        Returns:
            (is_valid, error_message)
        """
        if not isinstance(credit_amount, int) or credit_amount <= 0:
            return False, "Credit amount must be a positive integer"

        if credit_amount not in self.CREDIT_PACKAGES:
            available = list(self.CREDIT_PACKAGES.keys())
            return False, f"Invalid credit amount. Available: {available}"

        # Check for reasonable limits (prevent abuse)
        if credit_amount > 10000:
            return False, "Maximum purchase limit is 10,000 credits"

        return True, ""

    def get_profitability_report(self, days: int = 30) -> Dict:
        """
        Generate profitability report for the given period.

        This helps monitor business health and margins.
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get all credit purchases in period
        purchases = self.db.query(Credit).filter(
            Credit.source == "purchase",
            Credit.created_at >= start_date
        ).all()

        total_revenue = 0
        total_credits_sold = 0
        transactions = []

        for purchase in purchases:
            # Extract cost from description (this is a bit hacky but works for now)
            description = purchase.description or ""
            if "$" in description:
                try:
                    # Parse amount from description like "Credit purchase: 100 credits for $12.00"
                    amount_str = description.split("$")[1].split()[0]
                    amount = float(amount_str)
                    total_revenue += amount
                    total_credits_sold += abs(purchase.amount)

                    transactions.append({
                        "amount": amount,
                        "credits": abs(purchase.amount),
                        "margin": self.CREDIT_PACKAGES.get(abs(purchase.amount), {}).get("margin", "Unknown")
                    })
                except:
                    pass

        # Calculate average margin
        avg_margin = 0
        if transactions:
            margins = []
            for t in transactions:
                margin_str = t["margin"].rstrip("%")
                try:
                    margins.append(float(margin_str))
                except:
                    pass
            if margins:
                avg_margin = sum(margins) / len(margins)

        # Estimate costs (rough calculation)
        estimated_costs = total_credits_sold * 0.05  # Rough average cost per credit
        estimated_profit = total_revenue - estimated_costs

        return {
            "period_days": days,
            "total_revenue": total_revenue,
            "total_credits_sold": total_credits_sold,
            "estimated_costs": estimated_costs,
            "estimated_profit": estimated_profit,
            "average_margin": avg_margin,
            "transactions_count": len(transactions),
            "profit_margin": (estimated_profit / total_revenue * 100) if total_revenue > 0 else 0
        }

    def get_credit_history(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get user's credit transaction history."""
        transactions = self.db.query(Credit).filter(
            Credit.user_id == user_id
        ).order_by(desc(Credit.created_at)).offset(offset).limit(limit).all()

        return [
            {
                "id": str(tx.id),
                "amount": float(tx.amount),
                "source": tx.source,
                "description": tx.description,
                "created_at": tx.created_at.isoformat(),
                "type": "credit" if tx.amount >= 0 else "debit"
            } for tx in transactions
        ]

    def get_credit_analytics(self, user_id: int, days: int = 30) -> Dict:
        """Get credit usage analytics."""
        start_date = datetime.utcnow() - timedelta(days=days)

        # Daily usage aggregation
        daily_usage = self.db.query(
            func.date(Credit.created_at).label('date'),
            func.sum(Credit.amount).label('amount')
        ).filter(
            Credit.user_id == user_id,
            Credit.amount < 0,  # Only debits (usage)
            Credit.created_at >= start_date
        ).group_by(
            func.date(Credit.created_at)
        ).order_by(
            func.date(Credit.created_at)
        ).all()

        # Usage by source
        usage_by_source = self.db.query(
            Credit.source,
            func.sum(func.abs(Credit.amount)).label('total')
        ).filter(
            Credit.user_id == user_id,
            Credit.amount < 0,
            Credit.created_at >= start_date
        ).group_by(Credit.source).all()

        # Total spent in period
        total_spent = self.db.query(func.sum(func.abs(Credit.amount))).filter(
            Credit.user_id == user_id,
            Credit.amount < 0,
            Credit.created_at >= start_date
        ).scalar() or 0

        return {
            "period_days": days,
            "total_spent": float(total_spent),
            "daily_usage": [
                {
                    "date": str(day.date),
                    "amount": float(abs(day.amount))
                } for day in daily_usage
            ],
            "usage_by_source": [
                {
                    "source": source,
                    "amount": float(total)
                } for source, total in usage_by_source
            ]
        }

    def check_credit_limits(self, user_id: int) -> Dict[str, bool]:
        """Check if user is approaching credit limits."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        credits = float(user.credits)

        return {
            "is_low": credits <= self.WARNING_THRESHOLDS["low"],
            "is_critical": credits <= self.WARNING_THRESHOLDS["critical"],
            "is_empty": credits <= 0,
            "current_balance": credits
        }

    def allocate_monthly_credits(self, user_id: int) -> bool:
        """Allocate monthly subscription credits."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Get subscription tier info
        from ...services.subscription_tiers import get_subscription_tier
        tier_info = get_subscription_tier(user.subscription_tier)

        monthly_credits = tier_info.get("credits_per_month", 0)

        if monthly_credits > 0:
            # Reset credits to monthly allocation
            old_balance = user.credits
            user.credits = monthly_credits
            user.updated_at = datetime.utcnow()

            # Record the allocation
            transaction = Credit(
                user_id=user_id,
                amount=monthly_credits,
                source="monthly_allocation",
                description=f"Monthly credit allocation: {monthly_credits} credits",
                created_at=datetime.utcnow()
            )

            self.db.add(transaction)
            self.db.commit()

            return True

        return False

    def _get_warning_level(self, credits: float) -> str:
        """Get credit warning level."""
        if credits <= self.WARNING_THRESHOLDS["critical"]:
            return "critical"
        elif credits <= self.WARNING_THRESHOLDS["low"]:
            return "low"
        else:
            return "normal"


# Global credit service instance
def get_credit_service(db: Session = None) -> CreditService:
    """Get credit service instance."""
    if db is None:
        # Get from dependency injection
        from ...core.database import get_db
        db = next(get_db())
    return CreditService(db)
