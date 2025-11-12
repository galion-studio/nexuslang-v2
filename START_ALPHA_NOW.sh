#!/bin/bash
# Start NexusLang v2 Alpha - Working Version
# Simple script to get everything running quickly

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting NexusLang v2 Alpha...${NC}"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker found${NC}"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚙️ Creating default environment file...${NC}"
    cat > .env << 'EOF'
# NexusLang v2 Alpha - Development Configuration

# Database
POSTGRES_USER=nexus
POSTGRES_PASSWORD=nexus_dev_pass_123
POSTGRES_DB=nexus_v2

# Redis
REDIS_PASSWORD=redis_dev_pass_123

# Security (development only - change for production!)
SECRET_KEY=dev_secret_key_for_alpha_testing_only_32chars
JWT_SECRET=dev_jwt_secret_for_alpha_testing_only_needs_64_characters_minimum

# AI Services (optional for alpha)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Whisper/TTS (CPU for alpha - fast enough for testing)
WHISPER_MODEL=tiny
WHISPER_DEVICE=cpu
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC
TTS_DEVICE=cpu

# Application
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development
EOF
    echo -e "${GREEN}✓ Environment file created${NC}"
    echo -e "${YELLOW}   For AI features, add your OPENAI_API_KEY to .env${NC}"
    echo ""
fi

# Stop any existing containers
echo -e "${BLUE}🛑 Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true
echo ""

# Start services
echo -e "${BLUE}🚀 Starting services...${NC}"
echo ""

# Start database and cache first
echo "Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis

# Wait for database
echo -n "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U nexus > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

# Start Elasticsearch
echo "Starting Elasticsearch..."
docker-compose up -d elasticsearch
sleep 5
echo ""

# Start backend
echo "Starting Backend API..."
docker-compose up -d backend

# Wait for backend
echo -n "Waiting for Backend..."
for i in {1..60}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 2
    echo -n "."
done
echo ""

# Start frontend
echo "Starting Frontend..."
docker-compose up -d frontend

# Wait for frontend
echo -n "Waiting for Frontend..."
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 2
    echo -n "."
done
echo ""

# Check health
echo -e "${BLUE}🏥 Checking service health...${NC}"
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)

if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend is healthy!${NC}"
else
    echo -e "${YELLOW}⚠️ Backend may still be starting...${NC}"
fi
echo ""

# Show status
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose ps
echo ""

# Success message
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✅ NEXUSLANG V2 ALPHA IS RUNNING!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}🌐 Access URLs:${NC}"
echo ""
echo -e "  Frontend:   ${GREEN}http://localhost:3000${NC}"
echo -e "  IDE:        ${GREEN}http://localhost:3000/ide${NC}"
echo -e "  Grokopedia: ${GREEN}http://localhost:3000/grokopedia${NC}"
echo -e "  Community:  ${GREEN}http://localhost:3000/community${NC}"
echo -e "  Billing:    ${GREEN}http://localhost:3000/billing${NC}"
echo ""
echo -e "  Backend:    ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs:   ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  Health:     ${GREEN}http://localhost:8000/health${NC}"
echo ""
echo -e "${BLUE}📝 Quick Test:${NC}"
echo ""
echo "1. Open http://localhost:3000"
echo "2. Click 'Sign Up Free'"
echo "3. Create an account"
echo "4. Go to IDE and write code"
echo "5. Click 'Run' to execute!"
echo ""
echo -e "${BLUE}📚 Helpful Commands:${NC}"
echo ""
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose stop"
echo "  Restart:      docker-compose restart"
echo "  Clean start:  docker-compose down && ./START_ALPHA_NOW.sh"
echo ""
echo -e "${GREEN}🎉 Enjoy your NexusLang v2 Alpha!${NC}"
echo ""

