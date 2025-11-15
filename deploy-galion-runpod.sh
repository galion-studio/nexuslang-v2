#!/bin/bash

# ============================================
# Galion Platform - RunPod Deployment Script
# ============================================
# "Your imagination is the end."
# ============================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================"
echo "  GALION PLATFORM DEPLOYMENT"
echo "  RunPod CPU Instance"
echo "  Version: v2.2-production"
echo "============================================"
echo ""

# Step 1: Environment Check
echo -e "${BLUE}Step 1: Checking environment...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose installed${NC}"

echo ""

# Step 2: Create directories
echo -e "${BLUE}Step 2: Creating directories...${NC}"
mkdir -p logs
mkdir -p shared
mkdir -p .agent-flags
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Step 3: Check environment file
echo -e "${BLUE}Step 3: Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found, creating from template...${NC}"
    if [ -f "production.env" ]; then
        cp production.env .env
        echo -e "${GREEN}✓ Created .env from production.env${NC}"
    else
        echo -e "${RED}✗ No environment template found${NC}"
        echo -e "${YELLOW}Please create .env file manually${NC}"
    fi
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi
echo ""

# Step 4: Stop existing services
echo -e "${BLUE}Step 4: Stopping existing services...${NC}"
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✓ Existing services stopped${NC}"
echo ""

# Step 5: Build services
echo -e "${BLUE}Step 5: Building Docker images...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✓ Images built successfully${NC}"
echo ""

# Step 6: Start services
echo -e "${BLUE}Step 6: Starting all services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Step 7: Wait for services to be ready
echo -e "${BLUE}Step 7: Waiting for services to be ready...${NC}"
sleep 10

# Check health
echo "Checking service health..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8010/health/fast > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is healthy${NC}"
        break
    fi
    echo -e "${YELLOW}Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ Backend failed to start${NC}"
    echo "Check logs: docker-compose logs backend"
    exit 1
fi

echo ""

# Step 8: Verify all services
echo -e "${BLUE}Step 8: Verifying services...${NC}"
docker-compose ps
echo ""

# Step 9: Display access information
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  DEPLOYMENT SUCCESSFUL! 🚀${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Access your Galion Platform:"
echo ""
echo -e "${BLUE}Galion.app (Voice-First):${NC}"
echo "  http://localhost:3010/voice"
echo "  http://localhost:3010/onboarding"
echo "  http://localhost:3010/beta-signup"
echo ""
echo -e "${BLUE}Developer Platform (IDE):${NC}"
echo "  http://localhost:3020/ide"
echo ""
echo -e "${BLUE}Galion Studio (Corporate):${NC}"
echo "  http://localhost:3030"
echo ""
echo -e "${BLUE}Backend API:${NC}"
echo "  http://localhost:8010/docs"
echo "  http://localhost:8010/health/fast"
echo ""
echo -e "${BLUE}Monitoring:${NC}"
echo "  http://localhost:9090 (Prometheus)"
echo "  http://localhost:3001 (Grafana)"
echo "  http://localhost:8080 (Dashboard)"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  docker-compose ps              # Check service status"
echo "  docker-compose logs -f         # View logs"
echo "  docker-compose restart         # Restart services"
echo "  docker-compose down            # Stop services"
echo ""
echo -e "${GREEN}\"Your imagination is the end.\"${NC}"
echo ""

