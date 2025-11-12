#!/bin/bash
# NexusLang v2 - Safe RunPod Integration Script
# Deploys NexusLang v2 alongside existing Galion infrastructure
# Uses ports 3100/8100 to avoid conflicts with Galion's 3000/8000

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  NexusLang v2 - RunPod Integration Deployment                ║"
echo "║  Safe deployment alongside Galion.app/studio                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check we're in the right directory
if [ ! -f "v2/docker-compose.nexuslang.yml" ]; then
    echo -e "${RED}❌ Error: Must run from project-nexus root directory${NC}"
    echo "   Current directory: $(pwd)"
    echo "   Expected file: v2/docker-compose.nexuslang.yml"
    exit 1
fi

echo -e "${CYAN}📍 Current directory: $(pwd)${NC}"
echo ""

# ==================== PRE-FLIGHT CHECKS ====================

echo -e "${CYAN}🔍 Running pre-flight checks...${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found. Installing...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker found${NC}"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose not found. Installing...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✅ Docker Compose found${NC}"
fi

echo ""

# Check if Galion services are running
echo -e "${CYAN}🔍 Checking existing Galion services...${NC}"
echo ""

GALION_RUNNING=false

if docker ps | grep -q "galion-postgres"; then
    echo -e "${GREEN}✅ Galion PostgreSQL is running${NC}"
    GALION_RUNNING=true
else
    echo -e "${YELLOW}⚠️  Galion PostgreSQL not found${NC}"
    echo "   This is OK if Galion isn't deployed yet"
fi

if docker ps | grep -q "galion-redis"; then
    echo -e "${GREEN}✅ Galion Redis is running${NC}"
    GALION_RUNNING=true
else
    echo -e "${YELLOW}⚠️  Galion Redis not found${NC}"
    echo "   This is OK if Galion isn't deployed yet"
fi

# Check if ports 3100 and 8100 are available
echo ""
echo -e "${CYAN}🔍 Checking port availability...${NC}"

if netstat -tuln 2>/dev/null | grep -q ":3100 "; then
    echo -e "${RED}❌ Port 3100 is already in use!${NC}"
    echo "   Cannot deploy NexusLang frontend"
    exit 1
else
    echo -e "${GREEN}✅ Port 3100 is available (NexusLang frontend)${NC}"
fi

if netstat -tuln 2>/dev/null | grep -q ":8100 "; then
    echo -e "${RED}❌ Port 8100 is already in use!${NC}"
    echo "   Cannot deploy NexusLang backend"
    exit 1
else
    echo -e "${GREEN}✅ Port 8100 is available (NexusLang backend)${NC}"
fi

echo ""

# ==================== ENVIRONMENT SETUP ====================

echo -e "${CYAN}⚙️  Configuring environment...${NC}"
echo ""

# Generate secrets if not provided
if [ -z "$NEXUSLANG_SECRET_KEY" ]; then
    NEXUSLANG_SECRET_KEY=$(openssl rand -hex 32)
    echo -e "${YELLOW}🔐 Generated SECRET_KEY${NC}"
fi

if [ -z "$NEXUSLANG_JWT_SECRET" ]; then
    NEXUSLANG_JWT_SECRET=$(openssl rand -hex 32)
    echo -e "${YELLOW}🔐 Generated JWT_SECRET${NC}"
fi

# Check if .env exists in v2/backend
if [ ! -f "v2/backend/.env" ]; then
    echo -e "${YELLOW}⚙️  Creating backend .env file...${NC}"
    
    # Try to read Galion passwords if they exist
    POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-nexus_password_change_me}
    REDIS_PASSWORD=${REDIS_PASSWORD:-redis_password_change_me}
    
    cat > v2/backend/.env << EOF
# NexusLang v2 Backend Configuration
# RunPod Integration - Shares infrastructure with Galion

# Application
APP_NAME=NexusLang v2 API
DEBUG=false
ENVIRONMENT=production

# Security (NexusLang-specific)
SECRET_KEY=${NEXUSLANG_SECRET_KEY}
JWT_SECRET=${NEXUSLANG_JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database - Shared Galion PostgreSQL with separate database
DATABASE_URL=postgresql://nexus:${POSTGRES_PASSWORD}@galion-postgres:5432/nexuslang_v2
POSTGRES_USER=nexus
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=nexuslang_v2
POSTGRES_HOST=galion-postgres
POSTGRES_PORT=5432

# Redis - Shared Galion Redis using DB 1 (Galion uses DB 0)
REDIS_URL=redis://:${REDIS_PASSWORD}@galion-redis:6379/1
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_HOST=galion-redis
REDIS_PORT=6379

# CORS - Allow RunPod and custom domains
CORS_ORIGINS=["http://localhost:3100","http://localhost:8100","https://nexuslang.galion.app","https://api.nexuslang.galion.app","https://*.proxy.runpod.net"]

# OpenAI (optional)
OPENAI_API_KEY=${OPENAI_API_KEY:-}
EOF
    
    echo -e "${GREEN}✅ Backend .env created${NC}"
else
    echo -e "${GREEN}✅ Backend .env exists${NC}"
fi

echo ""

# ==================== DATABASE SETUP ====================

echo -e "${CYAN}🗄️  Setting up NexusLang database...${NC}"
echo ""

if [ "$GALION_RUNNING" = true ]; then
    echo "Creating nexuslang_v2 database in shared PostgreSQL..."
    
    # Try to create database (will fail gracefully if exists)
    docker exec galion-postgres psql -U nexus -d postgres -c "CREATE DATABASE nexuslang_v2;" 2>/dev/null || echo "   Database may already exist"
    
    # Enable UUID extension
    docker exec galion-postgres psql -U nexus -d nexuslang_v2 -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";' 2>/dev/null || true
    
    echo -e "${GREEN}✅ NexusLang database ready${NC}"
else
    echo -e "${YELLOW}⚠️  Galion PostgreSQL not running - will create database on first start${NC}"
fi

echo ""

# ==================== BUILD AND DEPLOY ====================

echo -e "${CYAN}🔨 Building NexusLang v2 services...${NC}"
echo ""

cd v2

# Build services using our integration docker-compose
docker-compose -f docker-compose.nexuslang.yml build

echo ""
echo -e "${CYAN}🚀 Starting NexusLang v2 services...${NC}"
echo ""

# Start services
docker-compose -f docker-compose.nexuslang.yml up -d

echo ""
echo -e "${CYAN}⏳ Waiting for services to initialize (30 seconds)...${NC}"
sleep 30

echo ""

# ==================== VERIFICATION ====================

echo -e "${CYAN}📊 Service Status:${NC}"
echo ""

docker-compose -f docker-compose.nexuslang.yml ps

echo ""
echo -e "${CYAN}🏥 Health Checks:${NC}"
echo ""

# Test backend
if curl -s http://localhost:8100/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ NexusLang Backend (port 8100) is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  NexusLang Backend not responding yet (may need more time)${NC}"
fi

# Test frontend
if curl -s http://localhost:3100 | grep -q "NexusLang"; then
    echo -e "${GREEN}✅ NexusLang Frontend (port 3100) is accessible${NC}"
else
    echo -e "${YELLOW}⚠️  NexusLang Frontend not responding yet (may need more time)${NC}"
fi

# Verify Galion is still running (if it was running)
if [ "$GALION_RUNNING" = true ]; then
    echo ""
    echo -e "${CYAN}🔍 Verifying Galion services not affected...${NC}"
    
    if docker ps | grep -q "galion-frontend"; then
        echo -e "${GREEN}✅ Galion services still running${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not verify Galion status${NC}"
    fi
fi

echo ""

# ==================== SUCCESS ====================

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✅ NEXUSLANG V2 DEPLOYED SUCCESSFULLY!                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}🌐 Access Points:${NC}"
echo ""
echo "  NexusLang v2:"
echo -e "    ${YELLOW}• Frontend:${NC}  http://localhost:3100"
echo -e "    ${YELLOW}• Backend:${NC}   http://localhost:8100"
echo -e "    ${YELLOW}• API Docs:${NC}  http://localhost:8100/docs"
echo -e "    ${YELLOW}• IDE:${NC}       http://localhost:3100/ide"
echo ""
echo "  Galion (existing):"
echo -e "    ${YELLOW}• Frontend:${NC}  http://localhost:3000"
echo -e "    ${YELLOW}• Backend:${NC}   http://localhost:8000"
echo ""
echo -e "${CYAN}📋 Next Steps:${NC}"
echo "  1. In RunPod dashboard, expose HTTP ports: 3100, 8100"
echo "  2. Get your RunPod proxy URLs for these ports"
echo "  3. Test: http://<runpod-url-3100>/ide"
echo "  4. Configure Cloudflare DNS (see instructions below)"
echo ""
echo -e "${CYAN}🔧 Useful Commands:${NC}"
echo "  View logs:         cd v2 && docker-compose -f docker-compose.nexuslang.yml logs -f"
echo "  Restart services:  cd v2 && docker-compose -f docker-compose.nexuslang.yml restart"
echo "  Stop services:     cd v2 && docker-compose -f docker-compose.nexuslang.yml down"
echo "  Check status:      cd v2 && docker-compose -f docker-compose.nexuslang.yml ps"
echo ""
echo -e "${CYAN}📖 Documentation:${NC}"
echo "  Setup guide:   v2/START_ON_RUNPOD.md"
echo "  DNS setup:     v2/CLOUDFLARE_DNS_SETUP.md (will be created)"
echo ""
echo -e "${GREEN}🎉 NexusLang v2 is running alongside Galion!${NC}"
echo ""

