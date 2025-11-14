-- Migration: Voice Sessions and Commands
-- Description: Adds tables for voice session tracking and command analytics
-- Version: 003
-- Date: 2025-11-14

-- Voice sessions table
CREATE TABLE IF NOT EXISTS voice_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('galion-app', 'developer-platform', 'galion-studio')),
    session_type VARCHAR(20) DEFAULT 'conversation' CHECK (session_type IN ('conversation', 'command', 'tutorial')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    commands_count INTEGER DEFAULT 0,
    transcription_accuracy FLOAT CHECK (transcription_accuracy >= 0 AND transcription_accuracy <= 1),
    credits_used INTEGER DEFAULT 0,
    total_audio_bytes INTEGER DEFAULT 0,
    language VARCHAR(10) DEFAULT 'en',
    client_info JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_voice_sessions_user_id ON voice_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_platform ON voice_sessions(platform);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_started_at ON voice_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_created_at ON voice_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_user_started ON voice_sessions(user_id, started_at);

-- Voice commands table
CREATE TABLE IF NOT EXISTS voice_commands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES voice_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transcription TEXT NOT NULL,
    transcription_confidence FLOAT CHECK (transcription_confidence >= 0 AND transcription_confidence <= 1),
    intent VARCHAR(100),
    response_text TEXT,
    response_audio_url VARCHAR(500),
    credits_used INTEGER DEFAULT 1,
    processing_time_ms INTEGER,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_voice_commands_session_id ON voice_commands(session_id);
CREATE INDEX IF NOT EXISTS idx_voice_commands_user_id ON voice_commands(user_id);
CREATE INDEX IF NOT EXISTS idx_voice_commands_created_at ON voice_commands(created_at);
CREATE INDEX IF NOT EXISTS idx_voice_commands_user_session ON voice_commands(user_id, session_id);

-- Function to update session statistics when commands are added
CREATE OR REPLACE FUNCTION update_voice_session_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update commands count and credits
    UPDATE voice_sessions
    SET
        commands_count = commands_count + 1,
        credits_used = credits_used + COALESCE(NEW.credits_used, 1),
        updated_at = NOW()
    WHERE id = NEW.session_id;

    -- Update transcription accuracy (moving average)
    UPDATE voice_sessions
    SET transcription_accuracy = CASE
        WHEN transcription_accuracy IS NULL THEN NEW.transcription_confidence
        ELSE (transcription_accuracy * 0.7) + (COALESCE(NEW.transcription_confidence, 0.8) * 0.3)
    END
    WHERE id = NEW.session_id AND NEW.transcription_confidence IS NOT NULL;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to maintain session statistics
CREATE TRIGGER trigger_update_voice_session_stats
    AFTER INSERT ON voice_commands
    FOR EACH ROW
    EXECUTE FUNCTION update_voice_session_stats();

-- Function to calculate session duration when ended
CREATE OR REPLACE FUNCTION calculate_session_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ended_at IS NOT NULL AND OLD.ended_at IS NULL THEN
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.ended_at - OLD.started_at))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to calculate duration when session ends
CREATE TRIGGER trigger_calculate_session_duration
    BEFORE UPDATE ON voice_sessions
    FOR EACH ROW
    WHEN (OLD.ended_at IS NULL AND NEW.ended_at IS NOT NULL)
    EXECUTE FUNCTION calculate_session_duration();

-- Function to validate session data
CREATE OR REPLACE FUNCTION validate_voice_session()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure ended_at is after started_at
    IF NEW.ended_at IS NOT NULL AND NEW.ended_at <= NEW.started_at THEN
        RAISE EXCEPTION 'ended_at must be after started_at';
    END IF;

    -- Ensure duration is reasonable (max 8 hours)
    IF NEW.duration_seconds IS NOT NULL AND NEW.duration_seconds > 28800 THEN
        RAISE EXCEPTION 'Session duration cannot exceed 8 hours';
    END IF;

    -- Ensure transcription accuracy is valid
    IF NEW.transcription_accuracy IS NOT NULL AND
       (NEW.transcription_accuracy < 0 OR NEW.transcription_accuracy > 1) THEN
        RAISE EXCEPTION 'Transcription accuracy must be between 0 and 1';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to validate session data
CREATE TRIGGER trigger_validate_voice_session
    BEFORE INSERT OR UPDATE ON voice_sessions
    FOR EACH ROW
    EXECUTE FUNCTION validate_voice_session();

-- Function to validate command data
CREATE OR REPLACE FUNCTION validate_voice_command()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure transcription confidence is valid
    IF NEW.transcription_confidence IS NOT NULL AND
       (NEW.transcription_confidence < 0 OR NEW.transcription_confidence > 1) THEN
        RAISE EXCEPTION 'Transcription confidence must be between 0 and 1';
    END IF;

    -- Ensure processing time is reasonable (max 30 seconds)
    IF NEW.processing_time_ms IS NOT NULL AND NEW.processing_time_ms > 30000 THEN
        RAISE EXCEPTION 'Processing time cannot exceed 30 seconds';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to validate command data
CREATE TRIGGER trigger_validate_voice_command
    BEFORE INSERT OR UPDATE ON voice_commands
    FOR EACH ROW
    EXECUTE FUNCTION validate_voice_command();

-- Create a view for session analytics
CREATE OR REPLACE VIEW voice_session_analytics AS
SELECT
    vs.id,
    vs.user_id,
    vs.platform,
    vs.session_type,
    vs.started_at,
    vs.ended_at,
    vs.duration_seconds,
    vs.commands_count,
    vs.transcription_accuracy,
    vs.credits_used,
    vs.language,
    CASE
        WHEN vs.duration_seconds > 0 THEN vs.commands_count::FLOAT / vs.duration_seconds
        ELSE 0
    END as commands_per_second,
    CASE
        WHEN vs.commands_count > 0 THEN vs.credits_used::FLOAT / vs.commands_count
        ELSE 0
    END as avg_credits_per_command,
    u.email as user_email,
    u.full_name as user_name
FROM voice_sessions vs
JOIN users u ON vs.user_id = u.id;

-- Create a view for daily voice usage
CREATE OR REPLACE VIEW daily_voice_usage AS
SELECT
    DATE(started_at) as date,
    platform,
    COUNT(*) as sessions_count,
    COUNT(DISTINCT user_id) as unique_users,
    SUM(commands_count) as total_commands,
    SUM(credits_used) as total_credits,
    AVG(transcription_accuracy) as avg_accuracy,
    SUM(duration_seconds) as total_duration_seconds,
    AVG(duration_seconds) as avg_session_duration
FROM voice_sessions
WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(started_at), platform
ORDER BY date DESC, platform;

-- Comments for documentation
COMMENT ON TABLE voice_sessions IS 'Voice interaction sessions with metadata and analytics';
COMMENT ON TABLE voice_commands IS 'Individual voice commands within sessions';
COMMENT ON VIEW voice_session_analytics IS 'Combined view of sessions with user information';
COMMENT ON VIEW daily_voice_usage IS 'Daily aggregated voice usage statistics';

COMMENT ON COLUMN voice_sessions.transcription_accuracy IS 'Average transcription accuracy (0.0-1.0)';
COMMENT ON COLUMN voice_sessions.credits_used IS 'Total credits consumed in session';
COMMENT ON COLUMN voice_commands.transcription_confidence IS 'Confidence score for transcription (0.0-1.0)';
COMMENT ON COLUMN voice_commands.processing_time_ms IS 'Time taken to process command in milliseconds';
