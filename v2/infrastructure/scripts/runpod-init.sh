#!/bin/bash
# RunPod Pod Initialization Script
# Run this ONCE when setting up a new RunPod pod

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🎮 Initializing RunPod for NexusLang v2...${NC}"
echo ""

# Verify we're on RunPod
if [ ! -d "/workspace" ]; then
    echo -e "${YELLOW}⚠️ This doesn't look like a RunPod pod${NC}"
    echo "Creating /workspace for compatibility..."
    mkdir -p /workspace
fi

# Update system
echo -e "${BLUE}📦 Updating system packages...${NC}"
apt-get update -qq
apt-get install -y -qq curl wget git jq htop iotop vim nano openssl

echo -e "${GREEN}✓ System updated${NC}"
echo ""

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}🐳 Installing Docker Compose...${NC}"
    apt-get install -y docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi
echo ""

# Create directory structure
echo -e "${BLUE}📁 Creating directory structure...${NC}"
mkdir -p /workspace/{postgres-data,redis-data,models,backups,uploads}
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Check GPU
if command -v nvidia-smi &> /dev/null; then
    echo -e "${BLUE}🎮 GPU detected:${NC}"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo -e "${GREEN}✓ GPU acceleration available!${NC}"
else
    echo -e "${YELLOW}⚠️ No GPU detected - will use CPU${NC}"
fi
echo ""

# Clone repository (if not exists)
if [ ! -d "/workspace/project-nexus" ]; then
    echo -e "${BLUE}📥 Cloning repository...${NC}"
    cd /workspace
    
    echo "Enter your GitHub repository URL:"
    echo "(e.g., https://github.com/your-org/project-nexus.git)"
    read -p "URL: " REPO_URL
    
    if [ -n "$REPO_URL" ]; then
        git clone $REPO_URL /workspace/project-nexus
        echo -e "${GREEN}✓ Repository cloned${NC}"
    else
        echo -e "${YELLOW}⚠️ No URL provided. You'll need to upload files manually.${NC}"
    fi
else
    echo -e "${GREEN}✓ Repository already exists${NC}"
fi
echo ""

# Create convenience aliases
echo -e "${BLUE}⚙️ Setting up aliases...${NC}"
cat >> ~/.bashrc << 'EOF'

# NexusLang v2 Aliases
alias nx='cd /workspace/project-nexus'
alias nxlogs='docker-compose -f docker-compose.runpod.yml logs -f'
alias nxps='docker-compose -f docker-compose.runpod.yml ps'
alias nxrestart='docker-compose -f docker-compose.runpod.yml restart'
alias nxstop='docker-compose -f docker-compose.runpod.yml stop'
alias nxstart='docker-compose -f docker-compose.runpod.yml start'
alias nxhealth='curl -s http://localhost:8000/health | jq .'
alias nxgpu='watch -n 1 nvidia-smi'
EOF

source ~/.bashrc
echo -e "${GREEN}✓ Aliases configured${NC}"
echo ""

# Create auto-start script
echo -e "${BLUE}🔄 Creating auto-start script...${NC}"
cat > /workspace/autostart.sh << 'EOF'
#!/bin/bash
# Auto-start NexusLang v2 on pod boot

cd /workspace/project-nexus
docker-compose -f docker-compose.runpod.yml up -d

echo "✅ NexusLang v2 services started"
EOF

chmod +x /workspace/autostart.sh
echo -e "${GREEN}✓ Auto-start script created${NC}"
echo ""

# Get pod info
POD_ID=$(hostname | cut -d'-' -f1 | head -c 10)

# Final instructions
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✅ RUNPOD INITIALIZATION COMPLETE!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📍 Your Pod ID:${NC} ${GREEN}${POD_ID}${NC}"
echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo ""
echo "1. Go to repository:"
echo -e "   ${GREEN}cd /workspace/project-nexus${NC}"
echo ""
echo "2. Configure environment:"
echo -e "   ${GREEN}cp env.runpod.template .env${NC}"
echo -e "   ${GREEN}nano .env${NC}  # Add your API keys"
echo ""
echo "3. Deploy platform:"
echo -e "   ${GREEN}./runpod-deploy.sh${NC}"
echo ""
echo "4. Access your platform:"
echo -e "   ${GREEN}https://${POD_ID}-3000.proxy.runpod.net${NC}"
echo ""
echo -e "${BLUE}💡 Useful Aliases:${NC}"
echo "  nx        - Go to project directory"
echo "  nxlogs    - View all logs"
echo "  nxps      - Check service status"
echo "  nxrestart - Restart all services"
echo "  nxhealth  - Check backend health"
echo "  nxgpu     - Monitor GPU usage"
echo ""
echo -e "${GREEN}🎉 Happy building!${NC}"
echo ""

