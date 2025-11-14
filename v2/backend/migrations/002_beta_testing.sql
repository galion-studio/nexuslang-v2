-- Migration: Beta Testing Infrastructure
-- Description: Adds tables for beta user management, invitations, and waitlist
-- Version: 002
-- Date: 2025-11-14

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Beta users table
CREATE TABLE IF NOT EXISTS beta_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invitation_code VARCHAR(50) NOT NULL UNIQUE,
    invited_by UUID REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed', 'banned')),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    feedback_count INTEGER DEFAULT 0,
    referral_count INTEGER DEFAULT 0,
    waitlist_position INTEGER,
    priority_score INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_beta_users_invitation_code ON beta_users(invitation_code);
CREATE INDEX IF NOT EXISTS idx_beta_users_status ON beta_users(status);
CREATE INDEX IF NOT EXISTS idx_beta_users_user_id ON beta_users(user_id);
CREATE INDEX IF NOT EXISTS idx_beta_users_created_at ON beta_users(created_at);

-- Beta invitations table (for codes that can be used before registration)
CREATE TABLE IF NOT EXISTS beta_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    created_by UUID REFERENCES users(id),
    used_by UUID REFERENCES users(id),
    expires_at TIMESTAMP WITH TIME ZONE,
    used_at TIMESTAMP WITH TIME ZONE,
    is_used CHAR(1) DEFAULT 'N' CHECK (is_used IN ('Y', 'N')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_beta_invitations_code ON beta_invitations(code);
CREATE INDEX IF NOT EXISTS idx_beta_invitations_email ON beta_invitations(email);
CREATE INDEX IF NOT EXISTS idx_beta_invitations_used ON beta_invitations(is_used);

-- Beta waitlist table
CREATE TABLE IF NOT EXISTS beta_waitlist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    signup_source VARCHAR(50) DEFAULT 'website',
    priority_score INTEGER DEFAULT 0,
    position INTEGER,
    invited_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_beta_waitlist_email ON beta_waitlist(email);
CREATE INDEX IF NOT EXISTS idx_beta_waitlist_priority ON beta_waitlist(priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_beta_waitlist_created_at ON beta_waitlist(created_at);

-- Function to update waitlist positions
CREATE OR REPLACE FUNCTION update_waitlist_positions()
RETURNS TRIGGER AS $$
BEGIN
    -- Update positions based on priority score and signup date
    WITH ranked_waitlist AS (
        SELECT
            id,
            ROW_NUMBER() OVER (
                ORDER BY
                    priority_score DESC,
                    created_at ASC
            ) as new_position
        FROM beta_waitlist
        WHERE invited_at IS NULL
    )
    UPDATE beta_waitlist
    SET position = ranked_waitlist.new_position
    FROM ranked_waitlist
    WHERE beta_waitlist.id = ranked_waitlist.id;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger to maintain waitlist positions
CREATE TRIGGER trigger_update_waitlist_positions
    AFTER INSERT OR UPDATE OR DELETE ON beta_waitlist
    FOR EACH STATEMENT
    EXECUTE FUNCTION update_waitlist_positions();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER trigger_beta_users_updated_at
    BEFORE UPDATE ON beta_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_beta_waitlist_updated_at
    BEFORE UPDATE ON beta_waitlist
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to increment referral count
CREATE OR REPLACE FUNCTION increment_referral_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.invited_by IS NOT NULL AND (OLD.invited_by IS NULL OR OLD.invited_by != NEW.invited_by) THEN
        UPDATE beta_users
        SET referral_count = referral_count + 1,
            updated_at = NOW()
        WHERE user_id = NEW.invited_by;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to increment referral count when user is invited
CREATE TRIGGER trigger_increment_referral_count
    AFTER INSERT OR UPDATE ON beta_users
    FOR EACH ROW
    WHEN (NEW.invited_by IS NOT NULL)
    EXECUTE FUNCTION increment_referral_count();

-- Insert some initial beta invitation codes
INSERT INTO beta_invitations (code, email, created_by)
SELECT
    'GALION-' || UPPER(SUBSTRING(MD5(RANDOM()::text) FROM 1 FOR 8)),
    'admin@nexuslang.dev',
    NULL
FROM generate_series(1, 50); -- Generate 50 initial codes

-- Comments for documentation
COMMENT ON TABLE beta_users IS 'Beta testing user management and invitation tracking';
COMMENT ON TABLE beta_invitations IS 'Beta invitation codes that can be used before user registration';
COMMENT ON TABLE beta_waitlist IS 'Waitlist for users interested in beta testing';

COMMENT ON COLUMN beta_users.invitation_code IS 'Unique code for beta access';
COMMENT ON COLUMN beta_users.status IS 'User beta status: pending, active, completed, banned';
COMMENT ON COLUMN beta_users.priority_score IS 'Score for waitlist prioritization';
COMMENT ON COLUMN beta_invitations.is_used IS 'Y/N flag for performance (avoids NULL checks)';
COMMENT ON COLUMN beta_waitlist.position IS 'Calculated position in waitlist';
