#!/bin/bash
# Test all deployed apps

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "=========================================="
echo "   Testing All Deployments"
echo "=========================================="
echo ""

POD_ID=$(hostname)

# Test local endpoints
echo -e "${BLUE}[1/6] Testing local endpoints...${NC}"
echo ""

# developer.galion.app
echo -n "  developer.galion.app backend (8000): "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

echo -n "  developer.galion.app frontend (3000): "
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ RESPONDING${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# galion.app
echo -n "  galion.app backend (8100): "
if curl -s http://localhost:8100/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${YELLOW}⚠ NOT RUNNING${NC}"
fi

echo -n "  galion.app frontend (3100): "
if curl -s http://localhost:3100 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ RESPONDING${NC}"
else
    echo -e "${YELLOW}⚠ NOT RUNNING${NC}"
fi

# galion.studio
echo -n "  galion.studio backend (8200): "
if curl -s http://localhost:8200/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${YELLOW}⚠ NOT RUNNING${NC}"
fi

echo -n "  galion.studio frontend (3200): "
if curl -s http://localhost:3200 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ RESPONDING${NC}"
else
    echo -e "${YELLOW}⚠ NOT RUNNING${NC}"
fi

# Test RunPod proxy URLs
echo ""
echo -e "${BLUE}[2/6] Testing RunPod proxy URLs...${NC}"
echo ""

echo -n "  https://${POD_ID}-8000.proxy.runpod.net/health: "
if curl -s -k "https://${POD_ID}-8000.proxy.runpod.net/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ ACCESSIBLE${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

echo -n "  https://${POD_ID}-3000.proxy.runpod.net: "
if curl -s -k "https://${POD_ID}-3000.proxy.runpod.net" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ ACCESSIBLE${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Test database
echo ""
echo -e "${BLUE}[3/6] Testing database connection...${NC}"
echo ""

if psql -h localhost -U nexus -d galion_platform -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL: Connected${NC}"
else
    echo -e "${RED}✗ PostgreSQL: Connection failed${NC}"
fi

# Test Redis
echo ""
echo -e "${BLUE}[4/6] Testing Redis connection...${NC}"
echo ""

if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis: Connected${NC}"
else
    echo -e "${RED}✗ Redis: Connection failed${NC}"
fi

# Test Cloudflare tunnels
echo ""
echo -e "${BLUE}[5/6] Testing Cloudflare tunnels...${NC}"
echo ""

if ps aux | grep cloudflared | grep -v grep > /dev/null 2>&1; then
    TUNNEL_COUNT=$(ps aux | grep cloudflared | grep -v grep | wc -l)
    echo -e "${GREEN}✓ Cloudflare tunnels running: ${TUNNEL_COUNT}${NC}"
    
    echo ""
    echo "Tunnel processes:"
    ps aux | grep cloudflared | grep -v grep | awk '{print "  PID "$2": "$11" "$12" "$13}'
else
    echo -e "${YELLOW}⚠ No Cloudflare tunnels running${NC}"
    echo "Run: ./setup-cloudflare-tunnels.sh"
fi

# Process summary
echo ""
echo -e "${BLUE}[6/6] Process summary...${NC}"
echo ""

echo "Python backends:"
ps aux | grep uvicorn | grep -v grep | wc -l | xargs echo -n "  "
echo " process(es)"

echo "Node.js frontends:"
ps aux | grep "next" | grep -v grep | wc -l | xargs echo -n "  "
echo " process(es)"

# URLs summary
echo ""
echo "=========================================="
echo "   Access URLs"
echo "=========================================="
echo ""
echo -e "${GREEN}Local URLs (for testing):${NC}"
echo "  developer.galion.app: http://localhost:3000"
echo "  galion.app:           http://localhost:3100"
echo "  galion.studio:        http://localhost:3200"
echo ""
echo -e "${GREEN}RunPod Proxy URLs:${NC}"
echo "  developer.galion.app: https://${POD_ID}-3000.proxy.runpod.net"
echo "  galion.app:           https://${POD_ID}-3100.proxy.runpod.net"
echo "  galion.studio:        https://${POD_ID}-3200.proxy.runpod.net"
echo ""
echo -e "${GREEN}Public URLs (via Cloudflare):${NC}"
echo "  developer.galion.app: https://developer.galion.app"
echo "  galion.app:           https://galion.app"
echo "  galion.studio:        https://galion.studio"
echo ""
echo "=========================================="
echo ""

