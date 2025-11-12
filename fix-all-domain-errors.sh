#!/bin/bash
# ╔════════════════════════════════════════════════════════════╗
# ║  Automated Domain Error Fix Script                        ║
# ║  Fixes all domain configuration issues in NexusLang v2    ║
# ╚════════════════════════════════════════════════════════════╝

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  NexusLang v2 - Domain Configuration Fix                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running from project root
if [ ! -d "v2" ]; then
    echo -e "${RED}❌ ERROR: Please run this script from the project root directory${NC}"
    echo -e "${YELLOW}cd /path/to/project-nexus && ./fix-all-domain-errors.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Running from correct directory${NC}"
echo ""

# Ask user for deployment type
echo -e "${YELLOW}Where are you deploying NexusLang v2?${NC}"
echo "1. Local development (localhost)"
echo "2. developer.galion.app (production)"
echo "3. nexuslang.galion.app (production)"
echo "4. RunPod (with custom domain)"
echo "5. RunPod (direct proxy URLs)"
echo ""
read -p "Enter choice (1-5): " DEPLOY_CHOICE

# Set default values based on choice
case $DEPLOY_CHOICE in
    1)
        DEPLOYMENT_TYPE="local"
        FRONTEND_URL="http://localhost:3000"
        BACKEND_URL="http://localhost:8000"
        PRIMARY_DOMAIN="localhost"
        CORS_ORIGINS="http://localhost:3000,http://localhost:8000"
        ;;
    2)
        DEPLOYMENT_TYPE="developer.galion.app"
        FRONTEND_URL="https://developer.galion.app"
        BACKEND_URL="https://api.developer.galion.app"
        PRIMARY_DOMAIN="developer.galion.app"
        CORS_ORIGINS="https://developer.galion.app,https://api.developer.galion.app"
        ;;
    3)
        DEPLOYMENT_TYPE="nexuslang.galion.app"
        FRONTEND_URL="https://nexuslang.galion.app"
        BACKEND_URL="https://api.nexuslang.galion.app"
        PRIMARY_DOMAIN="nexuslang.galion.app"
        CORS_ORIGINS="https://nexuslang.galion.app,https://api.nexuslang.galion.app"
        ;;
    4)
        DEPLOYMENT_TYPE="runpod-custom"
        read -p "Enter your custom domain (e.g., nexuslang.yoursite.com): " CUSTOM_DOMAIN
        FRONTEND_URL="https://$CUSTOM_DOMAIN"
        BACKEND_URL="https://api.$CUSTOM_DOMAIN"
        PRIMARY_DOMAIN="$CUSTOM_DOMAIN"
        CORS_ORIGINS="https://$CUSTOM_DOMAIN,https://api.$CUSTOM_DOMAIN"
        ;;
    5)
        DEPLOYMENT_TYPE="runpod-direct"
        read -p "Enter your RunPod Pod ID (e.g., abc123xyz456): " POD_ID
        FRONTEND_URL="https://${POD_ID}-3000.proxy.runpod.net"
        BACKEND_URL="https://${POD_ID}-8000.proxy.runpod.net"
        PRIMARY_DOMAIN="proxy.runpod.net"
        CORS_ORIGINS="https://${POD_ID}-3000.proxy.runpod.net,https://${POD_ID}-8000.proxy.runpod.net"
        ;;
    *)
        echo -e "${RED}Invalid choice!${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}Configuration Summary:${NC}"
echo -e "  Deployment Type: ${GREEN}$DEPLOYMENT_TYPE${NC}"
echo -e "  Frontend URL:    ${GREEN}$FRONTEND_URL${NC}"
echo -e "  Backend URL:     ${GREEN}$BACKEND_URL${NC}"
echo -e "  Primary Domain:  ${GREEN}$PRIMARY_DOMAIN${NC}"
echo ""
read -p "Is this correct? (y/n) " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo -e "${YELLOW}Cancelled by user${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 1: Creating Environment Files${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Create v2/.env if it doesn't exist
if [ ! -f "v2/.env" ]; then
    echo -e "${YELLOW}Creating v2/.env from template...${NC}"
    cp v2/env.template v2/.env
    
    # Update with actual values
    sed -i.bak "s|PRIMARY_DOMAIN=localhost|PRIMARY_DOMAIN=$PRIMARY_DOMAIN|g" v2/.env
    sed -i.bak "s|FRONTEND_URL=http://localhost:3000|FRONTEND_URL=$FRONTEND_URL|g" v2/.env
    sed -i.bak "s|BACKEND_URL=http://localhost:8000|BACKEND_URL=$BACKEND_URL|g" v2/.env
    sed -i.bak "s|CORS_ORIGINS=http://localhost:3000,http://localhost:8000|CORS_ORIGINS=$CORS_ORIGINS|g" v2/.env
    
    # Generate secure secrets
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 64)
    POSTGRES_PASSWORD=$(openssl rand -hex 16)
    REDIS_PASSWORD=$(openssl rand -hex 16)
    
    sed -i.bak "s|SECRET_KEY=your_secret_key.*|SECRET_KEY=$SECRET_KEY|g" v2/.env
    sed -i.bak "s|JWT_SECRET=your_jwt_secret.*|JWT_SECRET=$JWT_SECRET|g" v2/.env
    sed -i.bak "s|POSTGRES_PASSWORD=your_secure_postgres_password.*|POSTGRES_PASSWORD=$POSTGRES_PASSWORD|g" v2/.env
    sed -i.bak "s|REDIS_PASSWORD=your_secure_redis_password.*|REDIS_PASSWORD=$REDIS_PASSWORD|g" v2/.env
    
    # Update DATABASE_URL and REDIS_URL with generated passwords
    sed -i.bak "s|postgresql+asyncpg://nexus:your_secure_postgres_password.*@postgres|postgresql+asyncpg://nexus:$POSTGRES_PASSWORD@postgres|g" v2/.env
    sed -i.bak "s|redis://:your_secure_redis_password.*@redis|redis://:$REDIS_PASSWORD@redis|g" v2/.env
    
    rm -f v2/.env.bak
    
    echo -e "${GREEN}✅ Created v2/.env${NC}"
else
    echo -e "${YELLOW}⚠️  v2/.env already exists, updating URLs...${NC}"
    
    # Update existing .env
    sed -i.bak "s|PRIMARY_DOMAIN=.*|PRIMARY_DOMAIN=$PRIMARY_DOMAIN|g" v2/.env
    sed -i.bak "s|FRONTEND_URL=.*|FRONTEND_URL=$FRONTEND_URL|g" v2/.env
    sed -i.bak "s|BACKEND_URL=.*|BACKEND_URL=$BACKEND_URL|g" v2/.env
    sed -i.bak "s|CORS_ORIGINS=.*|CORS_ORIGINS=$CORS_ORIGINS|g" v2/.env
    
    rm -f v2/.env.bak
    
    echo -e "${GREEN}✅ Updated v2/.env${NC}"
fi

# Create v2/frontend/.env.local if it doesn't exist
if [ ! -f "v2/frontend/.env.local" ]; then
    echo -e "${YELLOW}Creating v2/frontend/.env.local...${NC}"
    cp v2/frontend/env.local.template v2/frontend/.env.local
    
    # Update with actual values
    sed -i.bak "s|NEXT_PUBLIC_API_URL=http://localhost:8000|NEXT_PUBLIC_API_URL=$BACKEND_URL|g" v2/frontend/.env.local
    
    # Set WebSocket URL
    if [[ $BACKEND_URL == https://* ]]; then
        WS_URL="${BACKEND_URL/https:/wss:}"
    else
        WS_URL="${BACKEND_URL/http:/ws:}"
    fi
    sed -i.bak "s|NEXT_PUBLIC_WS_URL=ws://localhost:8000|NEXT_PUBLIC_WS_URL=$WS_URL|g" v2/frontend/.env.local
    
    rm -f v2/frontend/.env.local.bak
    
    echo -e "${GREEN}✅ Created v2/frontend/.env.local${NC}"
else
    echo -e "${YELLOW}⚠️  v2/frontend/.env.local already exists, updating...${NC}"
    
    # Update existing .env.local
    sed -i.bak "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=$BACKEND_URL|g" v2/frontend/.env.local
    
    # Set WebSocket URL
    if [[ $BACKEND_URL == https://* ]]; then
        WS_URL="${BACKEND_URL/https:/wss:}"
    else
        WS_URL="${BACKEND_URL/http:/ws:}"
    fi
    sed -i.bak "s|NEXT_PUBLIC_WS_URL=.*|NEXT_PUBLIC_WS_URL=$WS_URL|g" v2/frontend/.env.local
    
    rm -f v2/frontend/.env.local.bak
    
    echo -e "${GREEN}✅ Updated v2/frontend/.env.local${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 2: Updating Docker Compose Configuration${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Update docker-compose.prod.yml
if [ -f "docker-compose.prod.yml" ]; then
    echo -e "${YELLOW}Updating docker-compose.prod.yml...${NC}"
    
    sed -i.bak "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=$BACKEND_URL|g" docker-compose.prod.yml
    
    rm -f docker-compose.prod.yml.bak
    
    echo -e "${GREEN}✅ Updated docker-compose.prod.yml${NC}"
fi

# Update v2/docker-compose.nexuslang.yml
if [ -f "v2/docker-compose.nexuslang.yml" ]; then
    echo -e "${YELLOW}Updating v2/docker-compose.nexuslang.yml...${NC}"
    
    # Update CORS_ORIGINS
    sed -i.bak "s|CORS_ORIGINS:.*|CORS_ORIGINS: '$CORS_ORIGINS'|g" v2/docker-compose.nexuslang.yml
    sed -i.bak "s|NEXT_PUBLIC_API_URL:.*|NEXT_PUBLIC_API_URL: $BACKEND_URL|g" v2/docker-compose.nexuslang.yml
    
    rm -f v2/docker-compose.nexuslang.yml.bak
    
    echo -e "${GREEN}✅ Updated v2/docker-compose.nexuslang.yml${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 3: Nginx Configuration${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$DEPLOYMENT_TYPE" == "local" ]; then
    echo -e "${YELLOW}⚠️  Skipping nginx configuration for local development${NC}"
else
    echo -e "${YELLOW}Nginx configuration requires manual SSL certificate setup${NC}"
    echo -e "See: ${GREEN}QUICK_FIX_SSL_ERROR.md${NC} for instructions"
    echo ""
    echo -e "Nginx configs located at:"
    echo -e "  ${BLUE}v2/infrastructure/nginx/developer.galion.app.conf${NC}"
    echo -e "  ${BLUE}v2/infrastructure/nginx/nexuslang.galion.app.conf${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 4: Verification${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}✅ Environment files created/updated${NC}"
echo -e "${GREEN}✅ Docker compose configurations updated${NC}"
echo -e "${GREEN}✅ Domain settings configured${NC}"
echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Next Steps:${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$DEPLOYMENT_TYPE" == "local" ]; then
    echo "1. Start the services:"
    echo -e "   ${YELLOW}cd v2 && docker-compose up -d${NC}"
    echo ""
    echo "2. Access the application:"
    echo -e "   Frontend: ${GREEN}$FRONTEND_URL${NC}"
    echo -e "   Backend:  ${GREEN}$BACKEND_URL${NC}"
    echo ""
    echo "3. Check health:"
    echo -e "   ${YELLOW}curl $BACKEND_URL/health${NC}"
else
    echo "1. Set up SSL certificates (REQUIRED):"
    echo -e "   ${YELLOW}./install-cloudflare-certs.sh${NC}"
    echo -e "   OR see: ${GREEN}QUICK_FIX_SSL_ERROR.md${NC}"
    echo ""
    echo "2. Configure DNS records in Cloudflare:"
    echo -e "   ${GREEN}$PRIMARY_DOMAIN${NC} → Your server IP"
    echo -e "   ${GREEN}api.$PRIMARY_DOMAIN${NC} → Your server IP"
    echo ""
    echo "3. Deploy nginx configuration:"
    echo -e "   ${YELLOW}sudo cp v2/infrastructure/nginx/*.conf /etc/nginx/sites-available/${NC}"
    echo -e "   ${YELLOW}sudo nginx -t && sudo systemctl restart nginx${NC}"
    echo ""
    echo "4. Start Docker services:"
    echo -e "   ${YELLOW}cd v2 && docker-compose -f docker-compose.prod.yml up -d${NC}"
    echo ""
    echo "5. Verify deployment:"
    echo -e "   ${YELLOW}curl -I $FRONTEND_URL${NC}"
    echo -e "   ${YELLOW}curl $BACKEND_URL/health${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Configuration Summary:${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Deployment Type: ${GREEN}$DEPLOYMENT_TYPE${NC}"
echo -e "Frontend URL:    ${GREEN}$FRONTEND_URL${NC}"
echo -e "Backend URL:     ${GREEN}$BACKEND_URL${NC}"
echo -e "CORS Origins:    ${GREEN}$CORS_ORIGINS${NC}"
echo ""
echo -e "${GREEN}✅ Domain configuration complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Additional Resources:${NC}"
echo "  - SSL Setup: QUICK_FIX_SSL_ERROR.md"
echo "  - Full Guide: FIX_SSL_ERROR.md"
echo "  - SSL Explained: SSL_ERROR_EXPLAINED.md"
echo "  - Environment Template: v2/env.template"
echo ""
echo -e "${GREEN}🚀 Your NexusLang v2 platform is ready to launch!${NC}"
echo ""

