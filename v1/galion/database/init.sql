-- Initialize Nexus Core database
-- This script runs when the database container first starts

-- Create schemas for organizing tables
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS chat;
CREATE SCHEMA IF NOT EXISTS cms;
CREATE SCHEMA IF NOT EXISTS media;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS content;

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Users table (shared by auth-service and user-service)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    bio TEXT,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    email_verified BOOLEAN DEFAULT false,
    failed_login_count INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP WITH TIME ZONE,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON public.users(role);
CREATE INDEX IF NOT EXISTS idx_users_status ON public.users(status);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON public.users(created_at);

-- Trigger to auto-update updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Content schema tables for scraped content
-- Scraped posts
CREATE TABLE IF NOT EXISTS content.posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_url VARCHAR(500) UNIQUE NOT NULL,
    title VARCHAR(500),
    author_username VARCHAR(255),
    author_url VARCHAR(500),
    posted_at TIMESTAMP WITH TIME ZONE,
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Scraped images
CREATE TABLE IF NOT EXISTS content.images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES content.posts(id) ON DELETE CASCADE,
    source_url VARCHAR(1000) NOT NULL,
    r2_key VARCHAR(500),
    r2_url VARCHAR(1000),
    file_size BIGINT,
    width INTEGER,
    height INTEGER,
    mime_type VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scraped users
CREATE TABLE IF NOT EXISTS content.scraped_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    profile_url VARCHAR(500),
    avatar_url VARCHAR(1000),
    bio TEXT,
    metadata JSONB DEFAULT '{}',
    first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scraping jobs
CREATE TABLE IF NOT EXISTS content.scraping_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    source_url VARCHAR(500),
    pages_scraped INTEGER DEFAULT 0,
    items_scraped INTEGER DEFAULT 0,
    errors JSONB DEFAULT '[]',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for content schema
CREATE INDEX IF NOT EXISTS idx_posts_source_url ON content.posts(source_url);
CREATE INDEX IF NOT EXISTS idx_posts_author ON content.posts(author_username);
CREATE INDEX IF NOT EXISTS idx_posts_posted_at ON content.posts(posted_at);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON content.posts(created_at);
CREATE INDEX IF NOT EXISTS idx_images_post_id ON content.images(post_id);
CREATE INDEX IF NOT EXISTS idx_images_r2_key ON content.images(r2_key);
CREATE INDEX IF NOT EXISTS idx_scraped_users_username ON content.scraped_users(username);
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_status ON content.scraping_jobs(status);
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_created_at ON content.scraping_jobs(created_at);

-- Trigger to auto-update updated_at for posts
CREATE TRIGGER update_posts_updated_at
    BEFORE UPDATE ON content.posts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Nexus Core database initialized successfully';
END $$;

