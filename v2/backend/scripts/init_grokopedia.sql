-- Initialize Grokopedia Database
-- Run this script to set up all knowledge base tables and seed data

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- Create knowledge_entries table
CREATE TABLE IF NOT EXISTS knowledge_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    summary TEXT,
    content TEXT NOT NULL,
    embeddings vector(1536),
    tags TEXT[] DEFAULT '{}',
    verified BOOLEAN DEFAULT FALSE,
    verified_by UUID,
    verified_at TIMESTAMP WITH TIME ZONE,
    views_count INTEGER DEFAULT 0,
    upvotes_count INTEGER DEFAULT 0,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create knowledge_graph table
CREATE TABLE IF NOT EXISTS knowledge_graph (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES knowledge_entries(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES knowledge_entries(id) ON DELETE CASCADE,
    relationship VARCHAR(50) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(source_id, target_id, relationship)
);

-- Create contributions table
CREATE TABLE IF NOT EXISTS contributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID NOT NULL REFERENCES knowledge_entries(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    type VARCHAR(20) NOT NULL,
    changes JSONB DEFAULT '{}'::jsonb,
    approved BOOLEAN DEFAULT FALSE,
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_title ON knowledge_entries(title);
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_slug ON knowledge_entries(slug);
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_verified ON knowledge_entries(verified);
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_created_by ON knowledge_entries(created_by);
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_created_at ON knowledge_entries(created_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_embeddings ON knowledge_entries USING ivfflat (embeddings vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_knowledge_graph_source_id ON knowledge_graph(source_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_graph_target_id ON knowledge_graph(target_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_graph_relationship ON knowledge_graph(relationship);

CREATE INDEX IF NOT EXISTS idx_contributions_entry_id ON contributions(entry_id);
CREATE INDEX IF NOT EXISTS idx_contributions_user_id ON contributions(user_id);
CREATE INDEX IF NOT EXISTS idx_contributions_type ON contributions(type);
CREATE INDEX IF NOT EXISTS idx_contributions_approved ON contributions(approved);
CREATE INDEX IF NOT EXISTS idx_contributions_created_at ON contributions(created_at);

-- Create update trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER update_knowledge_entries_updated_at
    BEFORE UPDATE ON knowledge_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO knowledge_entries (
    title, slug, summary, content, tags, verified, views_count, upvotes_count
) VALUES
(
    'Artificial Intelligence',
    'artificial-intelligence',
    'A field of computer science focused on creating systems capable of performing tasks that typically require human intelligence.',
    'Artificial Intelligence (AI) is a multidisciplinary field that encompasses computer science, mathematics, psychology, linguistics, and neuroscience. It focuses on creating systems that can perform tasks requiring human-like intelligence such as visual perception, speech recognition, decision-making, and language translation.

## Key Concepts

### Machine Learning
A subset of AI that enables systems to automatically learn and improve from experience without being explicitly programmed. Machine learning algorithms build mathematical models based on training data to make predictions or decisions.

### Deep Learning
A subset of machine learning that uses artificial neural networks with multiple layers (deep neural networks) to model complex patterns in data. Deep learning has revolutionized fields like computer vision, natural language processing, and speech recognition.

### Natural Language Processing (NLP)
The ability of computers to understand, interpret, and generate human language. Modern NLP systems use transformer architectures and large language models to achieve human-like language understanding.

## Applications

- **Healthcare**: Diagnostic assistance, drug discovery, personalized medicine
- **Finance**: Fraud detection, algorithmic trading, risk assessment
- **Transportation**: Autonomous vehicles, route optimization, predictive maintenance
- **Entertainment**: Content recommendation, game AI, creative tools

## Ethical Considerations

As AI systems become more powerful, important ethical questions arise:
- Privacy and data protection
- Algorithmic bias and fairness
- Job displacement and economic impact
- Autonomous weapons and military applications
- AI safety and alignment with human values',
    ARRAY['artificial-intelligence', 'machine-learning', 'technology', 'computer-science'],
    TRUE,
    150,
    45
),
(
    'Quantum Computing',
    'quantum-computing',
    'A revolutionary computing paradigm that uses quantum mechanics principles to perform calculations impossible on classical computers.',
    'Quantum computing represents a fundamental shift from classical computing by harnessing the principles of quantum mechanics to perform computations that would be impossible or impractical on traditional computers.

## Core Principles

### Quantum Bits (Qubits)
Unlike classical bits that exist in states of 0 or 1, qubits can exist in superposition - simultaneously representing both 0 and 1. This property allows quantum computers to process vast amounts of data in parallel.

### Entanglement
A quantum phenomenon where particles become correlated such that the state of one particle instantly influences the state of another, regardless of distance. This property enables quantum computers to perform complex correlations.

## Applications

- **Cryptography**: Breaking current encryption, enabling quantum-safe cryptography
- **Drug Discovery**: Simulating molecular interactions at quantum level
- **Optimization**: Solving complex optimization problems in logistics, finance, and materials science
- **Machine Learning**: Quantum machine learning algorithms with potential exponential speedups',
    ARRAY['quantum-computing', 'physics', 'technology', 'cryptography'],
    TRUE,
    120,
    38
),
(
    'Machine Learning',
    'machine-learning',
    'A subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.',
    'Machine Learning (ML) is a powerful approach to artificial intelligence that allows systems to automatically learn patterns and make decisions from data, without being explicitly programmed for each specific task.

## Learning Paradigms

### Supervised Learning
The most common ML approach where algorithms learn from labeled training data. The system is provided with input-output pairs and learns to map inputs to correct outputs.

### Unsupervised Learning
Algorithms discover hidden patterns in data without labeled examples. The system finds structure and relationships in the data itself.

### Reinforcement Learning
Learning through interaction with an environment, receiving rewards or penalties for actions. The system learns optimal behavior through trial and error.

## Applications

- Computer vision and image recognition
- Natural language processing and text analysis
- Predictive analytics and forecasting
- Recommendation systems
- Fraud detection and cybersecurity',
    ARRAY['machine-learning', 'artificial-intelligence', 'data-science', 'algorithms'],
    TRUE,
    200,
    67
),
(
    'Blockchain Technology',
    'blockchain-technology',
    'A decentralized, distributed ledger technology that maintains a continuously growing list of records secured by cryptography.',
    'Blockchain technology is a decentralized, distributed ledger system that maintains a continuously growing list of records (blocks) that are cryptographically linked and secured. It enables secure, transparent, and immutable transactions without requiring a central authority.

## Core Components

### Blocks
Containers that hold batches of valid transactions. Each block contains:
- Block Header: Metadata including previous block hash, timestamp, nonce
- Transaction List: Valid transactions included in the block
- Merkle Root: Cryptographic hash of all transactions in the block

### Consensus Mechanisms
- **Proof-of-Work (PoW)**: Used by Bitcoin and many other cryptocurrencies
- **Proof-of-Stake (PoS)**: More energy-efficient alternative
- **Delegated Proof-of-Stake (DPoS)**: Stakeholders elect delegates

## Applications

- **Cryptocurrency**: Bitcoin, Ethereum, and other digital currencies
- **Smart Contracts**: Self-executing contracts with terms directly written into code
- **Supply Chain Management**: End-to-end supply chain visibility
- **Identity Management**: Decentralized digital identities
- **Voting Systems**: Secure, transparent, tamper-proof voting',
    ARRAY['blockchain', 'cryptocurrency', 'distributed-systems', 'cryptography'],
    TRUE,
    180,
    52
),
(
    'Neural Networks',
    'neural-networks',
    'Computing systems inspired by biological neural networks, capable of learning complex patterns through interconnected nodes.',
    'Neural networks are computational models inspired by the structure and function of biological neural networks in the human brain. They form the foundation of deep learning and have revolutionized artificial intelligence.

## Basic Structure
- **Input Layer**: Receives raw data
- **Hidden Layers**: Process and transform data through learned representations
- **Output Layer**: Produces final predictions or classifications

## Training Process
- **Forward Propagation**: Data flows from input to output layer
- **Loss Function**: Measures the difference between predictions and actual targets
- **Backpropagation**: Algorithm for computing gradients of the loss function
- **Gradient Descent**: Optimization algorithm for updating network weights

## Applications
- Computer vision and image processing
- Natural language processing and understanding
- Speech recognition and synthesis
- Game playing and strategy
- Medical diagnosis and analysis',
    ARRAY['neural-networks', 'deep-learning', 'artificial-intelligence', 'machine-learning'],
    TRUE,
    135,
    41
)
ON CONFLICT (slug) DO NOTHING;

-- Create some knowledge graph relationships
INSERT INTO knowledge_graph (source_id, target_id, relationship, weight) VALUES
(
    (SELECT id FROM knowledge_entries WHERE slug = 'artificial-intelligence'),
    (SELECT id FROM knowledge_entries WHERE slug = 'machine-learning'),
    'related_to',
    0.9
),
(
    (SELECT id FROM knowledge_entries WHERE slug = 'artificial-intelligence'),
    (SELECT id FROM knowledge_entries WHERE slug = 'neural-networks'),
    'related_to',
    0.8
),
(
    (SELECT id FROM knowledge_entries WHERE slug = 'machine-learning'),
    (SELECT id FROM knowledge_entries WHERE slug = 'neural-networks'),
    'part_of',
    0.7
)
ON CONFLICT (source_id, target_id, relationship) DO NOTHING;
