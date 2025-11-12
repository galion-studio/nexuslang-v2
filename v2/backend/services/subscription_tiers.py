"""
Subscription Tier Management
Handles tier limits, feature access, and usage tracking
"""

from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass

class SubscriptionTier(str, Enum):
    """Subscription tier levels"""
    FREE_TRIAL = "free_trial"
    CREATOR = "creator"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    
    # Developer Platform tiers
    DEV_FREE = "dev_free"
    DEV_PRO = "dev_pro"
    DEV_BUSINESS = "dev_business"
    DEV_ENTERPRISE = "dev_enterprise"


@dataclass
class TierLimits:
    """Usage limits for each tier"""
    # Studio limits (monthly)
    image_generations: int
    video_generations: int
    text_generations: int
    nexuslang_runs: int
    voice_generations: int
    ai_upscaling: int
    background_removal: int
    model_3d_generations: int
    
    # Platform limits (rate limiting)
    api_requests_per_minute: int
    api_requests_per_day: int
    
    # Feature access
    has_watermark: bool
    has_commercial_license: bool
    has_api_access: bool
    has_priority_queue: bool
    has_premium_models: bool
    has_voice_cloning: bool
    has_team_seats: int
    has_white_label: bool
    has_custom_training: bool
    
    # Support level
    support_level: str  # "community", "email", "priority", "dedicated"
    support_response_time: str  # "none", "48h", "24h", "12h", "immediate"
    
    # Overage pricing (per unit in cents)
    overage_cost_cents: int


# Define tier limits
TIER_LIMITS: Dict[SubscriptionTier, TierLimits] = {
    # Galion Studio Tiers
    SubscriptionTier.FREE_TRIAL: TierLimits(
        image_generations=20,
        video_generations=10,
        text_generations=50,
        nexuslang_runs=100,
        voice_generations=0,
        ai_upscaling=0,
        background_removal=0,
        model_3d_generations=0,
        api_requests_per_minute=10,
        api_requests_per_day=1000,
        has_watermark=True,
        has_commercial_license=False,
        has_api_access=False,
        has_priority_queue=False,
        has_premium_models=False,
        has_voice_cloning=False,
        has_team_seats=1,
        has_white_label=False,
        has_custom_training=False,
        support_level="community",
        support_response_time="none",
        overage_cost_cents=0  # Cannot exceed trial limits
    ),
    
    SubscriptionTier.CREATOR: TierLimits(
        image_generations=200,
        video_generations=50,
        text_generations=500,
        nexuslang_runs=1000,
        voice_generations=100,
        ai_upscaling=50,
        background_removal=100,
        model_3d_generations=0,
        api_requests_per_minute=100,
        api_requests_per_day=10000,
        has_watermark=False,
        has_commercial_license=True,
        has_api_access=True,
        has_priority_queue=True,
        has_premium_models=False,
        has_voice_cloning=False,
        has_team_seats=1,
        has_white_label=False,
        has_custom_training=False,
        support_level="email",
        support_response_time="48h",
        overage_cost_cents=10  # $0.10 per generation
    ),
    
    SubscriptionTier.PROFESSIONAL: TierLimits(
        image_generations=1000,
        video_generations=200,
        text_generations=2000,
        nexuslang_runs=10000,
        voice_generations=500,
        ai_upscaling=999999,  # Unlimited
        background_removal=999999,
        model_3d_generations=50,
        api_requests_per_minute=500,
        api_requests_per_day=50000,
        has_watermark=False,
        has_commercial_license=True,
        has_api_access=True,
        has_priority_queue=True,
        has_premium_models=True,
        has_voice_cloning=True,
        has_team_seats=3,
        has_white_label=False,
        has_custom_training=False,
        support_level="priority",
        support_response_time="24h",
        overage_cost_cents=8  # $0.08 per generation
    ),
    
    SubscriptionTier.BUSINESS: TierLimits(
        image_generations=10000,
        video_generations=2000,
        text_generations=20000,
        nexuslang_runs=999999,  # Unlimited
        voice_generations=5000,
        ai_upscaling=999999,
        background_removal=999999,
        model_3d_generations=999999,
        api_requests_per_minute=2000,
        api_requests_per_day=200000,
        has_watermark=False,
        has_commercial_license=True,
        has_api_access=True,
        has_priority_queue=True,
        has_premium_models=True,
        has_voice_cloning=True,
        has_team_seats=10,
        has_white_label=True,
        has_custom_training=True,
        support_level="dedicated",
        support_response_time="12h",
        overage_cost_cents=5  # $0.05 per generation
    ),
    
    # Developer Platform Tiers
    SubscriptionTier.DEV_FREE: TierLimits(
        image_generations=0,  # Pay-per-use
        video_generations=0,
        text_generations=0,
        nexuslang_runs=0,
        voice_generations=0,
        ai_upscaling=0,
        background_removal=0,
        model_3d_generations=0,
        api_requests_per_minute=100,
        api_requests_per_day=10000,
        has_watermark=False,
        has_commercial_license=True,
        has_api_access=True,
        has_priority_queue=False,
        has_premium_models=True,
        has_voice_cloning=False,
        has_team_seats=1,
        has_white_label=False,
        has_custom_training=False,
        support_level="community",
        support_response_time="none",
        overage_cost_cents=0  # Pay-per-use
    ),
    
    SubscriptionTier.DEV_PRO: TierLimits(
        image_generations=0,  # Credits included
        video_generations=0,
        text_generations=0,
        nexuslang_runs=0,
        voice_generations=0,
        ai_upscaling=0,
        background_removal=0,
        model_3d_generations=0,
        api_requests_per_minute=500,
        api_requests_per_day=50000,
        has_watermark=False,
        has_commercial_license=True,
        has_api_access=True,
        has_priority_queue=True,
        has_premium_models=True,
        has_voice_cloning=True,
        has_team_seats=3,
        has_white_label=False,
        has_custom_training=False,
        support_level="priority",
        support_response_time="24h",
        overage_cost_cents=0  # Pay-per-use
    ),
    
    SubscriptionTier.DEV_BUSINESS: TierLimits(
        image_generations=0,
        video_generations=0,
        text_generations=0,
        nexuslang_runs=0,
        voice_generations=0,
        ai_upscaling=0,
        background_removal=0,
        model_3d_generations=0,
        api_requests_per_minute=2000,
        api_requests_per_day=200000,
        has_watermark=False,
        has_commercial_license=True,
        has_api_access=True,
        has_priority_queue=True,
        has_premium_models=True,
        has_voice_cloning=True,
        has_team_seats=5,
        has_white_label=False,
        has_custom_training=False,
        support_level="dedicated",
        support_response_time="12h",
        overage_cost_cents=0  # Pay-per-use
    )
}


def get_tier_limits(tier: SubscriptionTier) -> TierLimits:
    """Get limits for a subscription tier"""
    return TIER_LIMITS.get(tier, TIER_LIMITS[SubscriptionTier.FREE_TRIAL])


def can_perform_action(
    tier: SubscriptionTier,
    action: str,
    current_usage: Dict[str, int]
) -> tuple[bool, Optional[str]]:
    """
    Check if user can perform an action based on tier limits.
    
    Args:
        tier: User's subscription tier
        action: Action to perform (e.g., "image_generation")
        current_usage: Dict of current month's usage
        
    Returns:
        (can_perform, reason_if_not)
    """
    limits = get_tier_limits(tier)
    
    # Map action to limit attribute
    action_to_limit = {
        "image_generation": limits.image_generations,
        "video_generation": limits.video_generations,
        "text_generation": limits.text_generations,
        "nexuslang_run": limits.nexuslang_runs,
        "voice_generation": limits.voice_generations,
        "ai_upscaling": limits.ai_upscaling,
        "background_removal": limits.background_removal,
        "model_3d_generation": limits.model_3d_generations
    }
    
    if action not in action_to_limit:
        return True, None  # Unknown action, allow
    
    limit = action_to_limit[action]
    usage = current_usage.get(action, 0)
    
    # Unlimited = 999999
    if limit >= 999999:
        return True, None
    
    if usage >= limit:
        return False, f"Monthly limit reached ({limit}). Upgrade or buy credits."
    
    return True, None


def calculate_overage_cost(
    tier: SubscriptionTier,
    action: str,
    overage_count: int
) -> int:
    """
    Calculate cost for overage usage in cents.
    
    Returns:
        Cost in cents
    """
    limits = get_tier_limits(tier)
    return limits.overage_cost_cents * overage_count


def has_feature_access(tier: SubscriptionTier, feature: str) -> bool:
    """Check if tier has access to a feature"""
    limits = get_tier_limits(tier)
    
    feature_map = {
        "commercial_license": limits.has_commercial_license,
        "api_access": limits.has_api_access,
        "priority_queue": limits.has_priority_queue,
        "premium_models": limits.has_premium_models,
        "voice_cloning": limits.has_voice_cloning,
        "white_label": limits.has_white_label,
        "custom_training": limits.has_custom_training
    }
    
    return feature_map.get(feature, False)


# Credit pricing for Developer Platform (pay-per-use)
CREDIT_COSTS = {
    "nexuslang_execution": 1,
    "image_sd": 5,
    "image_dalle": 10,
    "video_5s": 20,
    "video_30s": 50,
    "text_claude_per_1k": 2,
    "text_gpt4_per_1k": 3,
    "text_gpt35_per_1k": 0.5,
    "voice_tts": 3,
    "voice_stt": 2,
    "ai_upscaling": 5,
    "background_removal": 3
}


def calculate_credit_cost(action: str, **kwargs) -> int:
    """
    Calculate credit cost for an API action.
    
    Args:
        action: Type of action
        **kwargs: Additional parameters (tokens, duration, etc.)
        
    Returns:
        Credits required
    """
    if action == "text_generation":
        model = kwargs.get("model", "gpt-3.5-turbo")
        tokens = kwargs.get("tokens", 1000)
        
        if "claude" in model:
            return int((tokens / 1000) * CREDIT_COSTS["text_claude_per_1k"])
        elif "gpt-4" in model:
            return int((tokens / 1000) * CREDIT_COSTS["text_gpt4_per_1k"])
        else:
            return int((tokens / 1000) * CREDIT_COSTS["text_gpt35_per_1k"])
    
    elif action == "video_generation":
        duration = kwargs.get("duration", 5)
        if duration <= 5:
            return CREDIT_COSTS["video_5s"]
        elif duration <= 30:
            return CREDIT_COSTS["video_30s"]
        else:
            return int((duration / 30) * CREDIT_COSTS["video_30s"])
    
    # Default costs
    return CREDIT_COSTS.get(action, 1)

