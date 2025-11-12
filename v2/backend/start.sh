#!/bin/bash
# Start NexusLang v2 Backend
# Works on any platform (local, RunPod, cloud)

set -e

echo "🚀 Starting NexusLang v2..."
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment loaded from .env"
else
    echo "⚠️  No .env file found, using defaults"
fi

# Check required variables
if [ -z "$JWT_SECRET_KEY" ]; then
    echo "❌ ERROR: JWT_SECRET_KEY not set"
    echo "   Generate with: openssl rand -hex 64"
    exit 1
fi

# Create directories
mkdir -p logs data

echo "✅ Directories created"
echo ""

# Show configuration
echo "📊 Configuration:"
echo "   Database: ${DATABASE_URL:-sqlite+aiosqlite:///./nexuslang_dev.db}"
echo "   Redis: ${REDIS_URL:-redis://localhost:6379/1}"
echo "   Debug: ${DEBUG:-false}"
echo "   Workers: ${WORKERS:-2}"
echo ""

# Determine number of workers
WORKERS=${WORKERS:-2}

# Start server
echo "🚀 Starting server on http://0.0.0.0:8000"
echo "📍 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers $WORKERS \
    --log-level info \
    --access-log

