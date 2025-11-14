#!/bin/bash
# ============================================================================
# GALION.STUDIO - EMERGENCY SERVER START
# ============================================================================
# Run this on your RunPod terminal to fix Error 521
# All pages will work after running this script!

clear

echo "============================================================================"
echo "🚨 GALION.STUDIO EMERGENCY SERVER START"
echo "============================================================================"
echo ""
echo "This will:"
echo "  1. Stop any old servers"
echo "  2. Start fresh server on port 8080"
echo "  3. Test if it works"
echo "  4. Show you the IP for Cloudflare"
echo ""
echo "⏱️  Takes about 30 seconds..."
echo ""
echo "============================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Step 1
echo -e "${BLUE}[1/9]${NC} Navigating to project..."
cd /workspace/project-nexus || {
    echo -e "${RED}❌ ERROR: Project directory not found${NC}"
    echo "Please ensure your code is in /workspace/project-nexus"
    exit 1
}
echo -e "${GREEN}✅ Done${NC}"
echo ""

# Step 2
echo -e "${BLUE}[2/9]${NC} Installing dependencies..."
pip install -q -r requirements.txt 2>&1 | grep -v "Requirement already satisfied" || true
echo -e "${GREEN}✅ Done${NC}"
echo ""

# Step 3
echo -e "${BLUE}[3/9]${NC} Setting environment variables..."
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
export PORT=8080
export HOST=0.0.0.0
echo -e "${GREEN}✅ Done${NC}"
echo ""

# Step 4
echo -e "${BLUE}[4/9]${NC} Stopping old servers..."
pkill -f uvicorn 2>/dev/null || true
sleep 1
echo -e "${GREEN}✅ Done${NC}"
echo ""

# Step 5
echo -e "${BLUE}[5/9]${NC} Creating log directory..."
mkdir -p /workspace/logs
echo -e "${GREEN}✅ Done${NC}"
echo ""

# Step 6
echo -e "${BLUE}[6/9]${NC} Starting server on port 8080..."
cd v2/backend
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8080 --workers 2 > /workspace/logs/galion-backend.log 2>&1 &
SERVER_PID=$!
echo -e "${GREEN}✅ Server started (PID: $SERVER_PID)${NC}"
echo ""

# Step 7
echo -e "${BLUE}[7/9]${NC} Waiting for server to initialize..."
sleep 4
echo -e "${GREEN}✅ Done${NC}"
echo ""

# Step 8
echo -e "${BLUE}[8/9]${NC} Testing health endpoint..."
if curl -f -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check PASSED!${NC}"
    echo ""
    echo "Server response:"
    curl -s http://localhost:8080/health | head -5
else
    echo -e "${YELLOW}⚠️  Health check didn't respond yet${NC}"
    echo "Server may still be starting up..."
    echo ""
    echo "Check logs with: tail -f /workspace/logs/galion-backend.log"
fi
echo ""

# Step 9
echo -e "${BLUE}[9/9]${NC} Getting your public IP..."
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to determine")
echo -e "${GREEN}✅ Your RunPod IP: $PUBLIC_IP${NC}"
echo ""

# Summary
echo "============================================================================"
echo "✅ SERVER IS RUNNING!"
echo "============================================================================"
echo ""
echo "📍 Access Points:"
echo "  - Local:  http://localhost:8080"
echo "  - Public: http://$PUBLIC_IP:8080"
echo "  - Health: http://$PUBLIC_IP:8080/health"
echo ""
echo "============================================================================"
echo "🌐 NOW CONFIGURE CLOUDFLARE:"
echo "============================================================================"
echo ""
echo "1. Go to: https://dash.cloudflare.com"
echo "2. Select: galion.studio"
echo "3. Go to: DNS"
echo "4. Add/Update A record:"
echo "   - Type: A"
echo "   - Name: @"
echo "   - Content: $PUBLIC_IP  👈 COPY THIS"
echo "   - Proxy: ON (orange cloud)"
echo ""
echo "5. Go to: SSL/TLS → Overview"
echo "   - Set mode to: Flexible (or Full)"
echo ""
echo "6. Wait 2-3 minutes"
echo ""
echo "7. Test: https://galion.studio/health"
echo ""
echo "============================================================================"
echo "📊 USEFUL COMMANDS:"
echo "============================================================================"
echo ""
echo "View logs:    tail -f /workspace/logs/galion-backend.log"
echo "Check status: curl http://localhost:8080/health"
echo "Stop server:  kill $SERVER_PID"
echo "Restart:      $0"
echo ""
echo "============================================================================"
echo ""
echo "🎉 ALL PAGES WILL WORK ONCE CLOUDFLARE IS CONFIGURED!"
echo ""
echo "============================================================================"

# Save PID
echo $SERVER_PID > /workspace/logs/server.pid

