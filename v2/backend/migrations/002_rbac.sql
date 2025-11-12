-- RBAC (Role-Based Access Control) Migration for Project Nexus
-- Version: 2.0.0
-- Created: November 11, 2025

-- ============================================================
-- ROLES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '[]'::jsonb,
    is_system BOOLEAN DEFAULT FALSE,  -- System roles cannot be deleted
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);
CREATE INDEX IF NOT EXISTS idx_roles_is_system ON roles(is_system);

-- ============================================================
-- PERMISSIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource VARCHAR(100) NOT NULL,  -- e.g., "users", "nexuslang", "admin"
    action VARCHAR(50) NOT NULL,     -- e.g., "read", "write", "delete", "execute"
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(resource, action)
);

-- Index for faster permission checks
CREATE INDEX IF NOT EXISTS idx_permissions_resource ON permissions(resource);
CREATE INDEX IF NOT EXISTS idx_permissions_action ON permissions(action);

-- ============================================================
-- USER_ROLES TABLE (Many-to-Many)
-- ============================================================
CREATE TABLE IF NOT EXISTS user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    expires_at TIMESTAMP WITH TIME ZONE,  -- Optional role expiration
    PRIMARY KEY (user_id, role_id)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_expires_at ON user_roles(expires_at);

-- ============================================================
-- BETA TESTER PROFILES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS beta_tester_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    cohort VARCHAR(50),              -- "alpha", "beta-1", "beta-2", etc.
    invited_by UUID REFERENCES users(id),
    invited_at TIMESTAMP WITH TIME ZONE,
    accepted_at TIMESTAMP WITH TIME ZONE,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    feedback_count INTEGER DEFAULT 0,
    bugs_reported INTEGER DEFAULT 0,
    features_tested JSONB DEFAULT '[]'::jsonb,
    test_assignments JSONB DEFAULT '[]'::jsonb,  -- Features assigned for testing
    notes TEXT,
    status VARCHAR(20) DEFAULT 'invited',  -- "invited", "active", "inactive", "graduated"
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_beta_profiles_user_id ON beta_tester_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_beta_profiles_cohort ON beta_tester_profiles(cohort);
CREATE INDEX IF NOT EXISTS idx_beta_profiles_status ON beta_tester_profiles(status);

-- ============================================================
-- FEATURE FLAGS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT FALSE,
    rollout_percentage INTEGER DEFAULT 0,  -- 0-100, for gradual rollout
    target_roles JSONB DEFAULT '[]'::jsonb,  -- Array of role names
    target_users JSONB DEFAULT '[]'::jsonb,  -- Array of user IDs
    target_cohorts JSONB DEFAULT '[]'::jsonb,  -- Array of cohort names
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster feature flag lookups
CREATE INDEX IF NOT EXISTS idx_feature_flags_name ON feature_flags(name);
CREATE INDEX IF NOT EXISTS idx_feature_flags_enabled ON feature_flags(enabled);

-- ============================================================
-- USER FEEDBACK TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    feature_name VARCHAR(200),
    feedback_type VARCHAR(50) NOT NULL,  -- "bug", "feature_request", "improvement", "praise"
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20),  -- "critical", "high", "medium", "low"
    status VARCHAR(50) DEFAULT 'new',  -- "new", "in_review", "planned", "in_progress", "resolved", "wont_fix"
    attachments JSONB DEFAULT '[]'::jsonb,  -- Array of file URLs
    metadata JSONB DEFAULT '{}'::jsonb,  -- Browser, OS, etc.
    assigned_to UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_type ON user_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_feedback_status ON user_feedback(status);
CREATE INDEX IF NOT EXISTS idx_feedback_severity ON user_feedback(severity);

-- ============================================================
-- AUDIT LOG TABLE (Enhanced)
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,  -- "login", "logout", "role_assigned", etc.
    resource_type VARCHAR(100),         -- "user", "role", "permission", etc.
    resource_id UUID,
    action VARCHAR(50),                 -- "create", "read", "update", "delete"
    details JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    severity VARCHAR(20) DEFAULT 'info',  -- "info", "warning", "error", "critical"
    request_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for faster audit queries
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_resource_type ON audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_severity ON audit_logs(severity);

-- ============================================================
-- API KEYS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL UNIQUE,  -- SHA-256 hash of the key
    key_prefix VARCHAR(20) NOT NULL,  -- First chars for identification (e.g., "nx_live_abc...")
    name VARCHAR(200),  -- User-friendly name
    permissions JSONB DEFAULT '[]'::jsonb,
    rate_limit_override INTEGER,  -- Custom rate limit for this key
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON api_keys(is_active);

-- ============================================================
-- INSERT DEFAULT ROLES
-- ============================================================

-- Super Admin Role (Full access to everything)
INSERT INTO roles (name, display_name, description, is_system, permissions)
VALUES (
    'super_admin',
    'Super Administrator',
    'Full system access with all permissions',
    TRUE,
    '["*:*"]'::jsonb
) ON CONFLICT (name) DO NOTHING;

-- Admin Role (User management + system settings)
INSERT INTO roles (name, display_name, description, is_system, permissions)
VALUES (
    'admin',
    'Administrator',
    'User management and system configuration',
    TRUE,
    '["users:*", "roles:*", "settings:*", "analytics:read", "feedback:*", "beta_testers:*"]'::jsonb
) ON CONFLICT (name) DO NOTHING;

-- Beta Tester Role (Testing features with feedback access)
INSERT INTO roles (name, display_name, description, is_system, permissions)
VALUES (
    'beta_tester',
    'Beta Tester',
    'Early access to features with feedback permissions',
    TRUE,
    '["nexuslang:execute", "ide:*", "voice:*", "feedback:create", "grokopedia:read"]'::jsonb
) ON CONFLICT (name) DO NOTHING;

-- Developer Role (API access with elevated limits)
INSERT INTO roles (name, display_name, description, is_system, permissions)
VALUES (
    'developer',
    'Developer',
    'API access with elevated rate limits',
    TRUE,
    '["nexuslang:execute", "api:*", "ide:*", "analytics:read", "grokopedia:*"]'::jsonb
) ON CONFLICT (name) DO NOTHING;

-- User Role (Standard user access)
INSERT INTO roles (name, display_name, description, is_system, permissions)
VALUES (
    'user',
    'User',
    'Standard user access to core features',
    TRUE,
    '["nexuslang:execute", "ide:read", "grokopedia:read", "community:*"]'::jsonb
) ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- INSERT DEFAULT PERMISSIONS
-- ============================================================

-- User management permissions
INSERT INTO permissions (resource, action, description) VALUES
    ('users', 'read', 'View user information'),
    ('users', 'create', 'Create new users'),
    ('users', 'update', 'Update user information'),
    ('users', 'delete', 'Delete users'),
    ('users', 'list', 'List all users')
ON CONFLICT (resource, action) DO NOTHING;

-- Role management permissions
INSERT INTO permissions (resource, action, description) VALUES
    ('roles', 'read', 'View role information'),
    ('roles', 'create', 'Create new roles'),
    ('roles', 'update', 'Update roles'),
    ('roles', 'delete', 'Delete roles'),
    ('roles', 'assign', 'Assign roles to users')
ON CONFLICT (resource, action) DO NOTHING;

-- NexusLang permissions
INSERT INTO permissions (resource, action, description) VALUES
    ('nexuslang', 'execute', 'Execute NexusLang code'),
    ('nexuslang', 'compile', 'Compile NexusLang code'),
    ('nexuslang', 'debug', 'Debug NexusLang code')
ON CONFLICT (resource, action) DO NOTHING;

-- IDE permissions
INSERT INTO permissions (resource, action, description) VALUES
    ('ide', 'read', 'Read-only IDE access'),
    ('ide', 'write', 'Edit code in IDE'),
    ('ide', 'collaborate', 'Real-time collaboration'),
    ('ide', 'share', 'Share projects publicly')
ON CONFLICT (resource, action) DO NOTHING;

-- Voice permissions
INSERT INTO permissions (resource, action, description) VALUES
    ('voice', 'stt', 'Speech-to-text'),
    ('voice', 'tts', 'Text-to-speech'),
    ('voice', 'clone', 'Voice cloning')
ON CONFLICT (resource, action) DO NOTHING;

-- Admin permissions
INSERT INTO permissions (resource, action, description) VALUES
    ('analytics', 'read', 'View analytics'),
    ('settings', 'read', 'View system settings'),
    ('settings', 'update', 'Update system settings'),
    ('feedback', 'read', 'View user feedback'),
    ('feedback', 'update', 'Manage user feedback'),
    ('beta_testers', 'read', 'View beta tester profiles'),
    ('beta_testers', 'manage', 'Manage beta testers')
ON CONFLICT (resource, action) DO NOTHING;

-- ============================================================
-- CREATE VIEWS FOR EASIER QUERIES
-- ============================================================

-- View: User permissions (flattened from roles)
CREATE OR REPLACE VIEW user_permissions AS
SELECT DISTINCT
    ur.user_id,
    u.email,
    u.username,
    r.name as role_name,
    p.value as permission
FROM user_roles ur
JOIN users u ON u.id = ur.user_id
JOIN roles r ON r.id = ur.role_id
CROSS JOIN LATERAL jsonb_array_elements_text(r.permissions) as p(value)
WHERE (ur.expires_at IS NULL OR ur.expires_at > NOW());

-- View: Active beta testers
CREATE OR REPLACE VIEW active_beta_testers AS
SELECT
    u.id,
    u.email,
    u.username,
    bt.cohort,
    bt.feedback_count,
    bt.bugs_reported,
    bt.invited_at,
    bt.accepted_at
FROM beta_tester_profiles bt
JOIN users u ON u.id = bt.user_id
WHERE bt.status = 'active'
ORDER BY bt.accepted_at DESC;

-- ============================================================
-- CREATE FUNCTIONS FOR PERMISSION CHECKING
-- ============================================================

-- Function: Check if user has permission
CREATE OR REPLACE FUNCTION user_has_permission(
    p_user_id UUID,
    p_resource VARCHAR,
    p_action VARCHAR
) RETURNS BOOLEAN AS $$
DECLARE
    has_perm BOOLEAN;
BEGIN
    -- Check if user has wildcard permission (*:*)
    SELECT EXISTS (
        SELECT 1 FROM user_permissions
        WHERE user_id = p_user_id
        AND permission = '*:*'
    ) INTO has_perm;
    
    IF has_perm THEN
        RETURN TRUE;
    END IF;
    
    -- Check if user has resource wildcard (resource:*)
    SELECT EXISTS (
        SELECT 1 FROM user_permissions
        WHERE user_id = p_user_id
        AND permission = p_resource || ':*'
    ) INTO has_perm;
    
    IF has_perm THEN
        RETURN TRUE;
    END IF;
    
    -- Check if user has specific permission
    SELECT EXISTS (
        SELECT 1 FROM user_permissions
        WHERE user_id = p_user_id
        AND permission = p_resource || ':' || p_action
    ) INTO has_perm;
    
    RETURN has_perm;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- CREATE TRIGGERS FOR AUTOMATIC TIMESTAMPS
-- ============================================================

-- Function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_beta_profiles_updated_at BEFORE UPDATE ON beta_tester_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feature_flags_updated_at BEFORE UPDATE ON feature_flags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feedback_updated_at BEFORE UPDATE ON user_feedback
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- MIGRATION COMPLETE
-- ============================================================
-- Version: 002_rbac.sql
-- Description: RBAC system with roles, permissions, beta testers, and feature flags
-- Status: ✅ Complete

