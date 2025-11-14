#!/bin/bash

# ============================================
# Galion Platform - RunPod Quick Start
# ============================================
# "Your imagination is the end."
# ============================================

set -e

echo "============================================"
echo "  🚀 GALION PLATFORM - RUNPOD"
echo "  Quick Start Script"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get RunPod IP
RUNPOD_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

echo -e "${BLUE}RunPod IP: ${RUNPOD_IP}${NC}"
echo ""

# Step 1: Check backend
echo -e "${BLUE}Step 1: Checking backend services...${NC}"
if curl -s http://localhost:8010/health/fast > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Backend not responding, starting services...${NC}"
    docker-compose up -d postgres redis backend
    sleep 10
fi
echo ""

# Step 2: Start Galion.app
echo -e "${BLUE}Step 2: Starting Galion.app...${NC}"
cd galion-app

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

# Kill existing process if running
pkill -f "next dev" 2>/dev/null || true

# Start in background
nohup npm run dev > ../logs/galion-app.log 2>&1 &
GALION_PID=$!
echo -e "${GREEN}✓ Galion.app started (PID: $GALION_PID)${NC}"
cd ..
echo ""

# Step 3: Start Developer Platform
echo -e "${BLUE}Step 3: Starting Developer Platform...${NC}"
cd developer-platform

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

nohup npm run dev -- -p 3020 > ../logs/developer-platform.log 2>&1 &
DEV_PID=$!
echo -e "${GREEN}✓ Developer Platform started (PID: $DEV_PID)${NC}"
cd ..
echo ""

# Step 4: Start Galion Studio
echo -e "${BLUE}Step 4: Starting Galion Studio...${NC}"
cd galion-studio

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

nohup npm run dev -- -p 3030 > ../logs/galion-studio.log 2>&1 &
STUDIO_PID=$!
echo -e "${GREEN}✓ Galion Studio started (PID: $STUDIO_PID)${NC}"
cd ..
echo ""

# Wait for services to initialize
echo -e "${BLUE}Waiting for services to initialize...${NC}"
sleep 15

# Step 5: Verify services
echo -e "${BLUE}Step 5: Verifying services...${NC}"

check_service() {
    if curl -s "$1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $2${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ $2 (may still be starting)${NC}"
        return 1
    fi
}

check_service "http://localhost:8010/health/fast" "Backend API"
check_service "http://localhost:3000" "Galion.app"
check_service "http://localhost:3020" "Developer Platform"
check_service "http://localhost:3030" "Galion Studio"

echo ""

# Display access information
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  ✅ GALION PLATFORM RUNNING!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${BLUE}Access your platforms:${NC}"
echo ""
echo "🎤 Galion.app (Voice-First):"
echo "   http://${RUNPOD_IP}:3000/voice"
echo "   http://${RUNPOD_IP}:3000/onboarding"
echo "   http://${RUNPOD_IP}:3000/beta-signup"
echo ""
echo "💻 Developer Platform (IDE):"
echo "   http://${RUNPOD_IP}:3020/ide"
echo ""
echo "🏢 Galion Studio (Corporate):"
echo "   http://${RUNPOD_IP}:3030"
echo ""
echo "🔧 Backend API:"
echo "   http://${RUNPOD_IP}:8010/docs"
echo "   http://${RUNPOD_IP}:8010/health/fast"
echo ""
echo "📊 Monitoring:"
echo "   http://${RUNPOD_IP}:9090 (Prometheus)"
echo "   http://${RUNPOD_IP}:3001 (Grafana)"
echo ""
echo -e "${YELLOW}Process IDs:${NC}"
echo "   Galion.app: $GALION_PID"
echo "   Developer: $DEV_PID"
echo "   Studio: $STUDIO_PID"
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo "   tail -f logs/galion-app.log"
echo "   tail -f logs/developer-platform.log"
echo "   tail -f logs/galion-studio.log"
echo ""
echo -e "${YELLOW}Stop services:${NC}"
echo "   kill $GALION_PID $DEV_PID $STUDIO_PID"
echo "   docker-compose down"
echo ""
echo -e "${GREEN}\"Your imagination is the end.\"${NC}"
echo ""

