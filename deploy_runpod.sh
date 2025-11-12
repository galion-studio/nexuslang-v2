#!/bin/bash
# NexusLang RunPod Deployment Script
# Run with: bash deploy_runpod.sh

set -e  # Exit on any error

echo "🚀 Starting NexusLang deployment on RunPod..."

# ============================================
# Step 1: Navigate to project
# ============================================
echo "📁 Navigating to project directory..."
cd /workspace/nexuslang-v2

# ============================================
# Step 2: Create .env file
# ============================================
echo "⚙️  Creating .env file..."
cat > .env << 'EOF'
POSTGRES_USER=nexus
POSTGRES_PASSWORD=9k3mNp8rT2xQv5jL6wYz4cB1nF7dK0sA
REDIS_PASSWORD=7aH2pW9xR4mN8qL3vK6jT1yB5cZ0fG2s
SECRET_KEY=4jL9mK2pX7vN1qR8wT3yH6zB5cF0sD4gA
JWT_SECRET=2xR7kP9mL4vN8qT3wH6yJ1zB5cF0sG2dA9xK4pM7rL3vN8qW1tY6hJ5bC0fZ2sG
POSTGRES_DB=nexus_v2
OPENROUTER_API_KEY=sk-or-v1-YOUR-ACTUAL-KEY-HERE
OPENAI_API_KEY=
AI_PROVIDER=openrouter
CORS_ORIGINS=*
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_AI_MODEL=openai/gpt-4-turbo
FAST_AI_MODEL=openai/gpt-3.5-turbo
DATABASE_URL=postgresql://nexus:9k3mNp8rT2xQv5jL6wYz4cB1nF7dK0sA@localhost:5432/nexus_v2
REDIS_URL=redis://:7aH2pW9xR4mN8qL3vK6jT1yB5cF0sG2s@localhost:6379/0
EOF

# ============================================
# Step 3: Check if API key needs to be set
# ============================================
if grep -q "YOUR-ACTUAL-KEY-HERE" .env; then
    echo "⚠️  WARNING: You need to set your OPENROUTER_API_KEY in .env file"
    echo "Edit with: nano .env"
    echo ""
    read -p "Press Enter after you've added your API key, or Ctrl+C to exit..."
fi

# ============================================
# Step 4: Install system dependencies
# ============================================
echo "📦 Installing PostgreSQL and Redis..."
apt-get update -qq
apt-get install -y postgresql postgresql-contrib redis-server > /dev/null 2>&1

# ============================================
# Step 5: Start PostgreSQL
# ============================================
echo "🗄️  Starting PostgreSQL..."
service postgresql start

# ============================================
# Step 6: Create database
# ============================================
echo "🗄️  Creating database and user..."
sudo -u postgres psql << 'EOSQL'
-- Drop if exists (for clean reinstall)
DROP DATABASE IF EXISTS nexus_v2;
DROP USER IF EXISTS nexus;

-- Create fresh
CREATE DATABASE nexus_v2;
CREATE USER nexus WITH PASSWORD '9k3mNp8rT2xQv5jL6wYz4cB1nF7dK0sA';
GRANT ALL PRIVILEGES ON DATABASE nexus_v2 TO nexus;
ALTER DATABASE nexus_v2 OWNER TO nexus;
EOSQL

# ============================================
# Step 7: Enable pgvector
# ============================================
echo "🔧 Enabling pgvector extension..."
sudo -u postgres psql -d nexus_v2 << 'EOSQL'
CREATE EXTENSION IF NOT EXISTS vector;
EOSQL

# ============================================
# Step 8: Start Redis
# ============================================
echo "🔴 Starting Redis..."
redis-server --daemonize yes --requirepass 7aH2pW9xR4mN8qL3vK6jT1yB5cZ0fG2s

# ============================================
# Step 9: Install Python dependencies
# ============================================
echo "🐍 Installing Python dependencies (this takes 5-10 minutes)..."
cd /workspace/nexuslang-v2/v2/backend
pip install -r requirements.txt -q

# ============================================
# Step 10: Run migrations
# ============================================
echo "🗄️  Running database migrations..."
alembic upgrade head || echo "⚠️  Migration warning (may be OK if tables don't exist yet)"

# ============================================
# Step 11: Start backend
# ============================================
echo "🚀 Starting backend server..."
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/nexus-backend.log 2>&1 &
BACKEND_PID=$!

# ============================================
# Step 12: Wait and test
# ============================================
echo "⏳ Waiting for backend to start..."
sleep 10

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 Deployment successful!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📍 Access your app at:"
    echo "   API:    http://$(curl -s ifconfig.me):8000"
    echo "   Docs:   http://$(curl -s ifconfig.me):8000/docs"
    echo "   Health: http://$(curl -s ifconfig.me):8000/health"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:    tail -f /tmp/nexus-backend.log"
    echo "   Stop backend: pkill -f uvicorn"
    echo "   Restart:      bash deploy_runpod.sh"
    echo ""
else
    echo "❌ Backend failed to start. Check logs:"
    echo "   tail -f /tmp/nexus-backend.log"
    exit 1
fi

