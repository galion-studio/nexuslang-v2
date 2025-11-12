#!/bin/bash
# Deploy BOTH Galion platforms on RunPod
# developer.galion.app + galion.studio

set -e

echo "🚀 DEPLOYING COMPLETE GALION ECOSYSTEM"
echo ""

cd /workspace/project-nexus

# Create complete environment if not exists
if [ ! -f "v2/.env" ]; then
    echo "Creating v2/.env..."
    cat > v2/.env << 'EOF'
POSTGRES_PASSWORD=9k3mNp8rT2xQv5jL6wYz4cB1nF7dK0sA
REDIS_PASSWORD=7aHZpW9xR4mN8qL3vK6jT1yB5cZ0fG2s
SECRET_KEY=4jL9mK2pX7vN1qR8wT3yH6zB5cfP0sD4gA
JWT_SECRET=2xR7kP9mL4vN8qT3wH6yJ1zB5cfP0sG2dA9xK4pM7rL3vN8qW1tY6hJ5bC0fZ2sG
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://developer.galion.app,https://api.developer.galion.app,https://galion.studio
POSTGRES_USER=nexus
POSTGRES_DB=nexus_v2
DATABASE_URL=postgresql+asyncpg://nexus:9k3mNp8rT2xQv5jL6wYz4cB1nF7dK0sA@postgres:5432/nexus_v2
REDIS_URL=redis://:7aHZpW9xR4mN8qL3vK6jT1yB5cZ0fG2s@redis:6379/0
OPENROUTER_API_KEY=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
OPENAI_API_KEY=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
AI_PROVIDER=openrouter
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
ENABLE_BILLING=false
WHISPER_DEVICE=cuda
TTS_DEVICE=cuda
ENABLE_VOICE=true
FREE_TIER_CREDITS=100
EOF
fi

# Stop current services if running
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Deploy BOTH platforms
echo "Building and starting all services..."
docker-compose -f docker-compose.both-platforms.yml up -d --build

echo ""
echo "✅ DEPLOYING BOTH PLATFORMS!"
echo ""
echo "Services:"
echo "  Backend:     http://localhost:8000"
echo "  Developer:   http://localhost:3000"
echo "  Studio:      http://localhost:3001"
echo ""
echo "Watch progress:"
echo "  docker-compose -f docker-compose.both-platforms.yml logs -f"
echo ""
echo "RunPod IP: $(curl -s ifconfig.me)"
echo ""
echo "Configure Cloudflare DNS:"
echo "  developer.galion.app → YOUR_IP"
echo "  galion.studio → YOUR_IP"
echo "  api.developer → YOUR_IP"
echo ""

