-- Migration: Feedback System
-- Description: Adds tables for user feedback collection and management
-- Version: 004
-- Date: 2025-11-14

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL CHECK (category IN ('bug', 'feature', 'improvement', 'general', 'other')),
    subcategory VARCHAR(100),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(200),
    comment TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'reviewed', 'in_progress', 'resolved', 'closed', 'rejected')),
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    platform VARCHAR(50) CHECK (platform IN ('galion-app', 'developer-platform', 'galion-studio')),
    page_url VARCHAR(500),
    user_agent TEXT,
    attachments JSONB,
    tags JSONB,
    metadata JSONB,
    admin_response TEXT,
    responded_by UUID REFERENCES users(id),
    responded_at TIMESTAMP WITH TIME ZONE,
    upvotes INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback(category);
CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status);
CREATE INDEX IF NOT EXISTS idx_feedback_priority ON feedback(priority);
CREATE INDEX IF NOT EXISTS idx_feedback_platform ON feedback(platform);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating);
CREATE INDEX IF NOT EXISTS idx_feedback_upvotes ON feedback(upvotes DESC);

-- Feedback attachments table
CREATE TABLE IF NOT EXISTS feedback_attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feedback_id UUID NOT NULL REFERENCES feedback(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_type VARCHAR(50), -- image, video, document, etc.
    file_size INTEGER, -- Size in bytes
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_feedback_attachments_feedback_id ON feedback_attachments(feedback_id);
CREATE INDEX IF NOT EXISTS idx_feedback_attachments_file_type ON feedback_attachments(file_type);

-- Feedback votes table (for upvotes/downvotes)
CREATE TABLE IF NOT EXISTS feedback_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feedback_id UUID NOT NULL REFERENCES feedback(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vote_type VARCHAR(10) DEFAULT 'upvote' CHECK (vote_type IN ('upvote', 'downvote')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(feedback_id, user_id) -- One vote per user per feedback
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_feedback_votes_feedback_id ON feedback_votes(feedback_id);
CREATE INDEX IF NOT EXISTS idx_feedback_votes_user_id ON feedback_votes(user_id);

-- Feedback categories table (for predefined categories)
CREATE TABLE IF NOT EXISTS feedback_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50), -- Icon identifier for UI
    color VARCHAR(7), -- Hex color code
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_feedback_categories_name ON feedback_categories(name);
CREATE INDEX IF NOT EXISTS idx_feedback_categories_active ON feedback_categories(is_active);
CREATE INDEX IF NOT EXISTS idx_feedback_categories_sort_order ON feedback_categories(sort_order);

-- Insert default feedback categories
INSERT INTO feedback_categories (name, display_name, description, icon, color, sort_order) VALUES
('bug', 'Bug Report', 'Report bugs, errors, or unexpected behavior', 'bug', '#ef4444', 1),
('feature', 'Feature Request', 'Suggest new features or improvements', 'lightbulb', '#3b82f6', 2),
('improvement', 'Improvement', 'Suggestions for existing features', 'arrow-up', '#10b981', 3),
('general', 'General Feedback', 'General comments and feedback', 'message', '#6b7280', 4),
('other', 'Other', 'Anything else', 'help', '#8b5cf6', 5)
ON CONFLICT (name) DO NOTHING;

-- Function to update feedback statistics
CREATE OR REPLACE FUNCTION update_feedback_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update user's feedback count in beta_users table
    IF TG_OP = 'INSERT' THEN
        UPDATE beta_users
        SET feedback_count = feedback_count + 1,
            updated_at = NOW()
        WHERE user_id = NEW.user_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE beta_users
        SET feedback_count = GREATEST(feedback_count - 1, 0),
            updated_at = NOW()
        WHERE user_id = OLD.user_id;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger to maintain feedback counts
CREATE TRIGGER trigger_update_feedback_stats
    AFTER INSERT OR DELETE ON feedback
    FOR EACH ROW
    EXECUTE FUNCTION update_feedback_stats();

-- Function to validate feedback data
CREATE OR REPLACE FUNCTION validate_feedback()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure title is not empty if provided
    IF NEW.title IS NOT NULL AND LENGTH(TRIM(NEW.title)) = 0 THEN
        RAISE EXCEPTION 'Title cannot be empty if provided';
    END IF;

    -- Ensure comment is not empty
    IF LENGTH(TRIM(NEW.comment)) = 0 THEN
        RAISE EXCEPTION 'Comment cannot be empty';
    END IF;

    -- Validate rating range
    IF NEW.rating IS NOT NULL AND (NEW.rating < 1 OR NEW.rating > 5) THEN
        RAISE EXCEPTION 'Rating must be between 1 and 5';
    END IF;

    -- Set responded_at when admin_response is provided
    IF NEW.admin_response IS NOT NULL AND NEW.responded_at IS NULL THEN
        NEW.responded_at = NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to validate feedback data
CREATE TRIGGER trigger_validate_feedback
    BEFORE INSERT OR UPDATE ON feedback
    FOR EACH ROW
    EXECUTE FUNCTION validate_feedback();

-- Function to handle feedback votes
CREATE OR REPLACE FUNCTION handle_feedback_vote()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Increment upvote count
        UPDATE feedback
        SET upvotes = upvotes + CASE WHEN NEW.vote_type = 'upvote' THEN 1 ELSE -1 END,
            updated_at = NOW()
        WHERE id = NEW.feedback_id;
    ELSIF TG_OP = 'DELETE' THEN
        -- Decrement upvote count
        UPDATE feedback
        SET upvotes = upvotes - CASE WHEN OLD.vote_type = 'upvote' THEN 1 ELSE -1 END,
            updated_at = NOW()
        WHERE id = OLD.feedback_id;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Handle vote type change
        IF OLD.vote_type != NEW.vote_type THEN
            UPDATE feedback
            SET upvotes = upvotes - CASE WHEN OLD.vote_type = 'upvote' THEN 1 ELSE -1 END +
                              CASE WHEN NEW.vote_type = 'upvote' THEN 1 ELSE -1 END,
                updated_at = NOW()
            WHERE id = NEW.feedback_id;
        END IF;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger to handle feedback votes
CREATE TRIGGER trigger_handle_feedback_vote
    AFTER INSERT OR UPDATE OR DELETE ON feedback_votes
    FOR EACH ROW
    EXECUTE FUNCTION handle_feedback_vote();

-- Create views for feedback analytics
CREATE OR REPLACE VIEW feedback_analytics AS
SELECT
    f.id,
    f.category,
    f.rating,
    f.status,
    f.priority,
    f.platform,
    f.upvotes,
    f.is_public,
    f.created_at,
    f.updated_at,
    EXTRACT(EPOCH FROM (NOW() - f.created_at))/86400 as days_old,
    u.email as user_email,
    u.full_name as user_name,
    r.email as responder_email,
    fc.display_name as category_name,
    fc.color as category_color
FROM feedback f
LEFT JOIN users u ON f.user_id = u.id
LEFT JOIN users r ON f.responded_by = r.id
LEFT JOIN feedback_categories fc ON f.category = fc.name;

-- Create view for feedback statistics
CREATE OR REPLACE VIEW feedback_stats AS
SELECT
    category,
    COUNT(*) as total_count,
    AVG(rating) as avg_rating,
    COUNT(CASE WHEN status IN ('resolved', 'closed') THEN 1 END) as resolved_count,
    COUNT(CASE WHEN status = 'new' THEN 1 END) as new_count,
    AVG(upvotes) as avg_upvotes,
    AVG(EXTRACT(EPOCH FROM (NOW() - created_at))/86400) as avg_days_old
FROM feedback
GROUP BY category;

-- Create view for recent feedback
CREATE OR REPLACE VIEW recent_feedback AS
SELECT
    f.*,
    u.email as user_email,
    u.full_name as user_name,
    fc.display_name as category_name,
    fc.color as category_color
FROM feedback f
LEFT JOIN users u ON f.user_id = u.id
LEFT JOIN feedback_categories fc ON f.category = fc.name
WHERE f.created_at >= NOW() - INTERVAL '30 days'
ORDER BY f.created_at DESC;

-- Comments for documentation
COMMENT ON TABLE feedback IS 'User feedback and feature requests';
COMMENT ON TABLE feedback_attachments IS 'File attachments for feedback';
COMMENT ON TABLE feedback_votes IS 'User votes on feedback items';
COMMENT ON TABLE feedback_categories IS 'Predefined feedback categories';

COMMENT ON VIEW feedback_analytics IS 'Feedback with user and category information';
COMMENT ON VIEW feedback_stats IS 'Aggregated feedback statistics by category';
COMMENT ON VIEW recent_feedback IS 'Recent feedback from the last 30 days';

COMMENT ON COLUMN feedback.upvotes IS 'Community upvotes for feedback visibility';
COMMENT ON COLUMN feedback.is_public IS 'Whether feedback is visible to other users';
COMMENT ON COLUMN feedback.is_anonymous IS 'Whether user wants to remain anonymous';
