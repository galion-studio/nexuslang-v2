-- Galion Autonomous Agent System - Database Initialization
-- RunPod PostgreSQL Setup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create enums
CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'failed', 'cancelled', 'waiting_approval');
CREATE TYPE task_priority AS ENUM ('low', 'normal', 'high', 'urgent');
CREATE TYPE approval_status AS ENUM ('pending', 'approved', 'rejected', 'expired');
CREATE TYPE approval_type AS ENUM ('task_execution', 'workflow_step', 'resource_access', 'deployment');
CREATE TYPE approval_priority AS ENUM ('low', 'normal', 'high', 'critical');
CREATE TYPE agent_status AS ENUM ('idle', 'busy', 'offline', 'error');
CREATE TYPE message_type AS ENUM ('task_assignment', 'status_update', 'collaboration_request', 'resource_request');
CREATE TYPE message_priority AS ENUM ('low', 'normal', 'high', 'urgent');

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create user preferences table
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    preference_key VARCHAR(100) NOT NULL,
    preference_value TEXT,
    confidence_score DECIMAL(3,2) DEFAULT 0.5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, preference_key)
);

-- Create agents table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    capabilities JSONB DEFAULT '[]',
    personality JSONB DEFAULT '{}',
    status agent_status DEFAULT 'idle',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP WITH TIME ZONE
);

-- Create tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status task_status DEFAULT 'pending',
    priority task_priority DEFAULT 'normal',
    created_by UUID REFERENCES users(id),
    assigned_to UUID REFERENCES agents(id),
    parent_task_id UUID REFERENCES tasks(id),
    context JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    estimated_duration INTERVAL,
    actual_duration INTERVAL,
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    deadline TIMESTAMP WITH TIME ZONE
);

-- Create task steps table
CREATE TABLE task_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status task_status DEFAULT 'pending',
    assigned_to UUID REFERENCES agents(id),
    estimated_duration INTERVAL,
    actual_duration INTERVAL,
    result TEXT,
    error_message TEXT,
    requires_approval BOOLEAN DEFAULT false,
    approval_status approval_status DEFAULT 'approved',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(task_id, step_number)
);

-- Create approvals table
CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    step_id UUID REFERENCES task_steps(id) ON DELETE CASCADE,
    requested_by UUID REFERENCES agents(id),
    approval_type approval_type NOT NULL,
    priority approval_priority DEFAULT 'normal',
    title VARCHAR(500) NOT NULL,
    description TEXT,
    context JSONB DEFAULT '{}',
    status approval_status DEFAULT 'pending',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create workflows table
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    definition JSONB NOT NULL,
    version VARCHAR(20) DEFAULT '1.0',
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create workflow executions table
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    status task_status DEFAULT 'pending',
    context JSONB DEFAULT '{}',
    results JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create tools table
CREATE TABLE tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    endpoint VARCHAR(500) NOT NULL,
    method VARCHAR(10) DEFAULT 'GET',
    headers JSONB DEFAULT '{}',
    authentication JSONB DEFAULT '{}',
    parameters JSONB DEFAULT '{}',
    response_schema JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create agent messages table
CREATE TABLE agent_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_agent_id UUID REFERENCES agents(id),
    to_agent_id UUID REFERENCES agents(id),
    message_type message_type NOT NULL,
    priority message_priority DEFAULT 'normal',
    subject VARCHAR(200),
    content TEXT,
    metadata JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE
);

-- Create monitoring events table
CREATE TABLE monitoring_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    message TEXT,
    source VARCHAR(100),
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create performance metrics table
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4),
    unit VARCHAR(20),
    tags JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create sessions table for collaboration
CREATE TABLE collaboration_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    goal TEXT,
    created_by UUID REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'active',
    participants UUID[] DEFAULT '{}',
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE
);

-- Create test results table
CREATE TABLE test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_suite VARCHAR(100) NOT NULL,
    test_case VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL,
    duration INTERVAL,
    error_message TEXT,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_created_by ON tasks(created_by);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_task_steps_task_id ON task_steps(task_id);
CREATE INDEX idx_task_steps_status ON task_steps(status);
CREATE INDEX idx_approvals_status ON approvals(status);
CREATE INDEX idx_approvals_requested_by ON approvals(requested_by);
CREATE INDEX idx_agent_messages_to_agent ON agent_messages(to_agent_id, is_read);
CREATE INDEX idx_monitoring_events_created_at ON monitoring_events(created_at);
CREATE INDEX idx_performance_metrics_timestamp ON performance_metrics(timestamp);
CREATE INDEX idx_performance_metrics_name ON performance_metrics(metric_name);

-- Create full-text search indexes
CREATE INDEX idx_tasks_search ON tasks USING GIN (to_tsvector('english', title || ' ' || description));
CREATE INDEX idx_users_search ON users USING GIN (to_tsvector('english', username || ' ' || full_name || ' ' || email));

-- Insert default admin user
INSERT INTO users (username, email, hashed_password, full_name, is_superuser)
VALUES ('admin', 'admin@galion.app', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/J1uY4X9yI2j2z9zK', 'Galion Admin', true);

-- Insert default agents
INSERT INTO agents (name, type, description, capabilities, personality) VALUES
('code_agent', 'specialized', 'Specialized in writing, reviewing, and debugging code', '["coding", "debugging", "code_review", "refactoring"]', '{"expertise_level": "expert", "communication_style": "technical"}'),
('research_agent', 'specialized', 'Handles research, data analysis, and information gathering', '["research", "data_analysis", "web_search", "documentation"]', '{"expertise_level": "advanced", "communication_style": "analytical"}'),
('design_agent', 'specialized', 'Creates designs, UI/UX, and system architectures', '["design", "ui_ux", "system_design", "prototyping"]', '{"expertise_level": "advanced", "communication_style": "creative"}'),
('testing_agent', 'specialized', 'Ensures quality through comprehensive testing', '["testing", "qa", "validation", "performance_testing"]', '{"expertise_level": "expert", "communication_style": "methodical"}'),
('devops_agent', 'specialized', 'Specialized in infrastructure, deployment, and DevOps operations', '["infrastructure_as_code", "container_orchestration", "ci_cd", "cloud_platforms", "monitoring_setup", "performance_optimization"]', '{"expertise_level": "expert", "communication_style": "technical", "specialties": ["infrastructure", "automation", "reliability"]}'),
('security_agent', 'specialized', 'Specialized in security analysis, vulnerability assessment, and security hardening', '["vulnerability_scanning", "threat_modeling", "security_auditing", "code_security", "infrastructure_security", "compliance_checking"]', '{"expertise_level": "expert", "communication_style": "analytical", "specialties": ["security", "risk_management", "compliance"]}'),
('data_science_agent', 'specialized', 'Specialized in data analysis, statistical modeling, and machine learning', '["data_exploration", "statistical_analysis", "machine_learning", "feature_engineering", "data_visualization", "model_evaluation"]', '{"expertise_level": "expert", "communication_style": "analytical", "specialties": ["data_science", "statistics", "machine_learning"]}'),
('ux_ui_agent', 'specialized', 'Specialized in user experience design, interface design, and usability engineering', '["user_research", "persona_development", "information_architecture", "wireframing", "prototyping", "usability_testing"]', '{"expertise_level": "expert", "communication_style": "user_centric", "specialties": ["ux_design", "ui_design", "usability", "accessibility"]}'),
('business_analyst_agent', 'specialized', 'Specialized in business analysis, requirements engineering, and stakeholder management', '["requirements_analysis", "stakeholder_management", "business_process_modeling", "use_case_development", "functional_specifications"]', '{"expertise_level": "expert", "communication_style": "structured", "specialties": ["business_analysis", "requirements", "stakeholder_management"]}');

-- Insert default tools
INSERT INTO tools (name, description, endpoint, method) VALUES
('web_search', 'Search the web for information', 'https://api.duckduckgo.com/', 'GET'),
('code_formatter', 'Format and beautify code', 'https://api.codetabs.com/v1/format', 'POST'),
('documentation_generator', 'Generate documentation from code', 'https://api.docgen.com/generate', 'POST');

-- Create default workflow
INSERT INTO workflows (name, description, definition) VALUES
('Code Development Pipeline', 'Complete pipeline from requirements to deployment',
 '{
   "steps": [
     {"name": "requirements_analysis", "agent": "research_agent", "description": "Analyze and clarify requirements"},
     {"name": "system_design", "agent": "design_agent", "description": "Design system architecture"},
     {"name": "implementation", "agent": "code_agent", "description": "Implement the solution"},
     {"name": "testing", "agent": "testing_agent", "description": "Test and validate the implementation"}
   ]
 }');

-- Create trigger for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_task_steps_updated_at BEFORE UPDATE ON task_steps FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_approvals_updated_at BEFORE UPDATE ON approvals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_executions_updated_at BEFORE UPDATE ON workflow_executions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tools_updated_at BEFORE UPDATE ON tools FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_collaboration_sessions_updated_at BEFORE UPDATE ON collaboration_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed for your security model)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO galion;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO galion;
