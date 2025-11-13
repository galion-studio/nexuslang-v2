#!/bin/bash
#
# Production Deployment Script for Galion Ecosystem
# Deploys all services using Docker Compose
#
# Usage: ./deploy.sh [--no-build] [--logs]

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="docker-compose.production.yml"
BUILD=true
SHOW_LOGS=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --no-build)
            BUILD=false
            shift
            ;;
        --logs)
            SHOW_LOGS=true
            shift
            ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                        ║${NC}"
echo -e "${BLUE}║        Galion Ecosystem Deployment Script             ║${NC}"
echo -e "${BLUE}║                                                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}Step 1: Checking prerequisites...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f "v2/.env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found in v2/ directory${NC}"
    echo -e "${YELLOW}   Using default credentials from docker-compose${NC}"
fi

echo -e "${GREEN}✅ Prerequisites met${NC}"
echo ""

echo -e "${GREEN}Step 2: Stopping existing containers...${NC}"
docker-compose -f $COMPOSE_FILE down || true
echo -e "${GREEN}✅ Stopped existing containers${NC}"
echo ""

if [ "$BUILD" = true ]; then
    echo -e "${GREEN}Step 3: Building services...${NC}"
    docker-compose -f $COMPOSE_FILE build --no-cache
    echo -e "${GREEN}✅ Services built${NC}"
    echo ""
fi

echo -e "${GREEN}Step 4: Starting services...${NC}"
docker-compose -f $COMPOSE_FILE up -d

echo ""
echo -e "${GREEN}Step 5: Waiting for services to be healthy...${NC}"
sleep 10  # Give services time to start

# Check health of each service
echo ""
echo -e "${BLUE}Service Health Check:${NC}"

# Check Postgres
if docker exec nexus-postgres pg_isready -U nexus &> /dev/null; then
    echo -e "  ${GREEN}✅ PostgreSQL${NC}"
else
    echo -e "  ${RED}❌ PostgreSQL${NC}"
fi

# Check Redis
if docker exec nexus-redis redis-cli --no-auth-warning -a "${REDIS_PASSWORD:-7aHZpW9xR4mN8qL3vK6jT1yB5cZ0fG2s}" ping &> /dev/null; then
    echo -e "  ${GREEN}✅ Redis${NC}"
else
    echo -e "  ${RED}❌ Redis${NC}"
fi

# Check Backend
if curl -sf http://localhost:8000/health &> /dev/null; then
    echo -e "  ${GREEN}✅ Backend API${NC}"
else
    echo -e "  ${YELLOW}⚠️  Backend API (may still be starting...)${NC}"
fi

# Check Developer Frontend
if curl -sf http://localhost:3000 &> /dev/null; then
    echo -e "  ${GREEN}✅ developer.galion.app${NC}"
else
    echo -e "  ${YELLOW}⚠️  developer.galion.app (may still be starting...)${NC}"
fi

# Check Galion Studio
if curl -sf http://localhost:3001 &> /dev/null; then
    echo -e "  ${GREEN}✅ galion.studio${NC}"
else
    echo -e "  ${YELLOW}⚠️  galion.studio (may still be starting...)${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Access your services:"
echo ""
echo -e "  🌐 Backend API:          ${BLUE}http://localhost:8000${NC}"
echo -e "  📚 API Docs:             ${BLUE}http://localhost:8000/docs${NC}"
echo -e "  🌐 developer.galion.app: ${BLUE}http://localhost:3000${NC}"
echo -e "  🌐 galion.studio:        ${BLUE}http://localhost:3001${NC}"
echo ""
echo "Manage services:"
echo ""
echo "  • View logs:    docker-compose -f $COMPOSE_FILE logs -f"
echo "  • Stop all:     docker-compose -f $COMPOSE_FILE down"
echo "  • Restart:      docker-compose -f $COMPOSE_FILE restart"
echo "  • Status:       docker-compose -f $COMPOSE_FILE ps"
echo ""

if [ "$SHOW_LOGS" = true ]; then
    echo -e "${BLUE}Showing logs (Ctrl+C to exit):${NC}"
    echo ""
    docker-compose -f $COMPOSE_FILE logs -f
fi

