#!/bin/bash

# Bash Script to Start NexusLang v2 with Cloudflare Tunnels
# This script starts all services including both Cloudflare tunnels

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Display banner
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Starting NexusLang v2 with Cloudflare Tunnels            ║${NC}"
echo -e "${CYAN}║  Domains: galion.studio & galion.app                       ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Docker is running
echo -e "${YELLOW}[1/4] Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running! Please start Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose is not installed!${NC}"
    exit 1
fi

# Check if .env file exists
echo -e "\n${YELLOW}[2/4] Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [ -f "env.template" ]; then
        cp env.template .env
        echo -e "${CYAN}📝 Please edit .env file and set your environment variables${NC}"
        echo -e "${CYAN}   Required: POSTGRES_PASSWORD, REDIS_PASSWORD, SECRET_KEY, JWT_SECRET${NC}"
        exit 0
    else
        echo -e "${RED}❌ env.template not found!${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ Environment configuration found${NC}"

# Stop existing containers if running
echo -e "\n${YELLOW}[3/4] Stopping existing containers...${NC}"
docker-compose down > /dev/null 2>&1
echo -e "${GREEN}✅ Cleaned up existing containers${NC}"

# Start services with Cloudflare tunnels
echo -e "\n${YELLOW}[4/4] Starting all services...${NC}"
echo -e "${GRAY}   - PostgreSQL (Database)${NC}"
echo -e "${GRAY}   - Redis (Cache)${NC}"
echo -e "${GRAY}   - Elasticsearch (Search)${NC}"
echo -e "${GRAY}   - Backend API${NC}"
echo -e "${GRAY}   - Frontend (Next.js)${NC}"
echo -e "${GRAY}   - Prometheus (Metrics)${NC}"
echo -e "${GRAY}   - Grafana (Monitoring)${NC}"
echo -e "${GRAY}   - Cloudflare Tunnel (galion.studio)${NC}"
echo -e "${GRAY}   - Cloudflare Tunnel (galion.app)${NC}"
echo ""

# Start all services
docker-compose -f docker-compose.yml -f docker-compose.cloudflare.yml up -d

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ All services started successfully!${NC}"
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🌐 Access Your Services                                   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}📍 Local Access:${NC}"
    echo -e "${WHITE}   Frontend:    http://localhost:3000${NC}"
    echo -e "${WHITE}   Backend API: http://localhost:8000${NC}"
    echo -e "${WHITE}   Grafana:     http://localhost:3001${NC}"
    echo -e "${WHITE}   Prometheus:  http://localhost:9090${NC}"
    echo ""
    echo -e "${CYAN}🌍 Public Access via Cloudflare:${NC}"
    echo -e "${MAGENTA}   galion.studio domains:${NC}"
    echo -e "${WHITE}     https://galion.studio           (Frontend)${NC}"
    echo -e "${WHITE}     https://www.galion.studio       (Frontend)${NC}"
    echo -e "${WHITE}     https://api.galion.studio       (Backend API)${NC}"
    echo -e "${WHITE}     https://grafana.galion.studio   (Monitoring)${NC}"
    echo -e "${WHITE}     https://prometheus.galion.studio (Metrics)${NC}"
    echo ""
    echo -e "${MAGENTA}   galion.app domains:${NC}"
    echo -e "${WHITE}     https://galion.app              (Frontend)${NC}"
    echo -e "${WHITE}     https://www.galion.app          (Frontend)${NC}"
    echo -e "${WHITE}     https://api.galion.app          (Backend API)${NC}"
    echo -e "${WHITE}     https://grafana.galion.app      (Monitoring)${NC}"
    echo -e "${WHITE}     https://prometheus.galion.app   (Metrics)${NC}"
    echo ""
    echo -e "${CYAN}📊 Useful Commands:${NC}"
    echo -e "${WHITE}   View logs:         docker-compose logs -f${NC}"
    echo -e "${WHITE}   Stop services:     docker-compose down${NC}"
    echo -e "${WHITE}   Restart services:  docker-compose restart${NC}"
    echo -e "${WHITE}   View status:       docker-compose ps${NC}"
    echo ""
else
    echo -e "\n${RED}❌ Failed to start services!${NC}"
    echo -e "${YELLOW}📋 Check logs with: docker-compose logs${NC}"
    exit 1
fi

