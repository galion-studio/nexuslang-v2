#!/bin/bash

# ============================================
# Galion Ecosystem - Simple RunPod Deployment
# Fixes Cloudflare Error 521
# ============================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "============================================"
echo "  GALION ECOSYSTEM - RUNPOD DEPLOYMENT"
echo "  Fixes Cloudflare Error 521"
echo "============================================"
echo ""

# Check if we're on RunPod
if [ -z "$RUNPOD_POD_ID" ]; then
    echo -e "${YELLOW}⚠ WARNING: Not running on RunPod${NC}"
    echo -e "${YELLOW}This script is designed for RunPod environment${NC}"
    echo ""
fi

# Step 1: Copy environment file
echo -e "${BLUE}Step 1: Setting up environment...${NC}"
if [ ! -f ".env" ] && [ -f "production.env" ]; then
    cp production.env .env
    echo -e "${GREEN}✓ Copied production.env to .env${NC}"
fi

# Step 2: Create necessary directories
echo -e "${BLUE}Step 2: Creating directories...${NC}"
mkdir -p logs shared monitoring/prometheus monitoring/grafana/provisioning
echo -e "${GREEN}✓ Directories created${NC}"

# Step 3: Stop any existing containers
echo -e "${BLUE}Step 3: Stopping existing services...${NC}"
docker-compose down 2>/dev/null || true
docker system prune -f 2>/dev/null || true
echo -e "${GREEN}✓ Cleaned up${NC}"

# Step 4: Build and start services
echo -e "${BLUE}Step 4: Building and starting services...${NC}"

# Build backend first
echo "Building backend..."
docker-compose build backend
echo -e "${GREEN}✓ Backend built${NC}"

# Build frontend services
echo "Building frontend services..."
docker-compose build galion-app developer-platform galion-studio
echo -e "${GREEN}✓ Frontend services built${NC}"

# Start infrastructure first
echo "Starting infrastructure..."
docker-compose up -d postgres redis
sleep 10

# Check if postgres is ready
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U galion -d galion_db >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL ready${NC}"
        break
    fi
    echo -e "${YELLOW}Waiting for PostgreSQL... ($i/30)${NC}"
    sleep 2
done

# Start backend
echo "Starting backend..."
docker-compose up -d backend
sleep 5

# Check backend health
echo "Waiting for backend..."
for i in {1..30}; do
    if curl -s http://localhost:8010/health/fast >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend healthy${NC}"
        break
    fi
    echo -e "${YELLOW}Waiting for backend... ($i/30)${NC}"
    sleep 2
done

# Start frontend services
echo "Starting frontend services..."
docker-compose up -d galion-app developer-platform galion-studio
sleep 5

# Start monitoring (optional)
echo "Starting monitoring services..."
docker-compose up -d prometheus grafana nginx 2>/dev/null || true

# Step 5: Final verification
echo -e "${BLUE}Step 5: Final verification...${NC}"
echo ""

# Get the RunPod pod URL if available
if [ -n "$RUNPOD_PUBLIC_IP" ]; then
    POD_URL="http://$RUNPOD_PUBLIC_IP"
    echo -e "${GREEN}🌐 RUNPOD POD URL: $POD_URL${NC}"
    echo ""
fi

# Display service status
echo "Service Status:"
docker-compose ps

echo ""
echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}  GALION ECOSYSTEM DEPLOYED! 🚀${NC}"
echo -e "${GREEN}===========================================${NC}"
echo ""

if [ -n "$POD_URL" ]; then
    echo "🌐 ACCESS YOUR GALION ECOSYSTEM:"
    echo ""
    echo -e "${BLUE}🎤 Galion.app (Voice AI):${NC}"
    echo "  $POD_URL:3010/voice"
    echo "  $POD_URL:3010/onboarding"
    echo ""
    echo -e "${BLUE}💻 developer.Galion.app (IDE):${NC}"
    echo "  $POD_URL:3020/ide"
    echo ""
    echo -e "${BLUE}🏢 Galion.studio (Corporate):${NC}"
    echo "  $POD_URL:3030"
    echo ""
    echo -e "${BLUE}🔗 Backend API:${NC}"
    echo "  $POD_URL:8010/docs"
    echo ""
else
    echo "🌐 LOCAL ACCESS:"
    echo ""
    echo -e "${BLUE}🎤 Galion.app (Voice AI):${NC}"
    echo "  http://localhost:3010/voice"
    echo ""
    echo -e "${BLUE}💻 developer.Galion.app (IDE):${NC}"
    echo "  http://localhost:3020/ide"
    echo ""
    echo -e "${BLUE}🏢 Galion.studio (Corporate):${NC}"
    echo "  http://localhost:3030"
    echo ""
    echo -e "${BLUE}🔗 Backend API:${NC}"
    echo "  http://localhost:8010/docs"
fi

echo ""
echo -e "${YELLOW}🔧 CLOUDFLARE SETUP (Fix Error 521):${NC}"
echo "1. Go to Cloudflare Dashboard"
echo "2. Update DNS records:"
if [ -n "$POD_URL" ]; then
    echo "   CNAME galion.app → $RUNPOD_PUBLIC_IP"
    echo "   CNAME developer.galion.app → $RUNPOD_PUBLIC_IP"
    echo "   CNAME galion.studio → $RUNPOD_PUBLIC_IP"
else
    echo "   CNAME galion.app → [your-runpod-ip]"
    echo "   CNAME developer.galion.app → [your-runpod-ip]"
    echo "   CNAME galion.studio → [your-runpod-ip]"
fi
echo "3. Enable 'Always Use HTTPS'"
echo "4. Set SSL to 'Full (strict)'"
echo ""

echo -e "${GREEN}\"Your imagination is the end.\"${NC}"
echo ""
echo "Deployment completed! 🎉"
