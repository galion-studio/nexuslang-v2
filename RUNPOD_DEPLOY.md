# NexusLang RunPod Deployment Guide

## Quick Deploy Commands

Copy and paste these commands into your RunPod terminal:

```bash
# ============================================
# STEP 1: Navigate to project
# ============================================
cd /workspace/nexuslang-v2

# ============================================
# STEP 2: Create proper .env file
# ============================================
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
REDIS_URL=redis://:7aH2pW9xR4mN8qL3vK6jT1yB5cZ0fG2s@localhost:6379/0
EOF

# ============================================
# STEP 3: Edit .env to add your real API key
# ============================================
nano .env
# Press Ctrl+X, then Y, then Enter to save

# ============================================
# STEP 4: Install PostgreSQL and Redis
# ============================================
apt-get update
apt-get install -y postgresql postgresql-contrib redis-server

# ============================================
# STEP 5: Start PostgreSQL
# ============================================
service postgresql start

# ============================================
# STEP 6: Create database and user
# ============================================
sudo -u postgres psql << 'EOSQL'
CREATE DATABASE nexus_v2;
CREATE USER nexus WITH PASSWORD '9k3mNp8rT2xQv5jL6wYz4cB1nF7dK0sA';
GRANT ALL PRIVILEGES ON DATABASE nexus_v2 TO nexus;
\q
EOSQL

# ============================================
# STEP 7: Enable pgvector extension
# ============================================
sudo -u postgres psql -d nexus_v2 << 'EOSQL'
CREATE EXTENSION IF NOT EXISTS vector;
\q
EOSQL

# ============================================
# STEP 8: Start Redis
# ============================================
redis-server --daemonize yes --requirepass 7aH2pW9xR4mN8qL3vK6jT1yB5cZ0fG2s

# ============================================
# STEP 9: Install Python dependencies
# ============================================
cd /workspace/nexuslang-v2/v2/backend
pip install -r requirements.txt

# This will take 5-10 minutes...
# Wait for it to complete

# ============================================
# STEP 10: Run database migrations
# ============================================
alembic upgrade head

# ============================================
# STEP 11: Start the backend
# ============================================
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &

# ============================================
# STEP 12: Wait and test
# ============================================
sleep 5
curl http://localhost:8000/health

# ============================================
# STEP 13: Check if it's running
# ============================================
curl http://localhost:8000/docs
```

## Troubleshooting

### If backend fails to start:
```bash
# Check logs
tail -f /tmp/backend.log

# Or run in foreground to see errors
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### If PostgreSQL fails:
```bash
# Check if PostgreSQL is running
service postgresql status

# Restart if needed
service postgresql restart
```

### If Redis fails:
```bash
# Check if Redis is running
redis-cli -a 7aH2pW9xR4mN8qL3vK6jT1yB5cZ0fG2s ping

# Should return PONG
```

## Accessing Your App

Once running, your backend will be available at:
- API: `http://your-runpod-ip:8000`
- Docs: `http://your-runpod-ip:8000/docs`
- Health: `http://your-runpod-ip:8000/health`

## Keeping Backend Running

To keep backend running even if you disconnect:
```bash
# Stop the current background process
pkill -f uvicorn

# Start with nohup
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &

# View logs
tail -f /tmp/backend.log
```

