#!/bin/bash
# NexusLang v2 - RunPod Quick Deploy

set -e
echo "🚀 NexusLang v2 - RunPod Deploy"

# Generate .env if missing
if [ ! -f ".env" ]; then
    echo "📝 Generating .env..."
    cat > .env << EOF
POSTGRES_USER=nexus
POSTGRES_PASSWORD=$(openssl rand -hex 32)
POSTGRES_DB=nexus_v2
REDIS_PASSWORD=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 64)
GRAFANA_PASSWORD=$(openssl rand -base64 16)

# AI Configuration - ADD YOUR KEYS
OPENROUTER_API_KEY=
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_AI_MODEL=openai/gpt-4-turbo
FAST_AI_MODEL=openai/gpt-3.5-turbo
AI_PROVIDER=openrouter
OPENAI_API_KEY=

CORS_ORIGINS=*
EOF
    echo "⚠️  ADD YOUR API KEYS TO .env!"
fi

# Install Docker if needed
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
fi

if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Start services
echo "🔨 Starting services..."
docker-compose -f docker-compose.runpod.yml up -d --build

# Wait for health
sleep 10

echo ""
echo "✅ DEPLOYED!"
echo ""
echo "🌐 URLs:"
echo "  API: https://${HOSTNAME}-8000.proxy.runpod.net"
echo "  Docs: https://${HOSTNAME}-8000.proxy.runpod.net/docs"
echo "  Frontend: https://${HOSTNAME}-3000.proxy.runpod.net"
echo ""
echo "⚠️  NEXT: Edit .env and add OPENROUTER_API_KEY"
echo "   Get key: https://openrouter.ai/keys"
echo "   Then run: docker-compose restart backend"

