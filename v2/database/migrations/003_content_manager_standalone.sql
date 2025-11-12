-- Content Manager - Standalone Migration
-- Creates all tables including users (no dependencies)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- USERS TABLE (Standalone - no dependencies)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- BRANDS TABLE
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

CREATE INDEX idx_brands_slug ON brands(slug);

-- ============================================================
-- SOCIAL ACCOUNTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS social_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    account_name VARCHAR(200) NOT NULL,
    account_url VARCHAR(500),
    account_id VARCHAR(200),
    credentials JSONB,
    platform_metadata JSONB,
    is_active BOOLEAN DEFAULT true,
    last_synced TIMESTAMP,
    sync_status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_social_accounts_brand ON social_accounts(brand_id);
CREATE INDEX idx_social_accounts_platform ON social_accounts(platform);

-- ============================================================
-- CONTENT POSTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS content_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    title VARCHAR(500),
    content TEXT NOT NULL,
    content_html TEXT,
    excerpt TEXT,
    media_urls JSONB DEFAULT '[]'::jsonb,
    platforms JSONB DEFAULT '[]'::jsonb,
    hashtags JSONB DEFAULT '[]'::jsonb,
    mentions JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(50) DEFAULT 'draft',
    scheduled_at TIMESTAMP,
    published_at TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_content_posts_brand ON content_posts(brand_id);
CREATE INDEX idx_content_posts_status ON content_posts(status);

-- ============================================================
-- PLATFORM POSTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS platform_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_post_id UUID NOT NULL REFERENCES content_posts(id) ON DELETE CASCADE,
    social_account_id UUID NOT NULL REFERENCES social_accounts(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(200),
    platform_url VARCHAR(500),
    platform_content TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    posted_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_platform_posts_content ON platform_posts(content_post_id);

-- ============================================================
-- POST ANALYTICS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS post_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_post_id UUID NOT NULL REFERENCES platform_posts(id) ON DELETE CASCADE,
    likes INT DEFAULT 0,
    comments INT DEFAULT 0,
    shares INT DEFAULT 0,
    views INT DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0.00,
    platform_specific_metrics JSONB DEFAULT '{}'::jsonb,
    synced_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_post_analytics_platform_post ON post_analytics(platform_post_id);

-- ============================================================
-- INSERT DEFAULT BRANDS
-- ============================================================
INSERT INTO brands (name, slug, brand_color, voice_guidelines, description) VALUES
('Galion Studio', 'galion-studio', '#3B82F6', 
 'Professional, innovative, technical. Focus on AI development, transparency, and community building.',
 'AI-native development platform building NexusLang and transparent workplace tools.'),
('Galion App', 'galion-app', '#10B981', 
 'User-friendly, helpful, empowering. Focus on productivity, transparency, and fairness.',
 'Transparent workplace management platform for remote teams.'),
('Slavic Nomad', 'slavic-nomad', '#F59E0B', 
 'Adventurous, cultural, authentic. Share travel experiences, nomadic lifestyle, and cultural insights.',
 'Digital nomad sharing experiences about remote work and travel.'),
('Marilyn Element', 'marilyn-element', '#EC4899', 
 'Creative, artistic, inspiring. Focus on design, aesthetics, and personal expression.',
 'Creative professional sharing design insights and artistic inspiration.')
ON CONFLICT (slug) DO NOTHING;

COMMENT ON TABLE brands IS 'Multi-brand management (Galion Studio, Galion App, Slavic Nomad, Marilyn Element)';
COMMENT ON TABLE social_accounts IS 'Connected social media accounts with OAuth credentials';
COMMENT ON TABLE content_posts IS 'Multi-platform content posts';
COMMENT ON TABLE platform_posts IS 'Individual platform-specific posts';
COMMENT ON TABLE post_analytics IS 'Engagement metrics for posts';

