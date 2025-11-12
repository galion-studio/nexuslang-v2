#!/bin/bash
# IMMEDIATE RUNPOD DEPLOYMENT
# Run this on RunPod to deploy NexusLang v2 NOW

set -e

echo "🚀 DEPLOYING NEXUSLANG V2 TO RUNPOD NOW"
echo ""

cd /workspace/project-nexus

# Create complete v2/.env
cat > v2/.env << 'EOF'
# Production Environment - Complete
POSTGRES_PASSWORD=9k3mNp8rT2xQv5jL6wYz4cB1nF7dK0sA
REDIS_PASSWORD=7aHZpW9xR4mN8qL3vK6jT1yB5cZ0fG2s
SECRET_KEY=4jL9mK2pX7vN1qR8wT3yH6zB5cfP0sD4gA
JWT_SECRET=2xR7kP9mL4vN8qT3wH6yJ1zB5cfP0sG2dA9xK4pM7rL3vN8qW1tY6hJ5bC0fZ2sG
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://developer.galion.app,https://api.developer.galion.app
POSTGRES_USER=nexus
POSTGRES_DB=nexus_v2
POSTGRES_HOST=postgres
DATABASE_URL=postgresql+asyncpg://nexus:9k3mNp8rT2xQv5jL6wYz4cB1nF7dK0sA@postgres:5432/nexus_v2
REDIS_HOST=redis
REDIS_URL=redis://:7aHZpW9xR4mN8qL3vK6jT1yB5cZ0fG2s@redis:6379/0
OPENROUTER_API_KEY=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
OPENAI_API_KEY=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
AI_PROVIDER=openrouter
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
ENABLE_BILLING=false
WHISPER_DEVICE=cuda
TTS_DEVICE=cuda
ENABLE_VOICE=true
ENABLE_GROKOPEDIA=true
FREE_TIER_CREDITS=100
EOF

cat > v2/frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=https://api.developer.galion.app
NEXT_PUBLIC_WS_URL=wss://api.developer.galion.app
NEXT_PUBLIC_ENVIRONMENT=production
EOF

echo "✅ Environment created"

# Install docker-compose if needed
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo "✅ Docker Compose ready"

# Start services
cd v2
docker-compose -f ../docker-compose.prod.yml up -d --build

echo ""
echo "✅ DEPLOYMENT STARTED!"
echo "Watch logs: docker-compose -f ../docker-compose.prod.yml logs -f"
echo "RunPod IP: 213.173.105.83"
echo "Configure DNS → developer.galion.app → 213.173.105.83"

