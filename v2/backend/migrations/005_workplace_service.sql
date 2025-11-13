-- Workplace Service Database Migration
-- Adds comprehensive workplace management tables

-- Create workspaces table
CREATE TABLE IF NOT EXISTS workspaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    billing_cycle VARCHAR(50) DEFAULT 'monthly',
    tax_rate DECIMAL(5,2) DEFAULT 0.00,
    currency VARCHAR(10) DEFAULT 'USD',
    workflow_type VARCHAR(50) DEFAULT 'kanban',
    platform_permissions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    member_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create workspace_members table
CREATE TABLE IF NOT EXISTS workspace_members (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    role VARCHAR(50) DEFAULT 'member',
    can_create_projects BOOLEAN DEFAULT FALSE,
    can_review_applications BOOLEAN DEFAULT FALSE,
    can_post_jobs BOOLEAN DEFAULT FALSE,
    platform_permissions JSONB DEFAULT '{}',
    skills TEXT[],  -- Array of skill strings
    availability_status VARCHAR(50) DEFAULT 'available',
    performance_score DECIMAL(3,1) DEFAULT 5.0,
    workload_capacity INTEGER DEFAULT 40,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, user_id)
);

-- Create sync_events table
CREATE TABLE IF NOT EXISTS sync_events (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    source_platform VARCHAR(50) NOT NULL,
    target_platforms TEXT[] NOT NULL,  -- Array of platform strings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for sync_events
CREATE INDEX IF NOT EXISTS idx_sync_events_workspace_id ON sync_events(workspace_id);
CREATE INDEX IF NOT EXISTS idx_sync_events_event_type ON sync_events(event_type);
CREATE INDEX IF NOT EXISTS idx_sync_events_created_at ON sync_events(created_at);

-- Update tasks table to add workplace fields
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS assignee_id INTEGER REFERENCES users(id);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS assigned_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS assignment_method VARCHAR(50) DEFAULT 'manual';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS required_skills TEXT[];
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS blockers TEXT[];
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS ai_analysis JSONB;

-- Create time_logs table
CREATE TABLE IF NOT EXISTS time_logs (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    hours DECIMAL(6,2) NOT NULL CHECK (hours > 0),
    work_date DATE NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) DEFAULT 'development',
    billable BOOLEAN DEFAULT TRUE,
    auto_categorized BOOLEAN DEFAULT FALSE,
    ai_analysis JSONB,
    hourly_rate DECIMAL(8,2),
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for time_logs
CREATE INDEX IF NOT EXISTS idx_time_logs_task_id ON time_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_time_logs_user_id ON time_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_time_logs_work_date ON time_logs(work_date);

-- Create live_sessions table
CREATE TABLE IF NOT EXISTS live_sessions (
    id VARCHAR(36) PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_by INTEGER NOT NULL REFERENCES users(id),
    session_type VARCHAR(50) NOT NULL,
    max_participants INTEGER DEFAULT 10,
    participants INTEGER[] DEFAULT '{}',  -- Array of user IDs
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE
);

-- Create code_reviews table
CREATE TABLE IF NOT EXISTS code_reviews (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    requested_by INTEGER NOT NULL REFERENCES users(id),
    code_content TEXT NOT NULL,
    language VARCHAR(50) NOT NULL,
    review_type VARCHAR(50) DEFAULT 'general',
    severity_level VARCHAR(20) DEFAULT 'medium',
    ai_analysis JSONB,
    ai_feedback JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Update payments table to add workplace fields
ALTER TABLE payments ADD COLUMN IF NOT EXISTS workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS period_start TIMESTAMP WITH TIME ZONE;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS period_end TIMESTAMP WITH TIME ZONE;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS auto_generated BOOLEAN DEFAULT FALSE;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS billing_data JSONB;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_workspaces_owner_id ON workspaces(owner_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace_id ON workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_user_id ON workspace_members(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee_id ON tasks(assignee_id);
CREATE INDEX IF NOT EXISTS idx_live_sessions_project_id ON live_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_code_reviews_project_id ON code_reviews(project_id);
CREATE INDEX IF NOT EXISTS idx_payments_workspace_id ON payments(workspace_id);

-- Create updated_at triggers for tables that have this column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at columns
DROP TRIGGER IF EXISTS update_workspaces_updated_at ON workspaces;
CREATE TRIGGER update_workspaces_updated_at
    BEFORE UPDATE ON workspaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample workspace data (optional - for testing)
-- This would typically be done through the API
INSERT INTO workspaces (name, description, owner_id)
SELECT 'Default Workspace', 'Default workspace for testing', id
FROM users
WHERE username = 'admin'
ON CONFLICT DO NOTHING;

-- Update existing projects to have workspace relationship if needed
-- This is a migration consideration for existing data
