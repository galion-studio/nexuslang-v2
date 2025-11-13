-- Knowledge Base Migration for Grokopedia
-- Version: 4.0.0
-- Created: November 13, 2025
-- Description: Adds knowledge_entries, knowledge_graph, and contributions tables

-- ============================================================
-- KNOWLEDGE ENTRIES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS knowledge_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    summary TEXT,
    content TEXT NOT NULL,
    embeddings vector(1536),  -- OpenAI embedding dimension
    tags TEXT[] DEFAULT '{}',
    verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    views_count INTEGER DEFAULT 0,
    upvotes_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for knowledge_entries
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_title ON knowledge_entries(title);
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_slug ON knowledge_entries(slug);
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_verified ON knowledge_entries(verified);
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_created_by ON knowledge_entries(created_by);
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_created_at ON knowledge_entries(created_at);
-- Vector similarity search index (requires pgvector)
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_embeddings ON knowledge_entries USING ivfflat (embeddings vector_cosine_ops);

-- ============================================================
-- KNOWLEDGE GRAPH TABLE (Relationships between entries)
-- ============================================================
CREATE TABLE IF NOT EXISTS knowledge_graph (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES knowledge_entries(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES knowledge_entries(id) ON DELETE CASCADE,
    relationship VARCHAR(50) NOT NULL,  -- related_to, part_of, prerequisite, similar_to, opposite_of
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(source_id, target_id, relationship)
);

-- Indexes for knowledge_graph
CREATE INDEX IF NOT EXISTS idx_knowledge_graph_source_id ON knowledge_graph(source_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_graph_target_id ON knowledge_graph(target_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_graph_relationship ON knowledge_graph(relationship);

-- ============================================================
-- CONTRIBUTIONS TABLE (Track edits and contributions)
-- ============================================================
CREATE TABLE IF NOT EXISTS contributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID NOT NULL REFERENCES knowledge_entries(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,  -- create, edit, verify, comment
    changes JSONB DEFAULT '{}'::jsonb,
    approved BOOLEAN DEFAULT FALSE,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for contributions
CREATE INDEX IF NOT EXISTS idx_contributions_entry_id ON contributions(entry_id);
CREATE INDEX IF NOT EXISTS idx_contributions_user_id ON contributions(user_id);
CREATE INDEX IF NOT EXISTS idx_contributions_type ON contributions(type);
CREATE INDEX IF NOT EXISTS idx_contributions_approved ON contributions(approved);
CREATE INDEX IF NOT EXISTS idx_contributions_created_at ON contributions(created_at);

-- ============================================================
-- UPDATE TRIGGERS
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
CREATE TRIGGER update_knowledge_entries_updated_at
    BEFORE UPDATE ON knowledge_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- INITIAL SEED DATA (Optional - will be seeded by scripts)
-- ============================================================

-- Insert sample knowledge entry (will be replaced by proper seeding)
INSERT INTO knowledge_entries (
    title, slug, summary, content, tags, verified, views_count, upvotes_count
) VALUES (
    'Welcome to Grokopedia',
    'welcome-to-grokopedia',
    'Introduction to the universal AI knowledge base',
    'Grokopedia is a comprehensive knowledge base powered by AI, featuring semantic search, collaborative editing, and intelligent relationships between concepts.',
    ARRAY['grokopedia', 'introduction', 'ai', 'knowledge-base'],
    TRUE,
    100,
    50
) ON CONFLICT (slug) DO NOTHING;

-- ============================================================
-- MIGRATION COMPLETE
-- ============================================================
-- Version: 004_knowledge_tables.sql
-- Description: Knowledge base tables for Grokopedia
-- Status: ✅ Complete
