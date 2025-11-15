#!/bin/bash
# ============================================
# Setup Nginx on RunPod with Subdomain Routing
# ============================================
# Automated script to configure nginx for Galion Platform

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  NGINX SUBDOMAIN ROUTING SETUP${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

# Step 1: Install nginx if not present
echo -e "${BLUE}[1/6] Checking nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    echo "Installing nginx..."
    apt-get update -qq
    apt-get install -y nginx
    echo -e "${GREEN}✓${NC} Nginx installed"
else
    echo -e "${GREEN}✓${NC} Nginx already installed"
fi
echo ""

# Step 2: Stop nginx to configure
echo -e "${BLUE}[2/6] Stopping nginx...${NC}"
systemctl stop nginx 2>/dev/null || service nginx stop 2>/dev/null || true
echo -e "${GREEN}✓${NC} Nginx stopped"
echo ""

# Step 3: Download configuration
echo -e "${BLUE}[3/6] Downloading nginx configuration...${NC}"
cd /etc/nginx/sites-available
wget -O galion-platform https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/nginx-subdomain-routing.conf
echo -e "${GREEN}✓${NC} Configuration downloaded"
echo ""

# Step 4: Enable site
echo -e "${BLUE}[4/6] Enabling site...${NC}"
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/galion-platform /etc/nginx/sites-enabled/galion-platform
echo -e "${GREEN}✓${NC} Site enabled"
echo ""

# Step 5: Test configuration
echo -e "${BLUE}[5/6] Testing nginx configuration...${NC}"
if nginx -t; then
    echo -e "${GREEN}✓${NC} Configuration valid"
else
    echo -e "${RED}✗${NC} Configuration has errors"
    exit 1
fi
echo ""

# Step 6: Start nginx
echo -e "${BLUE}[6/6] Starting nginx...${NC}"
systemctl start nginx 2>/dev/null || service nginx start
systemctl enable nginx 2>/dev/null || true
echo -e "${GREEN}✓${NC} Nginx started"
echo ""

# Verify nginx is running
if systemctl is-active --quiet nginx 2>/dev/null || service nginx status 2>/dev/null | grep -q "running"; then
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}✅ NGINX SETUP COMPLETE!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "${BLUE}Nginx is now routing:${NC}"
    echo "  • api.galion.studio      → Backend (8000)"
    echo "  • studio.galion.studio   → Galion Studio (3030)"
    echo "  • app.galion.studio      → Galion App (3000)"
    echo "  • dev.galion.studio      → Developer Platform (3003)"
    echo ""
    echo -e "${YELLOW}NEXT STEPS:${NC}"
    echo "1. Configure Cloudflare DNS (see CLOUDFLARE_SETUP.md)"
    echo "2. Test locally: curl -H 'Host: api.galion.studio' http://localhost/health"
    echo "3. Wait for DNS propagation (2-5 minutes)"
    echo "4. Test externally: curl https://api.galion.studio/health"
else
    echo -e "${RED}✗ Nginx failed to start${NC}"
    exit 1
fi

echo ""

