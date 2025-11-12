-- 006_custom_permissions.sql
-- Custom Permissions System - RBAC Implementation
-- Created: November 9, 2025

-- Roles Table
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT false, -- System roles cannot be deleted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permissions Table
CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    resource VARCHAR(100) NOT NULL,  -- e.g., 'users', 'documents', 'analytics'
    action VARCHAR(50) NOT NULL,     -- e.g., 'read', 'write', 'delete', 'admin'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resource, action)
);

-- Role-Permission Mapping (Many-to-Many)
CREATE TABLE IF NOT EXISTS role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);

-- User-Role Mapping (Many-to-Many)
CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- Optional: role expiration
    UNIQUE(user_id, role_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON role_permissions(permission_id);
CREATE INDEX IF NOT EXISTS idx_permissions_resource_action ON permissions(resource, action);

-- Insert default roles
INSERT INTO roles (name, description, is_system) VALUES
('admin', 'Full system administrator with all permissions', true),
('user', 'Standard user with basic access', true),
('moderator', 'Content moderator with review permissions', true),
('verified_user', 'Verified user with additional privileges', true),
('guest', 'Guest user with minimal access', true)
ON CONFLICT (name) DO NOTHING;

-- Insert default permissions
INSERT INTO permissions (resource, action, description) VALUES
-- User management permissions
('users', 'read', 'View user profiles and information'),
('users', 'write', 'Edit user profiles'),
('users', 'delete', 'Delete user accounts'),
('users', 'admin', 'Full user management including role assignment'),

-- Document management permissions
('documents', 'read', 'View documents'),
('documents', 'write', 'Upload and edit own documents'),
('documents', 'delete', 'Delete own documents'),
('documents', 'review', 'Review and approve/reject documents'),
('documents', 'admin', 'Full document management'),

-- Analytics permissions
('analytics', 'read', 'View analytics and reports'),
('analytics', 'write', 'Create custom analytics'),
('analytics', 'admin', 'Manage analytics system'),

-- Permissions management
('permissions', 'read', 'View roles and permissions'),
('permissions', 'write', 'Assign roles to users'),
('permissions', 'admin', 'Manage roles and permissions'),

-- System administration
('system', 'read', 'View system configuration'),
('system', 'admin', 'System administration and configuration')
ON CONFLICT (resource, action) DO NOTHING;

-- Assign all permissions to admin role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r 
CROSS JOIN permissions p 
WHERE r.name = 'admin'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Assign basic permissions to standard user role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name = 'user' 
  AND ((p.resource = 'users' AND p.action IN ('read', 'write'))
    OR (p.resource = 'documents' AND p.action IN ('read', 'write', 'delete')))
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Assign moderator permissions (can review documents)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name = 'moderator' 
  AND ((p.resource = 'users' AND p.action = 'read')
    OR (p.resource = 'documents' AND p.action IN ('read', 'review'))
    OR (p.resource = 'analytics' AND p.action = 'read'))
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Assign verified user permissions (same as user + analytics read)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name = 'verified_user' 
  AND ((p.resource = 'users' AND p.action IN ('read', 'write'))
    OR (p.resource = 'documents' AND p.action IN ('read', 'write', 'delete'))
    OR (p.resource = 'analytics' AND p.action = 'read'))
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Assign minimal guest permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name = 'guest' 
  AND p.resource = 'users' AND p.action = 'read'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
DROP TRIGGER IF EXISTS trigger_roles_updated_at ON roles;
CREATE TRIGGER trigger_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE FUNCTION update_roles_updated_at();

-- Function to check if user has permission (optimized query)
CREATE OR REPLACE FUNCTION user_has_permission(
    p_user_id UUID,
    p_resource VARCHAR,
    p_action VARCHAR
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM user_roles ur
        JOIN role_permissions rp ON ur.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE ur.user_id = p_user_id
          AND p.resource = p_resource
          AND p.action = p_action
          AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
    );
END;
$$ LANGUAGE plpgsql;

-- Function to get all user permissions (for caching)
CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id UUID)
RETURNS TABLE (
    resource VARCHAR,
    action VARCHAR,
    role_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT p.resource, p.action, r.name as role_name
    FROM user_roles ur
    JOIN roles r ON ur.role_id = r.id
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    JOIN permissions p ON rp.permission_id = p.id
    WHERE ur.user_id = p_user_id
      AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
    ORDER BY p.resource, p.action;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE roles IS 'User roles for RBAC system';
COMMENT ON TABLE permissions IS 'System permissions (resource + action)';
COMMENT ON TABLE role_permissions IS 'Maps permissions to roles';
COMMENT ON TABLE user_roles IS 'Assigns roles to users';
COMMENT ON FUNCTION user_has_permission IS 'Check if user has specific permission';
COMMENT ON FUNCTION get_user_permissions IS 'Get all permissions for a user';

