#!/bin/bash

# NexusLang v2 - RunPod Deployment Script
# Automated deployment to RunPod instance

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════╗"
echo "║  NexusLang v2 - RunPod Deployment                      ║"
echo "║  Automated setup for cloud development environment     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if running on RunPod (basic check)
echo "📍 Checking environment..."
if [ ! -f "/.dockerenv" ] && [ ! -d "/workspace" ]; then
    echo "⚠️  Warning: This script is designed for RunPod environments"
    echo "   You can still run it, but some assumptions may not hold"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system packages
echo ""
echo "📦 Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo ""
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo ""
    echo "🔧 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose already installed"
fi

# Verify installations
echo ""
echo "🔍 Verifying installations..."
docker --version
docker-compose --version

# Navigate to project root
cd "$(dirname "$0")/../../.."

echo ""
echo "📂 Project directory: $(pwd)"

# Generate secrets
echo ""
echo "🔐 Generating secure secrets..."
JWT_SECRET=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)

# Create environment file
echo ""
echo "⚙️  Creating environment configuration..."
cat > v2/backend/.env << EOF
# NexusLang v2 - Production Environment
# Generated: $(date)

# Application
APP_NAME=NexusLang v2 API
DEBUG=false
ENVIRONMENT=production

# Security
SECRET_KEY=${SECRET_KEY}
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database
DATABASE_URL=postgresql://nexus:${POSTGRES_PASSWORD}@postgres:5432/nexuslang_v2
POSTGRES_USER=nexus
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=nexuslang_v2

# Redis
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
REDIS_PASSWORD=${REDIS_PASSWORD}

# CORS (allow all for testing)
CORS_ORIGINS=["*"]

# OpenAI (optional)
OPENAI_API_KEY=${OPENAI_API_KEY:-}
EOF

echo "✅ Environment file created"

# Create docker-compose override for RunPod
cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  postgres:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  
  redis:
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 1gb --maxmemory-policy allkeys-lru --appendonly yes
  
  backend:
    environment:
      DATABASE_URL: postgresql://nexus:${POSTGRES_PASSWORD}@postgres:5432/nexuslang_v2
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
  
  frontend:
    environment:
      NEXT_PUBLIC_API_URL: http://0.0.0.0:8000
EOF

echo "✅ Docker Compose override created"

# Pull images
echo ""
echo "📥 Pulling Docker images..."
docker-compose pull

# Build services
echo ""
echo "🔨 Building services..."
docker-compose build

# Start services
echo ""
echo "🚀 Starting NexusLang v2 Platform..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check status
echo ""
echo "📊 Service Status:"
docker-compose ps

# Test backend health
echo ""
echo "🏥 Testing backend health..."
sleep 5
curl -f http://localhost:8000/health || echo "⚠️  Backend not responding yet (may need more time)"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  ✅ DEPLOYMENT COMPLETE!                                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Your NexusLang v2 Platform is running!"
echo ""
echo "Access points:"
echo "  Frontend:  http://<your-runpod-ip>:3000"
echo "  Backend:   http://<your-runpod-ip>:8000"
echo "  API Docs:  http://<your-runpod-ip>:8000/docs"
echo ""
echo "📋 Next steps:"
echo "  1. Get your RunPod public IP from dashboard"
echo "  2. Visit http://<your-ip>:3000/ide"
echo "  3. Register an account"
echo "  4. Start coding!"
echo ""
echo "🔧 Useful commands:"
echo "  View logs:     docker-compose logs -f"
echo "  Restart:       docker-compose restart"
echo "  Stop:          docker-compose down"
echo "  Check status:  docker-compose ps"
echo ""
echo "🎉 Happy coding with NexusLang v2!"

