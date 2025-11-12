-- Migration: Add Age Verification and Subscription System
-- Created: November 9, 2025
-- Purpose: Add 18+ age verification, badge system, and subscription tiers

-- ============================================================================
-- 1. ADD AGE VERIFICATION TO USERS TABLE
-- ============================================================================

ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS date_of_birth DATE,
ADD COLUMN IF NOT EXISTS age_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS age_verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS is_adult BOOLEAN GENERATED ALWAYS AS (
    CASE 
        WHEN date_of_birth IS NOT NULL AND 
             date_of_birth <= CURRENT_DATE - INTERVAL '18 years' 
        THEN TRUE 
        ELSE FALSE 
    END
) STORED;

-- Add check constraint to ensure users are 18+
ALTER TABLE public.users 
ADD CONSTRAINT check_minimum_age 
CHECK (date_of_birth IS NULL OR date_of_birth <= CURRENT_DATE - INTERVAL '18 years');

-- ============================================================================
-- 2. CREATE SUBSCRIPTION PLANS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    badge_name VARCHAR(50) NOT NULL UNIQUE,
    badge_icon VARCHAR(50),
    badge_color VARCHAR(20),
    price_monthly DECIMAL(10, 2) NOT NULL,
    price_yearly DECIMAL(10, 2),
    features JSONB NOT NULL DEFAULT '[]',
    limits JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 3. CREATE USER SUBSCRIPTIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES public.subscription_plans(id),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    -- Status: active, cancelled, expired, suspended, trial
    billing_cycle VARCHAR(20) NOT NULL DEFAULT 'monthly',
    -- Billing: monthly, yearly
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    payment_method VARCHAR(50),
    -- stripe, paypal, crypto, etc.
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    last_payment_at TIMESTAMP WITH TIME ZONE,
    next_billing_date DATE,
    auto_renew BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 4. CREATE PAYMENT HISTORY TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.payment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES public.user_subscriptions(id),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) NOT NULL,
    -- Status: succeeded, failed, pending, refunded
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    stripe_payment_intent_id VARCHAR(255),
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 5. CREATE USAGE TRACKING TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL,
    -- Type: ai_requests, voice_minutes, api_calls, storage_gb, etc.
    amount INT NOT NULL DEFAULT 1,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 6. ADD SUBSCRIPTION COLUMNS TO USERS TABLE
-- ============================================================================

ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS current_plan_id UUID REFERENCES public.subscription_plans(id),
ADD COLUMN IF NOT EXISTS badge_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(20) DEFAULT 'free';

-- ============================================================================
-- 7. CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_users_date_of_birth ON public.users(date_of_birth);
CREATE INDEX IF NOT EXISTS idx_users_is_adult ON public.users(is_adult);
CREATE INDEX IF NOT EXISTS idx_users_current_plan ON public.users(current_plan_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON public.user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON public.user_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_expires_at ON public.user_subscriptions(expires_at);
CREATE INDEX IF NOT EXISTS idx_payment_history_user_id ON public.payment_history(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_period ON public.usage_tracking(user_id, period_start, period_end);

-- ============================================================================
-- 8. INSERT SUBSCRIPTION PLANS (BADGE TIERS)
-- ============================================================================

INSERT INTO public.subscription_plans (name, display_name, badge_name, badge_icon, badge_color, price_monthly, price_yearly, features, limits, sort_order)
VALUES 
    -- FREE TIER (Explorer Badge)
    (
        'free',
        'Free Explorer',
        'Explorer',
        '🆓',
        '#6B7280',
        0.00,
        0.00,
        '[
            "Basic AI chat access",
            "5 AI requests per day",
            "Community support",
            "Standard response time",
            "Public workspace"
        ]'::jsonb,
        '{
            "ai_requests_per_day": 5,
            "ai_requests_per_month": 150,
            "voice_minutes_per_month": 0,
            "api_calls_per_month": 0,
            "storage_gb": 1,
            "max_projects": 1,
            "can_use_voice": false,
            "can_use_api": false,
            "priority_support": false,
            "custom_models": false
        }'::jsonb,
        1
    ),
    
    -- STARTER TIER (Pioneer Badge) - $9.99/month
    (
        'starter',
        'Starter Pioneer',
        'Pioneer',
        '🌟',
        '#3B82F6',
        9.99,
        99.90,
        '[
            "Everything in Free",
            "100 AI requests per day",
            "Basic voice chat (30 min/month)",
            "Priority queue",
            "Email support",
            "5GB storage",
            "Up to 5 projects"
        ]'::jsonb,
        '{
            "ai_requests_per_day": 100,
            "ai_requests_per_month": 3000,
            "voice_minutes_per_month": 30,
            "api_calls_per_month": 100,
            "storage_gb": 5,
            "max_projects": 5,
            "can_use_voice": true,
            "can_use_api": false,
            "priority_support": false,
            "custom_models": false
        }'::jsonb,
        2
    ),
    
    -- PRO TIER (Master Badge) - $19.99/month
    (
        'pro',
        'Pro Master',
        'Master',
        '⚡',
        '#8B5CF6',
        19.99,
        199.90,
        '[
            "Everything in Starter",
            "Unlimited AI requests",
            "Unlimited voice chat",
            "API access (10k calls/month)",
            "Priority support (24h response)",
            "50GB storage",
            "Unlimited projects",
            "Advanced AI models",
            "Custom training data"
        ]'::jsonb,
        '{
            "ai_requests_per_day": -1,
            "ai_requests_per_month": -1,
            "voice_minutes_per_month": -1,
            "api_calls_per_month": 10000,
            "storage_gb": 50,
            "max_projects": -1,
            "can_use_voice": true,
            "can_use_api": true,
            "priority_support": true,
            "custom_models": true
        }'::jsonb,
        3
    ),
    
    -- ELITE TIER (Legend Badge) - $49.99/month
    (
        'elite',
        'Elite Legend',
        'Legend',
        '👑',
        '#F59E0B',
        49.99,
        499.90,
        '[
            "Everything in Pro",
            "Priority AI processing",
            "Dedicated support (1h response)",
            "100k API calls/month",
            "200GB storage",
            "White-label options",
            "Custom AI model training",
            "Team collaboration (5 seats)",
            "Advanced analytics",
            "Early access to new features"
        ]'::jsonb,
        '{
            "ai_requests_per_day": -1,
            "ai_requests_per_month": -1,
            "voice_minutes_per_month": -1,
            "api_calls_per_month": 100000,
            "storage_gb": 200,
            "max_projects": -1,
            "team_seats": 5,
            "can_use_voice": true,
            "can_use_api": true,
            "priority_support": true,
            "custom_models": true,
            "white_label": true,
            "dedicated_support": true
        }'::jsonb,
        4
    ),
    
    -- ENTERPRISE TIER (Titan Badge) - $99.99/month
    (
        'enterprise',
        'Enterprise Titan',
        'Titan',
        '💎',
        '#EF4444',
        99.99,
        999.90,
        '[
            "Everything in Elite",
            "Highest priority processing",
            "Dedicated account manager",
            "Unlimited API calls",
            "1TB storage",
            "Unlimited team seats",
            "Custom integrations",
            "On-premise deployment option",
            "SLA guarantee (99.9% uptime)",
            "Custom contracts",
            "White-glove onboarding",
            "Quarterly business reviews"
        ]'::jsonb,
        '{
            "ai_requests_per_day": -1,
            "ai_requests_per_month": -1,
            "voice_minutes_per_month": -1,
            "api_calls_per_month": -1,
            "storage_gb": 1000,
            "max_projects": -1,
            "team_seats": -1,
            "can_use_voice": true,
            "can_use_api": true,
            "priority_support": true,
            "custom_models": true,
            "white_label": true,
            "dedicated_support": true,
            "account_manager": true,
            "sla_guarantee": true,
            "on_premise": true
        }'::jsonb,
        5
    )
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- 9. CREATE FUNCTION TO CHECK USER AGE
-- ============================================================================

CREATE OR REPLACE FUNCTION check_user_age_requirement(user_dob DATE)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if user is at least 18 years old
    IF user_dob IS NULL THEN
        RETURN FALSE;
    END IF;
    
    IF user_dob <= CURRENT_DATE - INTERVAL '18 years' THEN
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- 10. CREATE FUNCTION TO UPDATE SUBSCRIPTION STATUS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_user_subscription_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Update user's current plan and badge when subscription changes
    IF NEW.status = 'active' THEN
        UPDATE public.users 
        SET 
            current_plan_id = NEW.plan_id,
            badge_name = (SELECT badge_name FROM public.subscription_plans WHERE id = NEW.plan_id),
            subscription_status = 'active'
        WHERE id = NEW.user_id;
    ELSIF NEW.status IN ('cancelled', 'expired', 'suspended') THEN
        UPDATE public.users 
        SET 
            subscription_status = NEW.status
        WHERE id = NEW.user_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS trigger_update_user_subscription ON public.user_subscriptions;
CREATE TRIGGER trigger_update_user_subscription
    AFTER INSERT OR UPDATE ON public.user_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_user_subscription_status();

-- ============================================================================
-- 11. CREATE FUNCTION TO TRACK USAGE
-- ============================================================================

CREATE OR REPLACE FUNCTION track_resource_usage(
    p_user_id UUID,
    p_resource_type VARCHAR,
    p_amount INT DEFAULT 1
)
RETURNS VOID AS $$
DECLARE
    v_period_start DATE;
    v_period_end DATE;
BEGIN
    -- Calculate current billing period (monthly)
    v_period_start := DATE_TRUNC('month', CURRENT_DATE);
    v_period_end := DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month' - INTERVAL '1 day';
    
    -- Insert or update usage record
    INSERT INTO public.usage_tracking (user_id, resource_type, amount, period_start, period_end)
    VALUES (p_user_id, p_resource_type, p_amount, v_period_start, v_period_end)
    ON CONFLICT ON CONSTRAINT usage_tracking_pkey
    DO UPDATE SET amount = usage_tracking.amount + p_amount;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 12. CREATE VIEW FOR CURRENT ACTIVE SUBSCRIPTIONS
-- ============================================================================

CREATE OR REPLACE VIEW public.v_active_subscriptions AS
SELECT 
    us.id,
    us.user_id,
    u.email,
    u.name,
    us.plan_id,
    sp.name AS plan_name,
    sp.display_name AS plan_display_name,
    sp.badge_name,
    sp.badge_icon,
    sp.badge_color,
    us.status,
    us.billing_cycle,
    us.started_at,
    us.expires_at,
    us.next_billing_date,
    CASE 
        WHEN us.expires_at > CURRENT_TIMESTAMP THEN TRUE
        ELSE FALSE
    END AS is_valid,
    EXTRACT(DAYS FROM (us.expires_at - CURRENT_TIMESTAMP)) AS days_remaining
FROM public.user_subscriptions us
JOIN public.users u ON us.user_id = u.id
JOIN public.subscription_plans sp ON us.plan_id = sp.id
WHERE us.status = 'active';

-- ============================================================================
-- 13. COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE public.subscription_plans IS 'Available subscription tiers with badge names and pricing';
COMMENT ON TABLE public.user_subscriptions IS 'User subscription records tracking current and past subscriptions';
COMMENT ON TABLE public.payment_history IS 'Payment transaction history for auditing and billing';
COMMENT ON TABLE public.usage_tracking IS 'Resource usage tracking for billing and limits enforcement';

COMMENT ON COLUMN public.users.date_of_birth IS 'User date of birth for 18+ age verification';
COMMENT ON COLUMN public.users.is_adult IS 'Computed column: TRUE if user is 18 or older';
COMMENT ON COLUMN public.users.badge_name IS 'Current subscription badge name (Explorer, Pioneer, Master, Legend, Titan)';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

