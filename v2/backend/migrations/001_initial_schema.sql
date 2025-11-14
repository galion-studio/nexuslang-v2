-- Initial Database Schema for NexusLang v2
-- Complete schema for users, projects, billing, and content

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";  -- For AI embeddings

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    
    -- Profile
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    bio TEXT,
    website VARCHAR(500),
    
    -- Account status
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- Subscription
    subscription_tier VARCHAR(50) DEFAULT 'free' NOT NULL,
    subscription_status VARCHAR(50) DEFAULT 'active' NOT NULL,
    subscription_start TIMESTAMP,
    subscription_end TIMESTAMP,
    
    -- Credits
    credits REAL DEFAULT 100.0 NOT NULL,
    credits_used REAL DEFAULT 0.0 NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login TIMESTAMP,
    
    -- API access
    api_key VARCHAR(255) UNIQUE,
    
    -- Preferences
    preferences TEXT,
    
    -- Email verification
    verification_token VARCHAR(255),
    verification_token_expires TIMESTAMP,
    
    -- Password reset
    reset_token VARCHAR(255),
    reset_token_expires TIMESTAMP
);

-- Create indexes for users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Project info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    language VARCHAR(50) DEFAULT 'nexuslang' NOT NULL,
    
    -- Code
    code TEXT,
    compiled_binary BYTEA,
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft' NOT NULL,
    visibility VARCHAR(50) DEFAULT 'private' NOT NULL,
    
    -- Stats
    execution_count INTEGER DEFAULT 0,
    last_executed TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- Generated content table
CREATE TABLE IF NOT EXISTS generated_content (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Content info
    type VARCHAR(50) NOT NULL,  -- image, video, text, audio
    prompt TEXT NOT NULL,
    model VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    
    -- Generated data
    url VARCHAR(1000),
    content TEXT,
    metadata JSONB,
    
    -- Credits
    credits_used REAL NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_generated_content_user_id ON generated_content(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_content_type ON generated_content(type);
CREATE INDEX IF NOT EXISTS idx_generated_content_created_at ON generated_content(created_at);

-- Execution history table
CREATE TABLE IF NOT EXISTS executions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    
    -- Execution info
    language VARCHAR(50) NOT NULL,
    code_hash VARCHAR(64),  -- SHA256 of code
    
    -- Results
    stdout TEXT,
    stderr TEXT,
    return_code INTEGER,
    execution_time REAL,
    success BOOLEAN,
    
    -- Credits
    credits_used REAL,
    
    -- Timestamp
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_executions_user_id ON executions(user_id);
CREATE INDEX IF NOT EXISTS idx_executions_project_id ON executions(project_id);
CREATE INDEX IF NOT EXISTS idx_executions_executed_at ON executions(executed_at);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Transaction info
    type VARCHAR(50) NOT NULL,  -- subscription, credit_purchase, credit_usage
    amount REAL NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    
    -- Payment
    payment_method VARCHAR(50),
    payment_id VARCHAR(255),
    
    -- Description
    description TEXT,
    metadata JSONB,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);

-- API usage tracking table
CREATE TABLE IF NOT EXISTS api_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Request info
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    
    -- Timing
    response_time REAL,
    
    -- Credits
    credits_used REAL DEFAULT 0,
    
    -- Metadata
    user_agent TEXT,
    ip_address INET,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint ON api_usage(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage(created_at);

-- Knowledge base table (for Grokopedia)
CREATE TABLE IF NOT EXISTS knowledge (
    id SERIAL PRIMARY KEY,
    
    -- Content
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    
    -- Vector embedding for semantic search
    embedding vector(1536),  -- OpenAI embedding size
    
    -- Status
    published BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_published ON knowledge(published);
-- Vector similarity search index
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge USING ivfflat (embedding vector_cosine_ops);

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_updated_at BEFORE UPDATE ON knowledge
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default knowledge base entries
INSERT INTO knowledge (title, content, category, tags) VALUES
('Getting Started with NexusLang', 'NexusLang is an AI-native programming language...', 'tutorial', ARRAY['nexuslang', 'getting-started']),
('AI Chat Integration', 'Learn how to integrate AI chat in your applications...', 'guide', ARRAY['ai', 'chat', 'integration']),
('API Reference', 'Complete API reference for NexusLang v2...', 'reference', ARRAY['api', 'docs'])
ON CONFLICT DO NOTHING;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nexus;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nexus;

