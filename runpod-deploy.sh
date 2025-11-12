#!/bin/bash
# Quick Deployment Script for RunPod
# Deploys NexusLang v2 Platform on RunPod with GPU acceleration

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying NexusLang v2 to RunPod...${NC}"
echo ""

# Check if running on RunPod
if [ ! -d "/workspace" ]; then
    echo -e "${RED}⚠️ This script is designed for RunPod. /workspace not found.${NC}"
    echo "If you're testing locally, use: docker-compose up -d"
    exit 1
fi

# Change to workspace if not already there
cd /workspace/project-nexus 2>/dev/null || cd /workspace || {
    echo -e "${RED}❌ Project directory not found${NC}"
    exit 1
}

echo -e "${GREEN}✓ Running on RunPod${NC}"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚙️ Creating environment file...${NC}"
    
    cat > .env << 'EOF'
# Database Configuration
POSTGRES_PASSWORD=runpod_postgres_$(openssl rand -hex 16)
POSTGRES_USER=nexus
POSTGRES_DB=nexus_v2

# Redis Configuration
REDIS_PASSWORD=runpod_redis_$(openssl rand -hex 16)

# Security Keys
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 64)

# AI Services (ADD YOUR KEYS!)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Whisper (GPU accelerated on RunPod)
WHISPER_MODEL=base
WHISPER_DEVICE=cuda

# TTS (GPU accelerated on RunPod)
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC
TTS_DEVICE=cuda

# RunPod URLs (will be updated automatically)
RUNPOD_POD_ID=${HOSTNAME}
EOF

    # Generate actual random values
    POSTGRES_PW=$(openssl rand -hex 16)
    REDIS_PW=$(openssl rand -hex 16)
    SECRET=$(openssl rand -hex 32)
    JWT=$(openssl rand -hex 64)
    
    sed -i "s/runpod_postgres_\$(openssl rand -hex 16)/${POSTGRES_PW}/" .env
    sed -i "s/runpod_redis_\$(openssl rand -hex 16)/${REDIS_PW}/" .env
    sed -i "s/\$(openssl rand -hex 32)/${SECRET}/" .env
    sed -i "s/\$(openssl rand -hex 64)/${JWT}/" .env
    
    echo -e "${GREEN}✓ Environment file created${NC}"
    echo -e "${YELLOW}⚠️ Please edit .env and add your OpenAI API key!${NC}"
    echo ""
fi

# Source environment
source .env

# Stop existing services
echo -e "${BLUE}🛑 Stopping existing services...${NC}"
docker-compose -f docker-compose.runpod.yml down 2>/dev/null || true
echo -e "${GREEN}✓ Services stopped${NC}"
echo ""

# Pull latest images (if using pre-built)
echo -e "${BLUE}📥 Pulling Docker images...${NC}"
docker-compose -f docker-compose.runpod.yml pull 2>/dev/null || echo "Building locally..."
echo ""

# Start services
echo -e "${BLUE}🚀 Starting services with GPU acceleration...${NC}"
docker-compose -f docker-compose.runpod.yml up -d --build

echo -e "${GREEN}✓ Services starting...${NC}"
echo ""

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"

# Wait for PostgreSQL
echo -n "  Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker-compose -f docker-compose.runpod.yml exec -T postgres pg_isready -U nexus > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 2
    echo -n "."
done

# Wait for Redis
echo -n "  Waiting for Redis..."
for i in {1..15}; do
    if docker-compose -f docker-compose.runpod.yml exec -T redis redis-cli -a "$REDIS_PASSWORD" ping > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 2
    echo -n "."
done

# Wait for Backend
echo -n "  Waiting for Backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 2
    echo -n "."
done

# Wait for Frontend
echo -n "  Waiting for Frontend..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 2
    echo -n "."
done

echo ""

# Initialize database
echo -e "${BLUE}🗄️ Initializing database...${NC}"
docker-compose -f docker-compose.runpod.yml exec -T postgres psql -U nexus -d nexus_v2 << 'EOSQL'
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Extensions for full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

SELECT 'Database initialized successfully!' as status;
EOSQL

echo -e "${GREEN}✓ Database initialized${NC}"
echo ""

# Check health
echo -e "${BLUE}🏥 Checking service health...${NC}"
HEALTH=$(curl -s http://localhost:8000/health)
echo "  Backend: $HEALTH"

if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}⚠️ Backend health check failed${NC}"
fi
echo ""

# Get RunPod URLs
POD_ID=$(echo $HOSTNAME | cut -d'-' -f1 | head -c 10)
if [ -z "$POD_ID" ]; then
    POD_ID="your-pod-id"
fi

# Display access information
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✅ DEPLOYMENT COMPLETE! ✅${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📍 Access URLs (RunPod Proxy):${NC}"
echo ""
echo -e "  🌐 Frontend:  ${GREEN}https://${POD_ID}-3000.proxy.runpod.net${NC}"
echo -e "  🔧 Backend:   ${GREEN}https://${POD_ID}-8000.proxy.runpod.net${NC}"
echo -e "  📊 API Docs:  ${GREEN}https://${POD_ID}-8000.proxy.runpod.net/docs${NC}"
echo ""
echo -e "${BLUE}📍 Local URLs (for SSH tunneling):${NC}"
echo ""
echo -e "  Frontend:  http://localhost:3000"
echo -e "  Backend:   http://localhost:8000"
echo -e "  Grafana:   http://localhost:3001"
echo ""
echo -e "${BLUE}🎮 Running Services:${NC}"
docker-compose -f docker-compose.runpod.yml ps
echo ""

# Check GPU
if command -v nvidia-smi &> /dev/null; then
    echo -e "${BLUE}🎮 GPU Status:${NC}"
    nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader
    echo ""
fi

echo -e "${BLUE}💾 Data Storage:${NC}"
echo "  Database: /workspace/postgres-data"
echo "  Redis: /workspace/redis-data"
echo "  Models: /workspace/models (cached AI models)"
echo ""

echo -e "${BLUE}📝 Next Steps:${NC}"
echo "  1. Open ${GREEN}https://${POD_ID}-3000.proxy.runpod.net${NC} in your browser"
echo "  2. Register an account"
echo "  3. Try the IDE at /ide"
echo "  4. Search Grokopedia at /grokopedia"
echo "  5. Share with beta testers!"
echo ""

echo -e "${BLUE}🛠️ Management Commands:${NC}"
echo "  View logs:    docker-compose -f docker-compose.runpod.yml logs -f"
echo "  Restart:      docker-compose -f docker-compose.runpod.yml restart"
echo "  Stop:         docker-compose -f docker-compose.runpod.yml stop"
echo "  Update:       git pull && ./runpod-deploy.sh"
echo "  Backup:       /workspace/backup.sh (create this script)"
echo ""

echo -e "${GREEN}🎉 NexusLang v2 is LIVE on RunPod!${NC}"
echo ""

# Save URLs to file for easy access
cat > /workspace/RUNPOD_URLS.txt << EOF
NexusLang v2 - RunPod Deployment

Deployed: $(date)
Pod ID: ${POD_ID}

Access URLs:
-----------
Frontend: https://${POD_ID}-3000.proxy.runpod.net
Backend:  https://${POD_ID}-8000.proxy.runpod.net
API Docs: https://${POD_ID}-8000.proxy.runpod.net/docs
Grafana:  https://${POD_ID}-3001.proxy.runpod.net (optional)

Commands:
---------
View logs:  docker-compose -f docker-compose.runpod.yml logs -f
Restart:    docker-compose -f docker-compose.runpod.yml restart
Stop:       docker-compose -f docker-compose.runpod.yml stop
Health:     curl http://localhost:8000/health

Notes:
------
- All data stored in /workspace (persists between restarts)
- GPU acceleration enabled for Whisper and TTS
- Automatic HTTPS via RunPod proxy
EOF

echo -e "${GREEN}✓ URLs saved to /workspace/RUNPOD_URLS.txt${NC}"
echo ""

