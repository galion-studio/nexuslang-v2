-- Migration 003: Content Manager System
-- Multi-brand social media management platform
-- Created: 2025-11-11

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- BRANDS TABLE
-- Manages multiple brands (Galion Studio, Galion App, Slavic Nomad, Marilyn Element)
-- ============================================================
CREATE TABLE IF NOT EXISTS brands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    logo_url VARCHAR(500),
    brand_color VARCHAR(7) DEFAULT '#000000',
    voice_guidelines TEXT,
    website_url VARCHAR(500),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for faster brand lookups
CREATE INDEX idx_brands_slug ON brands(slug);
CREATE INDEX idx_brands_active ON brands(is_active);

-- ============================================================
-- SOCIAL ACCOUNTS TABLE
-- Connected social media accounts per brand
-- ============================================================
CREATE TABLE IF NOT EXISTS social_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,  -- 'reddit', 'twitter', 'instagram', 'facebook', 'linkedin', 'tiktok', 'youtube', 'hackernews', 'producthunt', 'devto', 'generic_forum'
    account_name VARCHAR(200) NOT NULL,
    account_url VARCHAR(500),
    account_id VARCHAR(200),  -- Platform-specific user/page ID
    credentials JSONB,  -- Encrypted OAuth tokens and secrets
    platform_metadata JSONB,  -- Platform-specific settings (e.g., subreddit for Reddit, page_id for Facebook)
    is_active BOOLEAN DEFAULT true,
    last_synced TIMESTAMP,
    sync_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'active', 'error', 'expired'
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(brand_id, platform, account_name)
);

-- Create indexes for social accounts
CREATE INDEX idx_social_accounts_brand ON social_accounts(brand_id);
CREATE INDEX idx_social_accounts_platform ON social_accounts(platform);
CREATE INDEX idx_social_accounts_active ON social_accounts(is_active);

-- ============================================================
-- CONTENT POSTS TABLE
-- All content posts with multi-platform support
-- ============================================================
CREATE TABLE IF NOT EXISTS content_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    title VARCHAR(500),
    content TEXT NOT NULL,
    content_html TEXT,
    excerpt TEXT,  -- Short summary/preview
    media_urls JSONB DEFAULT '[]'::jsonb,  -- Array of media URLs [{url, type, alt}]
    platforms JSONB DEFAULT '[]'::jsonb,  -- Array of target platforms ['reddit', 'twitter', etc.]
    hashtags JSONB DEFAULT '[]'::jsonb,  -- Array of hashtags
    mentions JSONB DEFAULT '[]'::jsonb,  -- Array of mentions/tags
    metadata JSONB DEFAULT '{}'::jsonb,  -- Additional metadata (links, attachments, etc.)
    status VARCHAR(50) DEFAULT 'draft',  -- 'draft', 'scheduled', 'publishing', 'published', 'failed', 'archived'
    scheduled_at TIMESTAMP,
    published_at TIMESTAMP,
    failed_at TIMESTAMP,
    failure_reason TEXT,
    recurring_schedule JSONB,  -- For recurring posts: {frequency, interval, end_date}
    template_id UUID,  -- Reference to template if used
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMP,
    version INT DEFAULT 1,
    parent_post_id UUID REFERENCES content_posts(id),  -- For post variations
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for content posts
CREATE INDEX idx_content_posts_brand ON content_posts(brand_id);
CREATE INDEX idx_content_posts_status ON content_posts(status);
CREATE INDEX idx_content_posts_scheduled ON content_posts(scheduled_at) WHERE scheduled_at IS NOT NULL;
CREATE INDEX idx_content_posts_created_by ON content_posts(created_by);
CREATE INDEX idx_content_posts_template ON content_posts(template_id);

-- ============================================================
-- PLATFORM POSTS TABLE
-- Individual platform-specific posts (one content_post can have multiple platform_posts)
-- ============================================================
CREATE TABLE IF NOT EXISTS platform_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_post_id UUID NOT NULL REFERENCES content_posts(id) ON DELETE CASCADE,
    social_account_id UUID NOT NULL REFERENCES social_accounts(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(200),  -- External ID from platform (e.g., Reddit post ID)
    platform_url VARCHAR(500),  -- Direct URL to the post on the platform
    platform_content TEXT,  -- Platform-specific formatted content
    platform_metadata JSONB DEFAULT '{}'::jsonb,  -- Platform-specific data
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'posting', 'posted', 'failed', 'deleted'
    posted_at TIMESTAMP,
    failed_at TIMESTAMP,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    last_retry_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for platform posts
CREATE INDEX idx_platform_posts_content ON platform_posts(content_post_id);
CREATE INDEX idx_platform_posts_account ON platform_posts(social_account_id);
CREATE INDEX idx_platform_posts_platform ON platform_posts(platform);
CREATE INDEX idx_platform_posts_status ON platform_posts(status);
CREATE INDEX idx_platform_posts_platform_id ON platform_posts(platform_post_id);

-- ============================================================
-- POST ANALYTICS TABLE
-- Engagement metrics for platform posts
-- ============================================================
CREATE TABLE IF NOT EXISTS post_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_post_id UUID NOT NULL REFERENCES platform_posts(id) ON DELETE CASCADE,
    likes INT DEFAULT 0,
    comments INT DEFAULT 0,
    shares INT DEFAULT 0,
    views INT DEFAULT 0,
    clicks INT DEFAULT 0,
    saves INT DEFAULT 0,
    reach INT DEFAULT 0,  -- Unique users reached
    impressions INT DEFAULT 0,  -- Total views
    engagement_rate DECIMAL(5,2) DEFAULT 0.00,  -- Percentage
    platform_specific_metrics JSONB DEFAULT '{}'::jsonb,  -- Platform-specific metrics (karma for Reddit, retweets for Twitter, etc.)
    synced_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for analytics
CREATE INDEX idx_post_analytics_platform_post ON post_analytics(platform_post_id);
CREATE INDEX idx_post_analytics_synced ON post_analytics(synced_at);

-- ============================================================
-- CONTENT TEMPLATES TABLE
-- Reusable content templates per brand
-- ============================================================
CREATE TABLE IF NOT EXISTS content_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    template_content TEXT NOT NULL,
    template_variables JSONB DEFAULT '[]'::jsonb,  -- Variables that can be replaced: [{name, default, description}]
    platforms JSONB DEFAULT '[]'::jsonb,  -- Target platforms this template is optimized for
    tags JSONB DEFAULT '[]'::jsonb,  -- Categorization tags
    category VARCHAR(100),  -- 'announcement', 'promotion', 'engagement', 'educational', etc.
    use_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for templates
CREATE INDEX idx_content_templates_brand ON content_templates(brand_id);
CREATE INDEX idx_content_templates_category ON content_templates(category);
CREATE INDEX idx_content_templates_active ON content_templates(is_active);

-- ============================================================
-- TEAM PERMISSIONS TABLE
-- Role-based access control for content management
-- ============================================================
CREATE TABLE IF NOT EXISTS team_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,  -- NULL means all brands
    role VARCHAR(50) NOT NULL,  -- 'admin', 'editor', 'contributor', 'viewer'
    permissions JSONB DEFAULT '{}'::jsonb,  -- Granular permissions: {can_post, can_schedule, can_delete, can_approve, etc.}
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, brand_id)
);

-- Create indexes for team permissions
CREATE INDEX idx_team_permissions_user ON team_permissions(user_id);
CREATE INDEX idx_team_permissions_brand ON team_permissions(brand_id);
CREATE INDEX idx_team_permissions_role ON team_permissions(role);

-- ============================================================
-- POST COMMENTS TABLE
-- Team comments and feedback on draft posts
-- ============================================================
CREATE TABLE IF NOT EXISTS post_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_post_id UUID NOT NULL REFERENCES content_posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    parent_comment_id UUID REFERENCES post_comments(id) ON DELETE CASCADE,  -- For threaded comments
    is_resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for comments
CREATE INDEX idx_post_comments_post ON post_comments(content_post_id);
CREATE INDEX idx_post_comments_user ON post_comments(user_id);
CREATE INDEX idx_post_comments_parent ON post_comments(parent_comment_id);

-- ============================================================
-- ACTIVITY LOG TABLE
-- Audit trail for all content management actions
-- ============================================================
CREATE TABLE IF NOT EXISTS content_activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,  -- 'created', 'updated', 'deleted', 'published', 'scheduled', 'approved', etc.
    entity_type VARCHAR(50) NOT NULL,  -- 'content_post', 'template', 'social_account', 'brand', etc.
    entity_id UUID NOT NULL,
    changes JSONB DEFAULT '{}'::jsonb,  -- What changed: {field: {old, new}}
    metadata JSONB DEFAULT '{}'::jsonb,  -- Additional context
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for activity log
CREATE INDEX idx_activity_log_user ON content_activity_log(user_id);
CREATE INDEX idx_activity_log_entity ON content_activity_log(entity_type, entity_id);
CREATE INDEX idx_activity_log_created ON content_activity_log(created_at);

-- ============================================================
-- MEDIA ASSETS TABLE
-- Centralized media library
-- ============================================================
CREATE TABLE IF NOT EXISTS media_assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    file_type VARCHAR(50),  -- 'image', 'video', 'gif', 'document'
    mime_type VARCHAR(100),
    file_size_bytes BIGINT,
    width INT,
    height INT,
    duration_seconds INT,  -- For videos
    alt_text TEXT,
    description TEXT,
    tags JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    use_count INT DEFAULT 0,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for media assets
CREATE INDEX idx_media_assets_brand ON media_assets(brand_id);
CREATE INDEX idx_media_assets_type ON media_assets(file_type);
CREATE INDEX idx_media_assets_uploaded_by ON media_assets(uploaded_by);

-- ============================================================
-- N8N WEBHOOKS TABLE
-- N8n workflow integration tracking
-- ============================================================
CREATE TABLE IF NOT EXISTS n8n_webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    webhook_url VARCHAR(500) NOT NULL,
    webhook_method VARCHAR(10) DEFAULT 'POST',  -- 'POST', 'GET'
    trigger_event VARCHAR(100),  -- 'post_published', 'post_scheduled', 'analytics_synced', etc.
    is_active BOOLEAN DEFAULT true,
    last_triggered_at TIMESTAMP,
    success_count INT DEFAULT 0,
    failure_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for webhooks
CREATE INDEX idx_n8n_webhooks_active ON n8n_webhooks(is_active);
CREATE INDEX idx_n8n_webhooks_event ON n8n_webhooks(trigger_event);

-- ============================================================
-- SCHEDULED JOBS TABLE
-- Track scheduled posting jobs
-- ============================================================
CREATE TABLE IF NOT EXISTS scheduled_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_type VARCHAR(50) NOT NULL,  -- 'post_content', 'sync_analytics', 'refresh_tokens', etc.
    entity_type VARCHAR(50),
    entity_id UUID,
    scheduled_for TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    priority INT DEFAULT 5,  -- 1-10, higher = more priority
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    payload JSONB DEFAULT '{}'::jsonb,
    result JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for scheduled jobs
CREATE INDEX idx_scheduled_jobs_status ON scheduled_jobs(status);
CREATE INDEX idx_scheduled_jobs_scheduled ON scheduled_jobs(scheduled_for);
CREATE INDEX idx_scheduled_jobs_entity ON scheduled_jobs(entity_type, entity_id);

-- ============================================================
-- INSERT DEFAULT BRANDS
-- Pre-populate with the four brands
-- ============================================================
INSERT INTO brands (id, name, slug, brand_color, voice_guidelines, description, is_active) VALUES
(uuid_generate_v4(), 'Galion Studio', 'galion-studio', '#3B82F6', 
 'Professional, innovative, technical. Focus on AI development, transparency, and community building. Use clear technical language with a friendly tone.',
 'AI-native development platform building NexusLang and transparent workplace tools.',
 true),
(uuid_generate_v4(), 'Galion App', 'galion-app', '#10B981', 
 'User-friendly, helpful, empowering. Focus on productivity, transparency, and fairness. Use simple language that anyone can understand.',
 'Transparent workplace management platform for remote teams.',
 true),
(uuid_generate_v4(), 'Slavic Nomad', 'slavic-nomad', '#F59E0B', 
 'Adventurous, cultural, authentic. Share travel experiences, nomadic lifestyle, and cultural insights. Personal and engaging tone.',
 'Digital nomad sharing experiences about remote work and travel.',
 true),
(uuid_generate_v4(), 'Marilyn Element', 'marilyn-element', '#EC4899', 
 'Creative, artistic, inspiring. Focus on design, aesthetics, and personal expression. Emotive and passionate tone.',
 'Creative professional sharing design insights and artistic inspiration.',
 true);

-- ============================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update_updated_at trigger to all relevant tables
CREATE TRIGGER update_brands_updated_at BEFORE UPDATE ON brands
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_social_accounts_updated_at BEFORE UPDATE ON social_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_posts_updated_at BEFORE UPDATE ON content_posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_platform_posts_updated_at BEFORE UPDATE ON platform_posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_templates_updated_at BEFORE UPDATE ON content_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_team_permissions_updated_at BEFORE UPDATE ON team_permissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_media_assets_updated_at BEFORE UPDATE ON media_assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_n8n_webhooks_updated_at BEFORE UPDATE ON n8n_webhooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scheduled_jobs_updated_at BEFORE UPDATE ON scheduled_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================

-- View: Content posts with brand and creator info
CREATE OR REPLACE VIEW v_content_posts_detail AS
SELECT 
    cp.*,
    b.name as brand_name,
    b.slug as brand_slug,
    b.brand_color,
    u.username as creator_username,
    u.email as creator_email,
    (SELECT COUNT(*) FROM platform_posts pp WHERE pp.content_post_id = cp.id) as platform_count,
    (SELECT COUNT(*) FROM platform_posts pp WHERE pp.content_post_id = cp.id AND pp.status = 'posted') as posted_count,
    (SELECT SUM(pa.likes + pa.comments + pa.shares) FROM post_analytics pa 
     JOIN platform_posts pp ON pa.platform_post_id = pp.id 
     WHERE pp.content_post_id = cp.id) as total_engagement
FROM content_posts cp
LEFT JOIN brands b ON cp.brand_id = b.id
LEFT JOIN users u ON cp.created_by = u.id;

-- View: Platform performance summary
CREATE OR REPLACE VIEW v_platform_performance AS
SELECT 
    pp.platform,
    sa.brand_id,
    b.name as brand_name,
    COUNT(pp.id) as total_posts,
    COUNT(CASE WHEN pp.status = 'posted' THEN 1 END) as successful_posts,
    COUNT(CASE WHEN pp.status = 'failed' THEN 1 END) as failed_posts,
    AVG(pa.engagement_rate) as avg_engagement_rate,
    SUM(pa.likes) as total_likes,
    SUM(pa.comments) as total_comments,
    SUM(pa.shares) as total_shares,
    SUM(pa.views) as total_views
FROM platform_posts pp
LEFT JOIN post_analytics pa ON pp.id = pa.platform_post_id
LEFT JOIN social_accounts sa ON pp.social_account_id = sa.id
LEFT JOIN brands b ON sa.brand_id = b.id
GROUP BY pp.platform, sa.brand_id, b.name;

-- ============================================================
-- GRANT PERMISSIONS
-- ============================================================

-- Grant permissions to application user (adjust username as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nexuslang_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nexuslang_user;

-- ============================================================
-- MIGRATION COMPLETE
-- ============================================================

COMMENT ON TABLE brands IS 'Manages multiple brands (Galion Studio, Galion App, Slavic Nomad, Marilyn Element)';
COMMENT ON TABLE social_accounts IS 'Connected social media accounts per brand with OAuth credentials';
COMMENT ON TABLE content_posts IS 'All content posts with multi-platform support';
COMMENT ON TABLE platform_posts IS 'Individual platform-specific posts';
COMMENT ON TABLE post_analytics IS 'Engagement metrics for platform posts';
COMMENT ON TABLE content_templates IS 'Reusable content templates per brand';
COMMENT ON TABLE team_permissions IS 'Role-based access control for content management';
COMMENT ON TABLE post_comments IS 'Team comments and feedback on draft posts';
COMMENT ON TABLE content_activity_log IS 'Audit trail for all content management actions';
COMMENT ON TABLE media_assets IS 'Centralized media library';
COMMENT ON TABLE n8n_webhooks IS 'N8n workflow integration tracking';
COMMENT ON TABLE scheduled_jobs IS 'Track scheduled posting jobs';

