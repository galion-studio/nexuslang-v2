#!/bin/bash

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║           NexusLang v2 - RunPod Deployment Script with AI Router            ║
# ║                      Quick Deploy to RunPod Cloud                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -e  # Exit on error

echo ""
echo "🚀 NexusLang v2 - RunPod Deployment"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if running on RunPod
if [ -z "$RUNPOD_POD_ID" ] && [ -z "$HOSTNAME" ]; then
    echo -e "${YELLOW}⚠️  Warning: Not detected as RunPod environment${NC}"
    echo "   Continuing anyway..."
fi

# Step 1: Setup Environment
echo -e "${CYAN}📋 Step 1: Setting up environment...${NC}"

# Create workspace directories
mkdir -p /workspace/nexus-data
mkdir -p /workspace/nexus-logs
mkdir -p /workspace/models

# Copy .env or use generated one
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Generating one...${NC}"
    
    # Generate secure passwords
    POSTGRES_PASS=$(openssl rand -hex 32)
    REDIS_PASS=$(openssl rand -hex 32)
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 64)
    GRAFANA_PASS=$(openssl rand -base64 16)
    
    cat > .env << EOF
# NexusLang v2 - RunPod Configuration
# Generated: $(date)

# Database
POSTGRES_USER=nexus
POSTGRES_PASSWORD=$POSTGRES_PASS
POSTGRES_DB=nexus_v2
DATABASE_URL=postgresql://nexus:$POSTGRES_PASS@postgres:5432/nexus_v2

# Redis
REDIS_PASSWORD=$REDIS_PASS
REDIS_URL=redis://:$REDIS_PASS@redis:6379/0

# Security
SECRET_KEY=$SECRET_KEY
JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256

# AI Configuration (REQUIRED)
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_AI_MODEL=openai/gpt-4-turbo
FAST_AI_MODEL=openai/gpt-3.5-turbo
AI_PROVIDER=openrouter

# OpenAI (Optional - for fallback)
OPENAI_API_KEY=

# Monitoring
GRAFANA_PASSWORD=$GRAFANA_PASS

# RunPod Specific
RUNPOD_POD_ID=${HOSTNAME}
CORS_ORIGINS=*
EOF

    echo -e "${GREEN}✅ Generated .env file${NC}"
    echo -e "${YELLOW}"
    echo "⚠️  IMPORTANT: Add your OpenRouter API key to .env:"
    echo "   Edit .env and set: OPENROUTER_API_KEY=sk-or-your-key-here"
    echo ""
    echo "   Get your key from: https://openrouter.ai/keys"
    echo -e "${NC}"
fi

# Step 2: Install Docker if needed
echo -e "${CYAN}📦 Step 2: Checking Docker...${NC}"

if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✅ Docker Compose already installed${NC}"
fi

# Step 3: Build and Start Services
echo -e "${CYAN}🔨 Step 3: Building and starting services...${NC}"

# Use RunPod-specific docker-compose
if [ -f "docker-compose.runpod.yml" ]; then
    echo "Using docker-compose.runpod.yml..."
    docker-compose -f docker-compose.runpod.yml up -d --build
else
    echo "Using docker-compose.yml..."
    docker-compose up -d --build
fi

echo -e "${GREEN}✅ Services started${NC}"

# Step 4: Wait for services to be healthy
echo -e "${CYAN}⏳ Step 4: Waiting for services to be healthy...${NC}"

sleep 5

# Check PostgreSQL
echo -n "  Checking PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U nexus &>/dev/null; then
        echo -e " ${GREEN}✅${NC}"
        break
    fi
    sleep 1
    echo -n "."
done

# Check Redis
echo -n "  Checking Redis..."
for i in {1..30}; do
    if docker-compose exec -T redis redis-cli ping &>/dev/null; then
        echo -e " ${GREEN}✅${NC}"
        break
    fi
    sleep 1
    echo -n "."
done

# Check Backend
echo -n "  Checking Backend..."
for i in {1..60}; do
    if curl -s http://localhost:8000/health &>/dev/null; then
        echo -e " ${GREEN}✅${NC}"
        break
    fi
    sleep 1
    echo -n "."
done

# Step 5: Display access information
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 🎉 DEPLOYMENT COMPLETE!                       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get RunPod URLs
if [ -n "$RUNPOD_POD_ID" ] || [ -n "$HOSTNAME" ]; then
    POD_ID=${RUNPOD_POD_ID:-$HOSTNAME}
    echo -e "${CYAN}🌐 Access Your Services:${NC}"
    echo ""
    echo -e "  Backend API:     ${GREEN}https://$POD_ID-8000.proxy.runpod.net${NC}"
    echo -e "  API Docs:        ${GREEN}https://$POD_ID-8000.proxy.runpod.net/docs${NC}"
    echo -e "  Frontend:        ${GREEN}https://$POD_ID-3000.proxy.runpod.net${NC}"
    echo -e "  Grafana:         ${GREEN}https://$POD_ID-3001.proxy.runpod.net${NC}"
    echo ""
    echo -e "${CYAN}📝 RunPod Port Configuration:${NC}"
    echo "  In RunPod Dashboard, expose these ports:"
    echo "    • 8000 (Backend API)"
    echo "    • 3000 (Frontend)"
    echo "    • 3001 (Grafana - optional)"
else
    echo -e "${CYAN}🌐 Access Your Services (Local):${NC}"
    echo ""
    echo -e "  Backend API:     ${GREEN}http://localhost:8000${NC}"
    echo -e "  API Docs:        ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "  Frontend:        ${GREEN}http://localhost:3000${NC}"
    echo -e "  Grafana:         ${GREEN}http://localhost:3001${NC}"
fi

echo ""
echo -e "${CYAN}🔑 Credentials:${NC}"
echo ""

# Read Grafana password from .env
GRAFANA_PWD=$(grep GRAFANA_PASSWORD .env | cut -d '=' -f2)
echo -e "  Grafana:"
echo -e "    Username: ${GREEN}admin${NC}"
echo -e "    Password: ${GREEN}$GRAFANA_PWD${NC}"

echo ""
echo -e "${YELLOW}⚠️  IMPORTANT - Configure AI:${NC}"
echo ""
echo "  1. Edit your .env file:"
echo -e "     ${GREEN}nano .env${NC}"
echo ""
echo "  2. Add your OpenRouter API key:"
echo -e "     ${GREEN}OPENROUTER_API_KEY=sk-or-your-key-here${NC}"
echo ""
echo "  3. Get your key from:"
echo -e "     ${CYAN}https://openrouter.ai/keys${NC}"
echo ""
echo "  4. Restart services:"
echo -e "     ${GREEN}docker-compose restart backend${NC}"
echo ""

echo -e "${CYAN}📚 Next Steps:${NC}"
echo ""
echo "  1. Configure your OpenRouter API key (see above)"
echo "  2. Test the API at /docs endpoint"
echo "  3. Try AI endpoints:"
echo "     • POST /api/v2/ai/quick - Quick queries"
echo "     • GET /api/v2/ai/models - See all 30+ models"
echo "     • POST /api/v2/ide/ai/generate - Generate code"
echo ""
echo "  4. View logs:"
echo -e "     ${GREEN}docker-compose logs -f backend${NC}"
echo ""

echo -e "${CYAN}📖 Documentation:${NC}"
echo ""
echo "  • AI Router Guide:        AI_ROUTER_GUIDE.md"
echo "  • Quick Start:            START_HERE_AI_SETUP.md"
echo "  • Implementation Summary: 🎉_AI_IMPLEMENTATION_COMPLETE.md"
echo ""

echo -e "${GREEN}✨ Your NexusLang v2 platform is now running with AI! ✨${NC}"
echo ""

