#!/bin/bash
# Quick Deploy NexusLang v2 to Server
# Run this script on your server after uploading files

set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║     🚀 NEXUSLANG V2 - SERVER DEPLOYMENT 🚀           ║"
echo "║                                                        ║"
echo "║     Deploying to developer.galion.app                  ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️  Please run as root or with sudo${NC}"
    exit 1
fi

echo -e "${CYAN}📋 Step 1: Installing System Dependencies...${NC}"
echo ""

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    apt install docker-compose -y
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi

# Install Python
if ! command -v python3.11 &> /dev/null; then
    echo "Installing Python 3.11..."
    apt install software-properties-common -y
    add-apt-repository ppa:deadsnakes/ppa -y
    apt update
    apt install python3.11 python3.11-venv python3-pip -y
    echo -e "${GREEN}✓ Python 3.11 installed${NC}"
else
    echo -e "${GREEN}✓ Python 3.11 already installed${NC}"
fi

# Install Nginx
if ! command -v nginx &> /dev/null; then
    echo "Installing Nginx..."
    apt install nginx -y
    systemctl enable nginx
    systemctl start nginx
    echo -e "${GREEN}✓ Nginx installed${NC}"
else
    echo -e "${GREEN}✓ Nginx already installed${NC}"
fi

echo ""
echo -e "${CYAN}📋 Step 2: Configuring Environment...${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env created${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env with your API keys before continuing!${NC}"
    echo ""
    echo "Required settings:"
    echo "  - POSTGRES_PASSWORD"
    echo "  - REDIS_PASSWORD"
    echo "  - SECRET_KEY"
    echo "  - JWT_SECRET"
    echo "  - OPENAI_API_KEY"
    echo "  - SHOPIFY_API_KEY"
    echo ""
    read -p "Press Enter after editing .env file, or Ctrl+C to exit..."
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo ""
echo -e "${CYAN}📋 Step 3: Starting Docker Services...${NC}"
echo ""

# Pull images
echo "Pulling Docker images..."
docker-compose pull

# Build services
echo "Building services..."
docker-compose build

# Start services
echo "Starting services..."
docker-compose up -d

echo -e "${GREEN}✓ Services started${NC}"

echo ""
echo -e "${CYAN}📋 Step 4: Waiting for Services to Initialize...${NC}"
echo ""

# Wait for services
echo "Waiting 60 seconds for services to start..."
sleep 60

# Check service status
echo ""
echo "Service status:"
docker-compose ps

echo ""
echo -e "${CYAN}📋 Step 5: Initializing Database...${NC}"
echo ""

# Initialize database
if [ -f "v2/database/schemas/init.sql" ]; then
    docker-compose exec -T postgres psql -U nexus -d nexus_v2 < v2/database/schemas/init.sql
    echo -e "${GREEN}✓ Database initialized${NC}"
else
    echo -e "${YELLOW}⚠️  Database schema not found${NC}"
fi

echo ""
echo -e "${CYAN}📋 Step 6: Installing NexusLang CLI...${NC}"
echo ""

# Install NexusLang
cd v2/nexuslang
pip3 install -e . > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ NexusLang v2 installed${NC}"
else
    echo -e "${YELLOW}⚠️  NexusLang installation had issues (optional)${NC}"
fi
cd ../..

echo ""
echo -e "${CYAN}📋 Step 7: Configuring Nginx...${NC}"
echo ""

# Copy Nginx config
if [ -f "v2/infrastructure/nginx/developer.galion.app.conf" ]; then
    cp v2/infrastructure/nginx/developer.galion.app.conf /etc/nginx/sites-available/developer.galion.app
    ln -sf /etc/nginx/sites-available/developer.galion.app /etc/nginx/sites-enabled/
    
    # Test configuration
    nginx -t
    
    # Reload Nginx
    systemctl reload nginx
    
    echo -e "${GREEN}✓ Nginx configured${NC}"
else
    echo -e "${YELLOW}⚠️  Nginx config not found${NC}"
fi

echo ""
echo -e "${CYAN}📋 Step 8: Configuring Firewall...${NC}"
echo ""

# Setup UFW firewall
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS
    echo "y" | ufw enable
    echo -e "${GREEN}✓ Firewall configured${NC}"
else
    echo -e "${YELLOW}⚠️  UFW not available${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                        ║${NC}"
echo -e "${GREEN}║     ✅ NEXUSLANG V2 DEPLOYED SUCCESSFULLY! ✅         ║${NC}"
echo -e "${GREEN}║                                                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}🌐 Access Points:${NC}"
echo ""
echo "  Local (on this server):"
echo -e "    ${YELLOW}• Frontend:${NC}    http://localhost:3000"
echo -e "    ${YELLOW}• Backend API:${NC} http://localhost:8000"
echo -e "    ${YELLOW}• API Docs:${NC}    http://localhost:8000/docs"
echo ""
echo "  Production (after DNS setup):"
echo -e "    ${CYAN}• Platform:${NC}    https://developer.galion.app"
echo -e "    ${CYAN}• API:${NC}         https://api.developer.galion.app"
echo ""
echo -e "${CYAN}📋 Next Steps:${NC}"
echo ""
echo "  1. Configure DNS in Cloudflare:"
echo "     A record: developer.galion.app → $(curl -s ifconfig.me)"
echo "     A record: api.developer.galion.app → $(curl -s ifconfig.me)"
echo ""
echo "  2. Setup SSL Certificate:"
echo "     sudo certbot --nginx -d developer.galion.app -d api.developer.galion.app"
echo "     OR use Cloudflare Origin Certificate (see CLOUDFLARE_SETUP_DEVELOPER.md)"
echo ""
echo "  3. Test locally:"
echo "     curl http://localhost:8000/health"
echo ""
echo "  4. View logs:"
echo "     docker-compose logs -f"
echo ""
echo -e "${GREEN}🎉 Ready to GO LIVE on developer.galion.app!${NC}"
echo ""

