"""
User Model
Complete user data model with authentication, subscription, and credits.

Features:
- Basic authentication fields
- Subscription tier management
- Credit system
- Admin roles
- Timestamps
- Email verification
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """
    User model for authentication and profile management.
    
    Attributes:
        id: Primary key
        email: Unique email address
        username: Unique username
        hashed_password: BCrypt hashed password
        full_name: User's full name (optional)
        
        # Account status
        is_active: Account is active
        is_verified: Email is verified
        is_admin: User has admin privileges
        
        # Subscription
        subscription_tier: Current subscription tier (free, creator, professional, business, enterprise)
        subscription_status: Status of subscription (active, canceled, expired)
        subscription_start: When subscription started
        subscription_end: When subscription ends
        
        # Credits system
        credits: Available credits for API usage
        credits_used: Total credits used (for analytics)
        
        # Timestamps
        created_at: Account creation date
        updated_at: Last update date
        last_login: Last login timestamp
        
        # Profile
        avatar_url: Profile picture URL
        bio: User bio/description
        website: User's website
        
        # Settings
        preferences: JSON string of user preferences
        api_key: Optional API key for programmatic access
    """
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Subscription management
    subscription_tier = Column(
        String(50),
        default='free',
        nullable=False
    )  # free, creator, professional, business, enterprise
    subscription_status = Column(
        String(50),
        default='active',
        nullable=False
    )  # active, canceled, expired, trial
    subscription_start = Column(DateTime, nullable=True)
    subscription_end = Column(DateTime, nullable=True)
    
    # Credits system
    credits = Column(Float, default=100.0, nullable=False)  # Free credits for new users
    credits_used = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # API access
    api_key = Column(String(255), unique=True, nullable=True, index=True)
    
    # User preferences (stored as JSON string)
    preferences = Column(Text, nullable=True)  # JSON string
    
    # Email verification
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    
    # Password reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive fields)."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "website": self.website,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_admin": self.is_admin,
            "subscription_tier": self.subscription_tier,
            "subscription_status": self.subscription_status,
            "credits": self.credits,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
    
    def has_credits(self, amount: float) -> bool:
        """Check if user has sufficient credits."""
        return self.credits >= amount
    
    def deduct_credits(self, amount: float) -> bool:
        """
        Deduct credits from user account.
        
        Returns:
            True if successful, False if insufficient credits
        """
        if self.credits >= amount:
            self.credits -= amount
            self.credits_used += amount
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def add_credits(self, amount: float):
        """Add credits to user account."""
        self.credits += amount
        self.updated_at = datetime.utcnow()
    
    def is_subscription_active(self) -> bool:
        """Check if user has an active subscription."""
        if self.subscription_status != 'active':
            return False
        
        if self.subscription_end and self.subscription_end < datetime.utcnow():
            return False
        
        return True
    
    def get_subscription_tier_limits(self) -> dict:
        """
        Get limits based on subscription tier.
        
        Returns dict with limits for various features.
        """
        tier_limits = {
            'free': {
                'credits_per_month': 100,
                'max_projects': 3,
                'api_calls_per_day': 100,
                'storage_gb': 1,
                'team_members': 1
            },
            'creator': {
                'credits_per_month': 1000,
                'max_projects': 10,
                'api_calls_per_day': 1000,
                'storage_gb': 10,
                'team_members': 1
            },
            'professional': {
                'credits_per_month': 5000,
                'max_projects': 50,
                'api_calls_per_day': 10000,
                'storage_gb': 100,
                'team_members': 5
            },
            'business': {
                'credits_per_month': 25000,
                'max_projects': 200,
                'api_calls_per_day': 100000,
                'storage_gb': 500,
                'team_members': 20
            },
            'enterprise': {
                'credits_per_month': -1,  # Unlimited
                'max_projects': -1,
                'api_calls_per_day': -1,
                'storage_gb': -1,
                'team_members': -1
            }
        }
        
        return tier_limits.get(self.subscription_tier, tier_limits['free'])
