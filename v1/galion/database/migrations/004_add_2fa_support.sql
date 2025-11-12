-- Add 2FA/TOTP support to users table (GitHub-style two-factor authentication)
-- This migration adds fields for TOTP secrets, backup codes, and 2FA status

-- Add 2FA columns to users table
ALTER TABLE public.users
    ADD COLUMN IF NOT EXISTS totp_enabled BOOLEAN DEFAULT false,
    ADD COLUMN IF NOT EXISTS totp_secret VARCHAR(32),  -- Base32 encoded secret for TOTP
    ADD COLUMN IF NOT EXISTS totp_verified_at TIMESTAMP WITH TIME ZONE,  -- When user completed 2FA setup
    ADD COLUMN IF NOT EXISTS backup_codes JSONB DEFAULT '[]',  -- Encrypted backup/recovery codes
    ADD COLUMN IF NOT EXISTS backup_codes_generated_at TIMESTAMP WITH TIME ZONE;

-- Add comments for documentation
COMMENT ON COLUMN public.users.totp_enabled IS 'Whether TOTP two-factor authentication is enabled for this user';
COMMENT ON COLUMN public.users.totp_secret IS 'Base32-encoded TOTP secret key (keep secure!)';
COMMENT ON COLUMN public.users.totp_verified_at IS 'Timestamp when user successfully set up and verified 2FA';
COMMENT ON COLUMN public.users.backup_codes IS 'Array of hashed backup codes for account recovery';
COMMENT ON COLUMN public.users.backup_codes_generated_at IS 'When backup codes were last generated';

-- Create index for 2FA lookups
CREATE INDEX IF NOT EXISTS idx_users_totp_enabled ON public.users(totp_enabled) WHERE totp_enabled = true;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '2FA support added to users table successfully';
END $$;


