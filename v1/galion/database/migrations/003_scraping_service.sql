-- Migration for scraping service tables

-- Add storage columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS storage_plan VARCHAR(50) DEFAULT 'free';
ALTER TABLE users ADD COLUMN IF NOT EXISTS storage_limit_gb FLOAT DEFAULT 1.0;

-- Storage files table
CREATE TABLE IF NOT EXISTS storage_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    storage_path TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    content_type VARCHAR(100),
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    CONSTRAINT fk_storage_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_storage_files_user ON storage_files(user_id);
CREATE INDEX idx_storage_files_created ON storage_files(created_at);
CREATE INDEX idx_storage_files_tags ON storage_files USING GIN(tags);

-- Workflow executions table
CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workflow_name VARCHAR(100) NOT NULL,
    inputs JSONB,
    status VARCHAR(50) NOT NULL,
    outputs JSONB,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    CONSTRAINT fk_workflow_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_workflow_executions_user ON workflow_executions(user_id);
CREATE INDEX idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX idx_workflow_executions_created ON workflow_executions(created_at);

-- Custom workflows table
CREATE TABLE IF NOT EXISTS custom_workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    workflow_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_custom_workflow_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT unique_user_workflow_name UNIQUE(user_id, name)
);

CREATE INDEX idx_custom_workflows_user ON custom_workflows(user_id);

-- Scraping history table (for tracking scraping operations)
CREATE TABLE IF NOT EXISTS scraping_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    mode VARCHAR(20) NOT NULL,
    status VARCHAR(50) NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    storage_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_scraping_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_scraping_history_user ON scraping_history(user_id);
CREATE INDEX idx_scraping_history_created ON scraping_history(created_at);

-- Storage usage analytics view
CREATE OR REPLACE VIEW user_storage_summary AS
SELECT 
    u.id as user_id,
    u.email,
    u.storage_plan,
    u.storage_limit_gb,
    COALESCE(SUM(sf.size_bytes), 0) as total_bytes_used,
    COALESCE(SUM(sf.size_bytes), 0) / (1024.0 * 1024.0 * 1024.0) as total_gb_used,
    COUNT(sf.id) as total_files
FROM users u
LEFT JOIN storage_files sf ON u.id = sf.user_id AND sf.deleted_at IS NULL
GROUP BY u.id, u.email, u.storage_plan, u.storage_limit_gb;

COMMENT ON TABLE storage_files IS 'User uploaded files and scraped content';
COMMENT ON TABLE workflow_executions IS 'ComfyUI workflow execution history';
COMMENT ON TABLE custom_workflows IS 'User-uploaded custom ComfyUI workflows';
COMMENT ON TABLE scraping_history IS 'Web scraping operation history';

