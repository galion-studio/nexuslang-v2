-- 005_document_verification.sql
-- Document Verification System - First Principles Approach
-- Created: November 9, 2025

-- Document Types Table
CREATE TABLE IF NOT EXISTS document_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    required_for_verification BOOLEAN DEFAULT false,
    max_file_size_mb INTEGER DEFAULT 10,
    allowed_formats VARCHAR(255) DEFAULT 'pdf,jpg,png,jpeg',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_type_id INTEGER NOT NULL REFERENCES document_types(id),
    
    -- File information
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'expired')),
    
    -- Review information
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Timestamps
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Additional metadata (JSON for flexibility)
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type_id);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at ON documents(uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_reviewed_by ON documents(reviewed_by);

-- Insert default document types
INSERT INTO document_types (name, description, required_for_verification, max_file_size_mb, allowed_formats) VALUES
('government_id', 'Government-issued ID (Passport, Driver License, National ID)', true, 10, 'pdf,jpg,png,jpeg'),
('proof_of_address', 'Proof of address (Utility bill, Bank statement)', true, 10, 'pdf,jpg,png,jpeg'),
('selfie', 'Selfie photo for identity verification', true, 5, 'jpg,png,jpeg'),
('business_registration', 'Business registration document', false, 10, 'pdf'),
('tax_id', 'Tax identification document', false, 10, 'pdf,jpg,png'),
('bank_statement', 'Bank account statement', false, 10, 'pdf'),
('other', 'Other supporting documents', false, 10, 'pdf,jpg,png,jpeg')
ON CONFLICT (name) DO NOTHING;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_documents_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
DROP TRIGGER IF EXISTS trigger_documents_updated_at ON documents;
CREATE TRIGGER trigger_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_documents_updated_at();

-- Comments for documentation
COMMENT ON TABLE documents IS 'User uploaded documents for verification';
COMMENT ON TABLE document_types IS 'Types of documents that can be uploaded';
COMMENT ON COLUMN documents.status IS 'Document verification status: pending, approved, rejected, expired';
COMMENT ON COLUMN documents.metadata IS 'Additional document metadata in JSON format';

