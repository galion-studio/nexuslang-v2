#!/bin/bash
# ============================================
# RunPod Domain Setup Script
# ============================================
# Automatically configures nginx for galion.studio and galion.app domains
# Only sets up the 4 domains: galion.studio, galion.app, api.galion.app, developer.galion.app

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GALION PLATFORM DOMAIN SETUP${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root or with sudo${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Domains to configure:${NC}"
echo "   • galion.studio (redirects to galion.app)"
echo "   • galion.app (main app)"
echo "   • api.galion.app (backend API)"
echo "   • developer.galion.app (developer platform)"
echo ""

# Step 1: Backup current nginx config
echo -e "${BLUE}1️⃣ Backing up current nginx configuration...${NC}"
if [ -f /etc/nginx/sites-available/galion-platform ]; then
    cp /etc/nginx/sites-available/galion-platform /etc/nginx/sites-available/galion-platform.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅${NC} Backup created"
else
    echo -e "${YELLOW}⚠️${NC} No existing configuration found"
fi
echo ""

# Step 2: Download nginx configuration
echo -e "${BLUE}2️⃣ Downloading nginx configuration...${NC}"
wget -q https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/nginx-both-domains.conf -O /tmp/nginx-both-domains.conf

if [ ! -f /tmp/nginx-both-domains.conf ]; then
    echo -e "${RED}❌ Failed to download nginx configuration${NC}"
    exit 1
fi

echo -e "${GREEN}✅${NC} Configuration downloaded"
echo ""

# Step 3: Install nginx configuration
echo -e "${BLUE}3️⃣ Installing nginx configuration...${NC}"
cp /tmp/nginx-both-domains.conf /etc/nginx/sites-available/galion-platform
ln -sf /etc/nginx/sites-available/galion-platform /etc/nginx/sites-enabled/

echo -e "${GREEN}✅${NC} Configuration installed"
echo ""

# Step 4: Test nginx configuration
echo -e "${BLUE}4️⃣ Testing nginx configuration...${NC}"
if nginx -t 2>/dev/null; then
    echo -e "${GREEN}✅${NC} Nginx configuration is valid"
else
    echo -e "${RED}❌ Nginx configuration has errors${NC}"
    echo "Restoring backup..."
    if [ -f /etc/nginx/sites-available/galion-platform.backup.* ]; then
        cp /etc/nginx/sites-available/galion-platform.backup.* /etc/nginx/sites-available/galion-platform
        echo -e "${YELLOW}⚠️${NC} Backup restored"
    fi
    exit 1
fi
echo ""

# Step 5: Check services are running
echo -e "${BLUE}5️⃣ Checking PM2 services...${NC}"

# Check if PM2 is running
if ! pgrep -f "pm2" > /dev/null; then
    echo -e "${YELLOW}⚠️${NC} PM2 daemon not running, starting..."
    pm2 startup
    pm2 save
fi

# Check service status
services=("backend" "galion-app" "developer-platform")
all_running=true

for service in "${services[@]}"; do
    if pm2 describe "$service" > /dev/null 2>&1; then
        status=$(pm2 jlist | jq -r ".[] | select(.name==\"$service\") | .pm2_env.status")
        if [ "$status" = "online" ]; then
            echo -e "${GREEN}✅${NC} $service: $status"
        else
            echo -e "${RED}❌${NC} $service: $status"
            all_running=false
        fi
    else
        echo -e "${RED}❌${NC} $service: not found"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    echo ""
    echo -e "${YELLOW}⚠️${NC} Some services are not running. Starting them..."
    pm2 restart all
    sleep 3
fi
echo ""

# Step 6: Test local access
echo -e "${BLUE}6️⃣ Testing local service access...${NC}"

test_local_service() {
    local port=$1
    local name=$2

    if curl -s --max-time 5 http://localhost:$port > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $name (port $port): responding"
    else
        echo -e "${RED}❌${NC} $name (port $port): not responding"
    fi
}

test_local_service 8000 "Backend API"
test_local_service 3000 "Galion App"
test_local_service 3003 "Developer Platform"
echo ""

# Step 7: Reload nginx
echo -e "${BLUE}7️⃣ Reloading nginx...${NC}"
if systemctl reload nginx 2>/dev/null; then
    echo -e "${GREEN}✅${NC} Nginx reloaded successfully"
else
    echo -e "${YELLOW}⚠️${NC} Nginx reload failed, trying restart..."
    if systemctl restart nginx 2>/dev/null; then
        echo -e "${GREEN}✅${NC} Nginx restarted successfully"
    else
        echo -e "${RED}❌${NC} Nginx restart failed"
        exit 1
    fi
fi
echo ""

# Step 8: Verify nginx is running
echo -e "${BLUE}8️⃣ Verifying nginx status...${NC}"
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅${NC} Nginx is running"
else
    echo -e "${RED}❌${NC} Nginx is not running"
    exit 1
fi
echo ""

# Step 9: Show final configuration
echo -e "${BLUE}9️⃣ Domain routing configuration:${NC}"
echo ""
echo "📋 galion.studio:"
echo "   • galion.studio → redirects to galion.app"
echo "   • www.galion.studio → redirects to galion.app"
echo ""
echo "📋 galion.app:"
echo "   • galion.app → Galion App (port 3000)"
echo "   • www.galion.app → Galion App (port 3000)"
echo "   • api.galion.app → Backend API (port 8000)"
echo "   • developer.galion.app → Developer Platform (port 3003)"
echo ""

# Step 10: Show next steps
echo -e "${BLUE}🔄 Next Steps:${NC}"
echo "1. Add domains to Cloudflare (see CLOUDFLARE_SETUP.md)"
echo "2. Configure DNS records (see cloudflare-dns-galion-*.txt files)"
echo "3. Enable SSL/TLS in Cloudflare"
echo "4. Test external access: curl -I https://galion.app"
echo "5. Test subdomains: curl -I https://api.galion.app/health"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ DOMAIN SETUP COMPLETE!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}🎉 RunPod is now configured for multi-domain routing!${NC}"
echo ""
echo -e "${BLUE}📝 Remember to configure Cloudflare DNS for external access.${NC}"
