#!/bin/bash
# Setup Cloudflare Tunnels for all three domains

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "=========================================="
echo "   Cloudflare Tunnels Setup"
echo "=========================================="
echo ""

# Check if cloudflared is installed
if command -v cloudflared &> /dev/null; then
    echo -e "${GREEN}✓ cloudflared already installed: $(cloudflared --version)${NC}"
else
    echo -e "${BLUE}[1/3] Installing cloudflared...${NC}"
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x cloudflared-linux-amd64
    mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
    echo -e "${GREEN}✓ cloudflared installed${NC}"
fi

# Load environment
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi

# Check for tunnel tokens
echo ""
echo -e "${BLUE}[2/3] Checking Cloudflare tunnel tokens...${NC}"
echo ""

if [ -z "$CF_TUNNEL_TOKEN_DEVELOPER" ] || [ "$CF_TUNNEL_TOKEN_DEVELOPER" = "GET_FROM_CLOUDFLARE_DASHBOARD" ]; then
    echo -e "${YELLOW}⚠ CF_TUNNEL_TOKEN_DEVELOPER not set${NC}"
    echo "Get it from: https://dash.cloudflare.com → Zero Trust → Access → Tunnels"
    echo "Create tunnel for: developer.galion.app"
    MISSING_TOKEN=1
fi

if [ -z "$CF_TUNNEL_TOKEN_APP" ] || [ "$CF_TUNNEL_TOKEN_APP" = "GET_FROM_CLOUDFLARE_DASHBOARD" ]; then
    echo -e "${YELLOW}⚠ CF_TUNNEL_TOKEN_APP not set${NC}"
    echo "Get it from: https://dash.cloudflare.com → Zero Trust → Access → Tunnels"
    echo "Create tunnel for: galion.app"
    MISSING_TOKEN=1
fi

if [ -z "$CF_TUNNEL_TOKEN_STUDIO" ] || [ "$CF_TUNNEL_TOKEN_STUDIO" = "GET_FROM_CLOUDFLARE_DASHBOARD" ]; then
    echo -e "${YELLOW}⚠ CF_TUNNEL_TOKEN_STUDIO not set${NC}"
    echo "Get it from: https://dash.cloudflare.com → Zero Trust → Access → Tunnels"
    echo "Create tunnel for: galion.studio"
    MISSING_TOKEN=1
fi

if [ "$MISSING_TOKEN" = "1" ]; then
    echo ""
    echo -e "${RED}❌ Please configure Cloudflare tunnel tokens in .env file${NC}"
    echo ""
    echo "Steps to get tokens:"
    echo "1. Go to https://dash.cloudflare.com"
    echo "2. Select your account → Zero Trust → Access → Tunnels"
    echo "3. Click 'Create a tunnel'"
    echo "4. Name it (e.g., 'developer-galion-app')"
    echo "5. Select 'Docker' connector"
    echo "6. Copy the token"
    echo "7. Add to .env file: CF_TUNNEL_TOKEN_DEVELOPER=your-token"
    echo "8. Repeat for galion.app and galion.studio"
    echo ""
    exit 1
fi

# Start tunnels
echo ""
echo -e "${BLUE}[3/3] Starting Cloudflare tunnels...${NC}"
echo ""

# Stop existing tunnels
pkill -f cloudflared || true
sleep 2

# Start developer.galion.app tunnel
echo -e "${BLUE}Starting tunnel for developer.galion.app...${NC}"
nohup cloudflared tunnel --config cloudflare-tunnel-developer-galion-app.yml run --token "$CF_TUNNEL_TOKEN_DEVELOPER" > /tmp/cf-tunnel-developer.log 2>&1 &
echo -e "${GREEN}✓ Tunnel started (PID: $!)${NC}"

# Start galion.app tunnel
echo -e "${BLUE}Starting tunnel for galion.app...${NC}"
nohup cloudflared tunnel --config cloudflare-tunnel-galion-app.yml run --token "$CF_TUNNEL_TOKEN_APP" > /tmp/cf-tunnel-app.log 2>&1 &
echo -e "${GREEN}✓ Tunnel started (PID: $!)${NC}"

# Start galion.studio tunnel
echo -e "${BLUE}Starting tunnel for galion.studio...${NC}"
nohup cloudflared tunnel --config cloudflare-tunnel-galion-studio.yml run --token "$CF_TUNNEL_TOKEN_STUDIO" > /tmp/cf-tunnel-studio.log 2>&1 &
echo -e "${GREEN}✓ Tunnel started (PID: $!)${NC}"

# Wait for tunnels to establish
echo ""
echo -e "${BLUE}Waiting for tunnels to establish...${NC}"
sleep 5

# Check tunnel status
echo ""
echo "=========================================="
echo "   Tunnel Status"
echo "=========================================="
echo ""

ps aux | grep cloudflared | grep -v grep || echo -e "${RED}No tunnels running${NC}"

echo ""
echo -e "${GREEN}✓ Cloudflare tunnels configured!${NC}"
echo ""
echo "Your apps should now be accessible at:"
echo "  - https://developer.galion.app"
echo "  - https://galion.app"
echo "  - https://galion.studio"
echo ""
echo "View tunnel logs:"
echo "  tail -f /tmp/cf-tunnel-developer.log"
echo "  tail -f /tmp/cf-tunnel-app.log"
echo "  tail -f /tmp/cf-tunnel-studio.log"
echo ""
echo "Stop tunnels:"
echo "  pkill -f cloudflared"
echo ""

