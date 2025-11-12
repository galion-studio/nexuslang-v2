#!/bin/bash
# Deploy all three apps on RunPod

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "=========================================="
echo "   Deploying All Galion Apps on RunPod"
echo "=========================================="
echo ""

# Load environment
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ Loading environment from .env${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Run: cp env.runpod.multi-apps .env"
    echo "Then edit .env with your secrets"
    exit 1
fi

# Check if PostgreSQL is running
echo -e "${BLUE}[1/8] Checking PostgreSQL...${NC}"
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}⚠ Starting PostgreSQL...${NC}"
    service postgresql start || echo -e "${RED}Failed to start PostgreSQL${NC}"
fi

# Check if Redis is running
echo -e "${BLUE}[2/8] Checking Redis...${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠ Starting Redis...${NC}"
    redis-server --daemonize yes --requirepass "${REDIS_PASSWORD}" || echo -e "${RED}Failed to start Redis${NC}"
fi

# Stop any existing services
echo -e "${BLUE}[3/8] Stopping existing services...${NC}"
pkill -f "uvicorn" || true
pkill -f "next" || true
sleep 2

# Create database if not exists
echo -e "${BLUE}[4/8] Setting up database...${NC}"
cd /workspace/nexuslang-v2
psql -h localhost -U ${POSTGRES_USER} -c "CREATE DATABASE galion_platform;" 2>/dev/null || echo "Database already exists"

# Start developer.galion.app (NexusLang v2)
echo -e "${BLUE}[5/8] Starting developer.galion.app...${NC}"
cd /workspace/nexuslang-v2/v2/backend
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/developer-backend.log 2>&1 &
echo -e "${GREEN}✓ Backend started on port 8000${NC}"

cd /workspace/nexuslang-v2/v2/frontend
nohup npm run dev -- -p 3000 > /tmp/developer-frontend.log 2>&1 &
echo -e "${GREEN}✓ Frontend started on port 3000${NC}"

# Start galion.app (Voice AI) - if exists
echo -e "${BLUE}[6/8] Starting galion.app...${NC}"
if [ -d "/workspace/nexuslang-v2/v1/galion/backend" ]; then
    cd /workspace/nexuslang-v2/v1/galion/backend
    nohup python -m uvicorn main:app --host 0.0.0.0 --port 8100 > /tmp/galion-app-backend.log 2>&1 &
    echo -e "${GREEN}✓ Backend started on port 8100${NC}"
    
    if [ -d "/workspace/nexuslang-v2/v1/galion/frontend" ]; then
        cd /workspace/nexuslang-v2/v1/galion/frontend
        nohup npm run dev -- -p 3100 > /tmp/galion-app-frontend.log 2>&1 &
        echo -e "${GREEN}✓ Frontend started on port 3100${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Galion.app code not found, skipping...${NC}"
fi

# Start galion.studio (Collaborative) - if exists
echo -e "${BLUE}[7/8] Starting galion.studio...${NC}"
if [ -d "/workspace/nexuslang-v2/v1/galion/studio" ]; then
    cd /workspace/nexuslang-v2/v1/galion/studio
    nohup python -m uvicorn main:app --host 0.0.0.0 --port 8200 > /tmp/galion-studio-backend.log 2>&1 &
    echo -e "${GREEN}✓ Backend started on port 8200${NC}"
    
    if [ -d "/workspace/nexuslang-v2/v1/galion/studio-frontend" ]; then
        cd /workspace/nexuslang-v2/v1/galion/studio-frontend
        nohup npm run dev -- -p 3200 > /tmp/galion-studio-frontend.log 2>&1 &
        echo -e "${GREEN}✓ Frontend started on port 3200${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Galion.studio code not found, skipping...${NC}"
fi

# Wait for services to start
echo -e "${BLUE}[8/8] Waiting for services to initialize...${NC}"
sleep 10

# Check service status
echo ""
echo "=========================================="
echo "   Service Status"
echo "=========================================="
echo ""

# Check developer.galion.app
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ developer.galion.app backend: http://localhost:8000${NC}"
else
    echo -e "${RED}✗ developer.galion.app backend: FAILED${NC}"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ developer.galion.app frontend: http://localhost:3000${NC}"
else
    echo -e "${YELLOW}⚠ developer.galion.app frontend: Starting (may take 30s)${NC}"
fi

# Check galion.app
if curl -s http://localhost:8100/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ galion.app backend: http://localhost:8100${NC}"
else
    echo -e "${YELLOW}⚠ galion.app backend: Not running${NC}"
fi

if curl -s http://localhost:3100 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ galion.app frontend: http://localhost:3100${NC}"
else
    echo -e "${YELLOW}⚠ galion.app frontend: Not running${NC}"
fi

# Check galion.studio
if curl -s http://localhost:8200/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ galion.studio backend: http://localhost:8200${NC}"
else
    echo -e "${YELLOW}⚠ galion.studio backend: Not running${NC}"
fi

if curl -s http://localhost:3200 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ galion.studio frontend: http://localhost:3200${NC}"
else
    echo -e "${YELLOW}⚠ galion.studio frontend: Not running${NC}"
fi

echo ""
echo "=========================================="
echo "   RunPod URLs"
echo "=========================================="
echo ""
POD_ID=$(hostname)
echo -e "${BLUE}Pod ID: ${POD_ID}${NC}"
echo ""
echo -e "${GREEN}developer.galion.app:${NC}"
echo "  Frontend: https://${POD_ID}-3000.proxy.runpod.net"
echo "  Backend:  https://${POD_ID}-8000.proxy.runpod.net"
echo ""
echo -e "${GREEN}galion.app:${NC}"
echo "  Frontend: https://${POD_ID}-3100.proxy.runpod.net"
echo "  Backend:  https://${POD_ID}-8100.proxy.runpod.net"
echo ""
echo -e "${GREEN}galion.studio:${NC}"
echo "  Frontend: https://${POD_ID}-3200.proxy.runpod.net"
echo "  Backend:  https://${POD_ID}-8200.proxy.runpod.net"
echo ""
echo "=========================================="
echo ""
echo "View logs:"
echo "  tail -f /tmp/developer-backend.log"
echo "  tail -f /tmp/galion-app-backend.log"
echo "  tail -f /tmp/galion-studio-backend.log"
echo ""
echo "Stop all services:"
echo "  pkill -f uvicorn && pkill -f next"
echo ""

