#!/bin/bash
# Master deployment script for all three Galion apps on RunPod
# Run this script to deploy everything in one command

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║                                                ║"
echo "║     GALION PLATFORM DEPLOYMENT ON RUNPOD       ║"
echo "║                                                ║"
echo "║  deploying: developer.galion.app               ║"
echo "║             galion.app                         ║"
echo "║             galion.studio                      ║"
echo "║                                                ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Make all scripts executable
echo -e "${BLUE}Making scripts executable...${NC}"
chmod +x install-dependencies.sh
chmod +x generate-secrets.sh
chmod +x deploy-all-apps.sh
chmod +x setup-cloudflare-tunnels.sh
chmod +x test-deployment.sh
echo -e "${GREEN}✓ Scripts ready${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo ""
    echo "Creating .env from template..."
    cp env.runpod.multi-apps .env
    
    echo ""
    echo "Generating secure secrets..."
    ./generate-secrets.sh > .env.secrets
    
    echo ""
    echo -e "${YELLOW}IMPORTANT: Add these secrets to your .env file:${NC}"
    cat .env.secrets
    echo ""
    echo -e "${YELLOW}Press ENTER after you've updated .env file...${NC}"
    read -r
    
    rm .env.secrets
fi

# Step 1: Install dependencies
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 1/4: Installing Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
./install-dependencies.sh

# Step 2: Deploy all apps
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 2/4: Deploying All Applications${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
./deploy-all-apps.sh

# Step 3: Test deployment
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 3/4: Testing Deployment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
./test-deployment.sh

# Step 4: Setup Cloudflare (optional)
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 4/4: Cloudflare Tunnels (Optional)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Do you want to setup Cloudflare tunnels for public access? (y/n)${NC}"
read -r response

if [ "$response" = "y" ]; then
    echo ""
    echo "Make sure you have Cloudflare tunnel tokens in your .env file"
    echo "Press ENTER to continue, or Ctrl+C to skip..."
    read -r
    ./setup-cloudflare-tunnels.sh
else
    echo ""
    echo -e "${YELLOW}Skipping Cloudflare setup${NC}"
    echo "You can run ./setup-cloudflare-tunnels.sh later"
fi

# Final summary
echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║                                                ║"
echo "║          ✅ DEPLOYMENT COMPLETE! ✅            ║"
echo "║                                                ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

POD_ID=$(hostname)

echo -e "${GREEN}🚀 Your apps are now running!${NC}"
echo ""
echo -e "${BLUE}Access via RunPod Proxy:${NC}"
echo "  developer.galion.app:"
echo "    Frontend: https://${POD_ID}-3000.proxy.runpod.net"
echo "    Backend:  https://${POD_ID}-8000.proxy.runpod.net"
echo ""
echo "  galion.app:"
echo "    Frontend: https://${POD_ID}-3100.proxy.runpod.net"
echo "    Backend:  https://${POD_ID}-8100.proxy.runpod.net"
echo ""
echo "  galion.studio:"
echo "    Frontend: https://${POD_ID}-3200.proxy.runpod.net"
echo "    Backend:  https://${POD_ID}-8200.proxy.runpod.net"
echo ""

if [ "$response" = "y" ]; then
    echo -e "${BLUE}Public URLs (via Cloudflare):${NC}"
    echo "  https://developer.galion.app"
    echo "  https://galion.app"
    echo "  https://galion.studio"
    echo ""
fi

echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs:        tail -f /tmp/developer-backend.log"
echo "  Test deployment:  ./test-deployment.sh"
echo "  Stop services:    pkill -f uvicorn && pkill -f next"
echo "  Restart:          ./deploy-all-apps.sh"
echo ""
echo -e "${GREEN}📚 Full documentation: DEPLOYMENT_COMPLETE_GUIDE.md${NC}"
echo ""

