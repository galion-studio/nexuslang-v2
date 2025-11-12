#!/bin/bash
# Install all dependencies for multi-app deployment on RunPod

set -e

echo "=========================================="
echo "Installing Dependencies for All Apps"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running on RunPod
if [ ! -d "/workspace" ]; then
    echo -e "${YELLOW}Warning: Not running on RunPod. Continue anyway? (y/n)${NC}"
    read -r response
    if [ "$response" != "y" ]; then
        exit 1
    fi
fi

# Update package lists
echo -e "${BLUE}[1/7] Updating package lists...${NC}"
apt update

# Install Node.js and npm (if not already installed)
echo -e "${BLUE}[2/7] Installing Node.js and npm...${NC}"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
else
    echo -e "${GREEN}✓ Node.js already installed: $(node --version)${NC}"
fi

if ! command -v npm &> /dev/null; then
    apt install -y npm
else
    echo -e "${GREEN}✓ npm already installed: $(npm --version)${NC}"
fi

# Install Python pip (if not already installed)
echo -e "${BLUE}[3/7] Ensuring pip is installed...${NC}"
apt install -y python3-pip python3-venv

# Install PostgreSQL client tools
echo -e "${BLUE}[4/7] Installing PostgreSQL tools...${NC}"
apt install -y postgresql-client

# Install Redis tools
echo -e "${BLUE}[5/7] Installing Redis tools...${NC}"
apt install -y redis-tools

# Install Python dependencies for developer.galion.app (NexusLang v2)
echo -e "${BLUE}[6/7] Installing Python dependencies for NexusLang v2...${NC}"
cd /workspace/nexuslang-v2/v2/backend
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ NexusLang v2 backend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ requirements.txt not found in v2/backend${NC}"
fi

# Install Python dependencies for galion.app
echo -e "${BLUE}[7/7] Installing Python dependencies for galion.app...${NC}"
if [ -d "/workspace/nexuslang-v2/v1/galion/backend" ]; then
    cd /workspace/nexuslang-v2/v1/galion/backend
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo -e "${GREEN}✓ Galion.app backend dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠ requirements.txt not found in v1/galion/backend${NC}"
    fi
else
    echo -e "${YELLOW}⚠ v1/galion directory not found${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✓ All Dependencies Installed!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Configure environment: cp env.runpod.multi-apps .env"
echo "2. Generate secrets: ./generate-secrets.sh"
echo "3. Start services: ./deploy-all-apps.sh"
echo ""

