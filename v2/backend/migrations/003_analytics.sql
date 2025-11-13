-- ===============================================
-- NexusLang v2 Analytics Database Schema
-- ===============================================
-- Comprehensive analytics tracking for all platform activity
--
-- Features:
-- - Real-time event tracking
-- - Aggregated metrics
-- - User session tracking
-- - AI usage monitoring
-- - Performance metrics
-- - Cost tracking

-- Create analytics schema for organization
CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant permissions
GRANT ALL ON SCHEMA analytics TO nexus;

-- ===============================================
-- 1. Events Table - Raw event stream
-- ===============================================
CREATE TABLE IF NOT EXISTS analytics.events (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Event classification
    event_type VARCHAR(100) NOT NULL,  -- e.g., 'user_registered', 'ai_query', 'code_executed'
    category VARCHAR(50) NOT NULL,      -- e.g., 'auth', 'ai', 'ide', 'community'
    
    -- Event source
    user_id UUID,                       -- User who triggered event (NULL for anonymous)
    session_id UUID,                    -- Session ID for tracking user flows
    service VARCHAR(50) NOT NULL,       -- Service that generated event
    
    -- Request details
    ip_address INET,                    -- Client IP address
    user_agent TEXT,                    -- Browser/client info
    endpoint VARCHAR(255),              -- API endpoint called
    http_method VARCHAR(10),            -- GET, POST, etc.
    
    -- Event data
    data JSONB NOT NULL DEFAULT '{}',   -- Event-specific data
    
    -- Metadata
    severity VARCHAR(20) DEFAULT 'info', -- info, warning, error, critical
    success BOOLEAN DEFAULT true,        -- Whether operation succeeded
    error_message TEXT,                  -- Error details if failed
    
    -- Timing
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processing_time_ms INTEGER,         -- Time to process request
    
    -- Indexing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_events_user_id ON analytics.events(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_events_type ON analytics.events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_category ON analytics.events(category);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON analytics.events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_session ON analytics.events(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_events_severity ON analytics.events(severity) WHERE severity != 'info';
CREATE INDEX IF NOT EXISTS idx_events_data_gin ON analytics.events USING GIN(data); -- For JSON queries

-- ===============================================
-- 2. User Sessions Table - Track user activity sessions
-- ===============================================
CREATE TABLE IF NOT EXISTS analytics.user_sessions (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- User info
    user_id UUID NOT NULL,
    
    -- Session details
    session_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_end TIMESTAMPTZ,
    duration_seconds INTEGER,
    
    -- Session metadata
    ip_address INET,
    user_agent TEXT,
    device_type VARCHAR(50),           -- desktop, mobile, tablet
    browser VARCHAR(50),
    os VARCHAR(50),
    
    -- Activity metrics
    events_count INTEGER DEFAULT 0,
    api_calls_count INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    
    -- Session outcome
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    exit_type VARCHAR(50),             -- normal, timeout, error
    
    -- Indexing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON analytics.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_start ON analytics.user_sessions(session_start DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON analytics.user_sessions(session_end) WHERE session_end IS NULL;

-- ===============================================
-- 3. AI Usage Metrics - Track AI model usage and costs
-- ===============================================
CREATE TABLE IF NOT EXISTS analytics.ai_usage (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- User and session
    user_id UUID,
    session_id UUID,
    
    -- AI request details
    model VARCHAR(100) NOT NULL,       -- e.g., 'anthropic/claude-3.5-sonnet'
    provider VARCHAR(50) NOT NULL,     -- openrouter, openai, etc.
    request_type VARCHAR(50) NOT NULL, -- chat, completion, embedding, etc.
    
    -- Usage metrics
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    
    -- Cost tracking (in credits or USD cents)
    estimated_cost_credits INTEGER DEFAULT 0,
    estimated_cost_usd DECIMAL(10, 6) DEFAULT 0,
    
    -- Performance
    response_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    
    -- Request/response samples (for debugging, limited size)
    prompt_sample TEXT,                -- First 500 chars of prompt
    response_sample TEXT,              -- First 500 chars of response
    
    -- Timing
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ai_usage_user ON analytics.ai_usage(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ai_usage_model ON analytics.ai_usage(model);
CREATE INDEX IF NOT EXISTS idx_ai_usage_timestamp ON analytics.ai_usage(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ai_usage_cost ON analytics.ai_usage(estimated_cost_credits DESC);

-- ===============================================
-- 4. API Performance Metrics - Response times and errors
-- ===============================================
CREATE TABLE IF NOT EXISTS analytics.api_performance (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Endpoint info
    endpoint VARCHAR(255) NOT NULL,
    http_method VARCHAR(10) NOT NULL,
    
    -- Performance metrics
    response_time_ms INTEGER NOT NULL,
    status_code INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    
    -- Error tracking
    error_type VARCHAR(100),
    error_message TEXT,
    
    -- User context
    user_id UUID,
    authenticated BOOLEAN DEFAULT false,
    
    -- Aggregation period (for pre-aggregated metrics)
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    request_count INTEGER DEFAULT 1,   -- For aggregated records
    
    -- Timing
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_api_perf_endpoint ON analytics.api_performance(endpoint, http_method);
CREATE INDEX IF NOT EXISTS idx_api_perf_timestamp ON analytics.api_performance(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_perf_errors ON analytics.api_performance(success) WHERE success = false;
CREATE INDEX IF NOT EXISTS idx_api_perf_slow ON analytics.api_performance(response_time_ms DESC);

-- ===============================================
-- 5. Usage Metrics - Aggregated daily/hourly statistics
-- ===============================================
CREATE TABLE IF NOT EXISTS analytics.usage_metrics (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Time period
    metric_date DATE NOT NULL,
    metric_hour INTEGER,               -- NULL for daily metrics, 0-23 for hourly
    
    -- User metrics
    total_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,    -- Users who logged in
    new_users INTEGER DEFAULT 0,       -- New registrations
    
    -- Activity metrics
    total_sessions INTEGER DEFAULT 0,
    total_api_calls INTEGER DEFAULT 0,
    total_events INTEGER DEFAULT 0,
    
    -- AI metrics
    total_ai_queries INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    total_ai_cost_credits INTEGER DEFAULT 0,
    
    -- Feature usage
    code_executions INTEGER DEFAULT 0,
    files_created INTEGER DEFAULT 0,
    projects_created INTEGER DEFAULT 0,
    
    -- Performance
    avg_response_time_ms INTEGER,
    error_rate DECIMAL(5, 4),          -- Percentage of failed requests
    
    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Unique constraint for aggregation periods
    UNIQUE(metric_date, metric_hour)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_usage_metrics_date ON analytics.usage_metrics(metric_date DESC);
CREATE INDEX IF NOT EXISTS idx_usage_metrics_hour ON analytics.usage_metrics(metric_date DESC, metric_hour DESC NULLS LAST);

-- ===============================================
-- 6. Feature Usage Tracking - Which features are used
-- ===============================================
CREATE TABLE IF NOT EXISTS analytics.feature_usage (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Feature identification
    feature_name VARCHAR(100) NOT NULL, -- e.g., 'ide_code_editor', 'grokopedia_search'
    feature_category VARCHAR(50) NOT NULL, -- ide, ai, community, billing, etc.
    
    -- Usage metrics
    user_id UUID,
    session_id UUID,
    
    -- Usage details
    action VARCHAR(50),                -- opened, closed, used, clicked, etc.
    duration_seconds INTEGER,          -- How long feature was used
    metadata JSONB DEFAULT '{}',       -- Feature-specific data
    
    -- Success tracking
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    
    -- Timing
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_feature_usage_name ON analytics.feature_usage(feature_name);
CREATE INDEX IF NOT EXISTS idx_feature_usage_user ON analytics.feature_usage(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_feature_usage_timestamp ON analytics.feature_usage(timestamp DESC);

-- ===============================================
-- 7. Error Tracking - Centralized error logging
-- ===============================================
CREATE TABLE IF NOT EXISTS analytics.errors (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Error classification
    error_type VARCHAR(100) NOT NULL,  -- 500, 404, validation_error, etc.
    error_code VARCHAR(50),
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    
    -- Context
    user_id UUID,
    session_id UUID,
    endpoint VARCHAR(255),
    http_method VARCHAR(10),
    
    -- Request data
    request_body JSONB,
    request_headers JSONB,
    
    -- Environment
    service VARCHAR(50),
    environment VARCHAR(20) DEFAULT 'production',
    
    -- Severity
    severity VARCHAR(20) DEFAULT 'error', -- warning, error, critical
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMPTZ,
    
    -- Timing
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_errors_type ON analytics.errors(error_type);
CREATE INDEX IF NOT EXISTS idx_errors_timestamp ON analytics.errors(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_errors_user ON analytics.errors(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_errors_unresolved ON analytics.errors(resolved) WHERE resolved = false;
CREATE INDEX IF NOT EXISTS idx_errors_severity ON analytics.errors(severity) WHERE severity IN ('error', 'critical');

-- ===============================================
-- 8. System Health Metrics - Infrastructure monitoring
-- ===============================================
CREATE TABLE IF NOT EXISTS analytics.system_health (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Component
    component VARCHAR(50) NOT NULL,    -- api, database, redis, etc.
    
    -- Health status
    status VARCHAR(20) NOT NULL,       -- healthy, degraded, down
    
    -- Metrics
    cpu_usage DECIMAL(5, 2),           -- Percentage
    memory_usage DECIMAL(5, 2),        -- Percentage  
    disk_usage DECIMAL(5, 2),          -- Percentage
    
    -- Component-specific metrics
    metrics JSONB DEFAULT '{}',        -- Additional metrics
    
    -- Response time
    response_time_ms INTEGER,
    
    -- Details
    message TEXT,
    details JSONB DEFAULT '{}',
    
    -- Timing
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_health_component ON analytics.system_health(component);
CREATE INDEX IF NOT EXISTS idx_health_timestamp ON analytics.system_health(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_health_status ON analytics.system_health(status) WHERE status != 'healthy';

-- ===============================================
-- Helper Views for Common Queries
-- ===============================================

-- Daily active users
CREATE OR REPLACE VIEW analytics.daily_active_users AS
SELECT 
    DATE(timestamp) as date,
    COUNT(DISTINCT user_id) as active_users
FROM analytics.events
WHERE user_id IS NOT NULL
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- AI usage summary by model
CREATE OR REPLACE VIEW analytics.ai_usage_by_model AS
SELECT 
    model,
    COUNT(*) as queries,
    SUM(total_tokens) as total_tokens,
    SUM(estimated_cost_credits) as total_cost_credits,
    AVG(response_time_ms) as avg_response_time_ms,
    SUM(CASE WHEN success THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as success_rate
FROM analytics.ai_usage
GROUP BY model
ORDER BY queries DESC;

-- Error summary by type
CREATE OR REPLACE VIEW analytics.error_summary AS
SELECT 
    error_type,
    COUNT(*) as occurrences,
    COUNT(DISTINCT user_id) as affected_users,
    MAX(timestamp) as last_occurrence,
    SUM(CASE WHEN resolved THEN 1 ELSE 0 END) as resolved_count
FROM analytics.errors
GROUP BY error_type
ORDER BY occurrences DESC;

-- Feature popularity
CREATE OR REPLACE VIEW analytics.feature_popularity AS
SELECT 
    feature_name,
    feature_category,
    COUNT(*) as usage_count,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(duration_seconds) as avg_duration_seconds,
    SUM(CASE WHEN success THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as success_rate
FROM analytics.feature_usage
GROUP BY feature_name, feature_category
ORDER BY usage_count DESC;

-- ===============================================
-- Functions for Analytics Aggregation
-- ===============================================

-- Function to aggregate daily metrics
CREATE OR REPLACE FUNCTION analytics.aggregate_daily_metrics(target_date DATE)
RETURNS void AS $$
BEGIN
    -- Insert or update daily metrics
    INSERT INTO analytics.usage_metrics (
        metric_date,
        metric_hour,
        total_users,
        active_users,
        new_users,
        total_sessions,
        total_api_calls,
        total_events,
        total_ai_queries,
        total_tokens_used,
        total_ai_cost_credits,
        code_executions,
        files_created,
        projects_created,
        avg_response_time_ms,
        error_rate
    )
    SELECT
        target_date,
        NULL,
        -- User metrics
        (SELECT COUNT(*) FROM users WHERE DATE(created_at) <= target_date),
        (SELECT COUNT(DISTINCT user_id) FROM analytics.events WHERE DATE(timestamp) = target_date),
        (SELECT COUNT(*) FROM users WHERE DATE(created_at) = target_date),
        -- Activity metrics
        (SELECT COUNT(DISTINCT session_id) FROM analytics.events WHERE DATE(timestamp) = target_date),
        (SELECT COUNT(*) FROM analytics.api_performance WHERE DATE(timestamp) = target_date),
        (SELECT COUNT(*) FROM analytics.events WHERE DATE(timestamp) = target_date),
        -- AI metrics
        (SELECT COUNT(*) FROM analytics.ai_usage WHERE DATE(timestamp) = target_date),
        (SELECT COALESCE(SUM(total_tokens), 0) FROM analytics.ai_usage WHERE DATE(timestamp) = target_date),
        (SELECT COALESCE(SUM(estimated_cost_credits), 0) FROM analytics.ai_usage WHERE DATE(timestamp) = target_date),
        -- Feature usage
        (SELECT COUNT(*) FROM analytics.events WHERE event_type = 'code_executed' AND DATE(timestamp) = target_date),
        (SELECT COUNT(*) FROM analytics.events WHERE event_type = 'file_created' AND DATE(timestamp) = target_date),
        (SELECT COUNT(*) FROM analytics.events WHERE event_type = 'project_created' AND DATE(timestamp) = target_date),
        -- Performance
        (SELECT AVG(response_time_ms)::INTEGER FROM analytics.api_performance WHERE DATE(timestamp) = target_date),
        (SELECT (SUM(CASE WHEN success = false THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0)) 
         FROM analytics.api_performance WHERE DATE(timestamp) = target_date)
    ON CONFLICT (metric_date, metric_hour) DO UPDATE SET
        total_users = EXCLUDED.total_users,
        active_users = EXCLUDED.active_users,
        new_users = EXCLUDED.new_users,
        total_sessions = EXCLUDED.total_sessions,
        total_api_calls = EXCLUDED.total_api_calls,
        total_events = EXCLUDED.total_events,
        total_ai_queries = EXCLUDED.total_ai_queries,
        total_tokens_used = EXCLUDED.total_tokens_used,
        total_ai_cost_credits = EXCLUDED.total_ai_cost_credits,
        code_executions = EXCLUDED.code_executions,
        files_created = EXCLUDED.files_created,
        projects_created = EXCLUDED.projects_created,
        avg_response_time_ms = EXCLUDED.avg_response_time_ms,
        error_rate = EXCLUDED.error_rate,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ===============================================
-- Trigger to auto-update session metrics
-- ===============================================
CREATE OR REPLACE FUNCTION analytics.update_session_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update session with new event
    UPDATE analytics.user_sessions
    SET 
        events_count = events_count + 1,
        last_activity = NEW.timestamp
    WHERE id = NEW.session_id AND session_end IS NULL;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_session_metrics
AFTER INSERT ON analytics.events
FOR EACH ROW
WHEN (NEW.session_id IS NOT NULL)
EXECUTE FUNCTION analytics.update_session_metrics();

-- ===============================================
-- Grants
-- ===============================================
GRANT ALL ON ALL TABLES IN SCHEMA analytics TO nexus;
GRANT ALL ON ALL SEQUENCES IN SCHEMA analytics TO nexus;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA analytics TO nexus;

-- ===============================================
-- Initial Data / Test Events
-- ===============================================
-- Insert a system startup event
INSERT INTO analytics.events (
    event_type,
    category,
    service,
    data,
    severity
) VALUES (
    'system_initialized',
    'system',
    'backend',
    '{"message": "Analytics system initialized", "version": "2.0.0-beta"}'::jsonb,
    'info'
);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Analytics schema created successfully!';
    RAISE NOTICE '   - 8 tables created';
    RAISE NOTICE '   - 4 views created';
    RAISE NOTICE '   - Indexes optimized for fast queries';
    RAISE NOTICE '   - Ready to track platform analytics';
END $$;

