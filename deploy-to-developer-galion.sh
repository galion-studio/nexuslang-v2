#!/bin/bash
# Deploy NexusLang v2 to developer.galion.app
# Production deployment script for Linux

set -e

echo "🚀 Deploying NexusLang v2 to developer.galion.app..."
echo ""

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="developer.galion.app"
API_DOMAIN="api.developer.galion.app"

echo -e "${CYAN}📋 Configuration:${NC}"
echo "   Domain: $DOMAIN"
echo "   API Domain: $API_DOMAIN"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env created${NC}"
    echo ""
    echo -e "${YELLOW}Please edit .env with your API keys before continuing!${NC}"
    echo "Required: POSTGRES_PASSWORD, REDIS_PASSWORD, SECRET_KEY, JWT_SECRET, OPENAI_API_KEY, SHOPIFY_API_KEY"
    echo ""
    read -p "Press Enter after editing .env..."
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed. Please install Docker first."
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker found"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not installed. Please install Docker Compose first."
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker Compose found"
echo ""

# Pull latest images
echo -e "${CYAN}📦 Pulling Docker images...${NC}"
docker-compose pull

# Build services
echo ""
echo -e "${CYAN}🔨 Building NexusLang v2 services...${NC}"
docker-compose build --no-cache

# Stop existing services
echo ""
echo -e "${CYAN}🛑 Stopping existing services...${NC}"
docker-compose down

# Start services
echo ""
echo -e "${CYAN}🚀 Starting services...${NC}"
docker-compose up -d

# Wait for services
echo ""
echo -e "${YELLOW}⏳ Waiting for services to initialize (30 seconds)...${NC}"
sleep 30

# Check status
echo ""
echo -e "${CYAN}📊 Service Status:${NC}"
docker-compose ps

# Initialize database
echo ""
echo -e "${CYAN}🗄️  Initializing database...${NC}"
if [ -f "v2/database/schemas/init.sql" ]; then
    docker-compose exec -T postgres psql -U nexus -d nexus_v2 < v2/database/schemas/init.sql
    echo -e "${GREEN}✅ Database initialized${NC}"
else
    echo -e "${YELLOW}⚠️  Database schema not found${NC}"
fi

# Install NexusLang
echo ""
echo -e "${CYAN}📦 Installing NexusLang v2...${NC}"
cd v2/nexuslang
pip install -e . > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ NexusLang v2 installed${NC}"
else
    echo -e "${YELLOW}⚠️  NexusLang installation had issues (may need manual setup)${NC}"
fi
cd ../..

# Test NexusLang
echo ""
echo -e "${CYAN}🧪 Testing NexusLang...${NC}"
cd v2/nexuslang
if [ -f "examples/personality_demo.nx" ]; then
    nexuslang run examples/personality_demo.nx > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ NexusLang working!${NC}"
    fi
fi
cd ../..

# Setup Nginx (if running on server)
if [ -f "/etc/nginx/sites-available" ]; then
    echo ""
    echo -e "${CYAN}🔧 Setting up Nginx...${NC}"
    
    # Copy nginx config
    sudo cp v2/infrastructure/nginx/developer.galion.app.conf /etc/nginx/sites-available/developer.galion.app
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/developer.galion.app /etc/nginx/sites-enabled/
    
    # Test nginx config
    sudo nginx -t
    
    # Reload nginx
    sudo systemctl reload nginx
    
    echo -e "${GREEN}✅ Nginx configured${NC}"
fi

# Setup SSL with Certbot (if available)
if command -v certbot &> /dev/null; then
    echo ""
    echo -e "${CYAN}🔒 Setting up SSL...${NC}"
    echo "Run this command to get SSL certificates:"
    echo ""
    echo "  sudo certbot --nginx -d developer.galion.app -d api.developer.galion.app"
    echo ""
fi

# Display final information
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        NEXUSLANG V2 DEPLOYED SUCCESSFULLY!                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}🌐 Access Points:${NC}"
echo ""
echo "  Local Development:"
echo -e "    ${YELLOW}• Frontend:${NC}    http://localhost:3000"
echo -e "    ${YELLOW}• Backend API:${NC} http://localhost:8000"
echo -e "    ${YELLOW}• API Docs:${NC}    http://localhost:8000/docs"
echo -e "    ${YELLOW}• Prometheus:${NC}  http://localhost:9090"
echo -e "    ${YELLOW}• Grafana:${NC}     http://localhost:3001"
echo ""
echo "  Production URLs (configure DNS first):"
echo -e "    ${CYAN}• Platform:${NC}    https://developer.galion.app"
echo -e "    ${CYAN}• API:${NC}         https://api.developer.galion.app"
echo ""
echo -e "${CYAN}📚 Useful Commands:${NC}"
echo "    docker-compose ps              # Check status"
echo "    docker-compose logs -f         # View logs"
echo "    docker-compose restart         # Restart all"
echo "    docker-compose down            # Stop all"
echo ""
echo -e "${CYAN}📖 Next Steps:${NC}"
echo "    1. Configure DNS: developer.galion.app → your server IP"
echo "    2. Setup SSL: sudo certbot --nginx -d developer.galion.app"
echo "    3. Open browser: http://localhost:3000"
echo "    4. Read: 🎯_MASTER_LAUNCH_DOCUMENT.md"
echo ""
echo -e "${GREEN}🎉 Ready to revolutionize AI development!${NC}"
echo ""

