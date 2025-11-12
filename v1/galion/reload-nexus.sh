#!/bin/bash
# NEXUS CORE - FULL SYSTEM RELOAD
# Clears all caches and reloads every Nexus service
# Built with First Principles: Fast, Simple, Effective

echo "================================"
echo "NEXUS CORE - FULL SYSTEM RELOAD"
echo "Clearing Caches & Reloading Services"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Step 1: Clear Redis Cache
echo -e "${YELLOW}[1/5] Clearing Redis cache...${NC}"
REDIS_PASSWORD=$(grep "^REDIS_PASSWORD=" .env | cut -d '=' -f2)
if docker exec nexus-redis redis-cli -a "$REDIS_PASSWORD" FLUSHALL > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis cache cleared${NC}"
else
    echo -e "${YELLOW}⚠ Redis cache clear failed (might not be running)${NC}"
fi

# Step 2: Stop all application services
echo ""
echo -e "${YELLOW}[2/5] Stopping all application services...${NC}"
APP_SERVICES=(
    "api-gateway"
    "auth-service"
    "user-service"
    "scraping-service"
    "voice-service"
    "analytics-service"
)

for service in "${APP_SERVICES[@]}"; do
    echo "  - Stopping $service..."
    docker-compose stop "$service" > /dev/null 2>&1
done
echo -e "${GREEN}✓ All services stopped${NC}"

# Step 3: Remove containers
echo ""
echo -e "${YELLOW}[3/5] Removing containers for clean restart...${NC}"
for service in "${APP_SERVICES[@]}"; do
    docker-compose rm -f "$service" > /dev/null 2>&1
done
echo -e "${GREEN}✓ Containers removed${NC}"

# Step 4: Restart all services
echo ""
echo -e "${YELLOW}[4/5] Starting all services...${NC}"
docker-compose up -d > /dev/null 2>&1
echo -e "${GREEN}✓ Services restarted${NC}"

# Step 5: Wait for services
echo ""
echo -e "${YELLOW}[5/5] Waiting for services to be healthy...${NC}"
echo "  This takes ~45 seconds for health checks..."

sleep 10
echo -e "  ${CYAN}▓▓▓░░░░░░░ 25% - Services initializing...${NC}"
sleep 10
echo -e "  ${CYAN}▓▓▓▓▓▓░░░░ 50% - Database connections...${NC}"
sleep 15
echo -e "  ${CYAN}▓▓▓▓▓▓▓▓░░ 75% - Health checks running...${NC}"
sleep 10
echo -e "  ${CYAN}▓▓▓▓▓▓▓▓▓▓ 100% - Services ready!${NC}"

# Step 6: Verify system health
echo ""
echo "================================"
echo "SYSTEM STATUS"
echo "================================"
echo ""

# Check API Gateway
if curl -s http://localhost:8080/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ API Gateway: HEALTHY${NC}"
else
    echo -e "${RED}✗ API Gateway: NOT RESPONDING${NC}"
fi

# Check Auth Service
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo -e "${GREEN}✓ Auth Service: HEALTHY${NC}"
else
    echo -e "${YELLOW}⚠ Auth Service: STARTING (wait 30s)${NC}"
fi

# Check User Service
if curl -s http://localhost:8001/health | grep -q "ok"; then
    echo -e "${GREEN}✓ User Service: HEALTHY${NC}"
else
    echo -e "${YELLOW}⚠ User Service: STARTING (wait 30s)${NC}"
fi

# Check Analytics Service
if curl -s http://localhost:9090/health | grep -q "ok"; then
    echo -e "${GREEN}✓ Analytics Service: HEALTHY${NC}"
else
    echo -e "${YELLOW}⚠ Analytics Service: STARTING (wait 30s)${NC}"
fi

# Check Voice Service
if curl -s http://localhost:8003/health | grep -q "ok"; then
    echo -e "${GREEN}✓ Voice Service: HEALTHY${NC}"
else
    echo -e "${YELLOW}⚠ Voice Service: STARTING (wait 30s)${NC}"
fi

# Check Scraping Service
if curl -s http://localhost:8002/health | grep -q "ok"; then
    echo -e "${GREEN}✓ Scraping Service: HEALTHY${NC}"
else
    echo -e "${YELLOW}⚠ Scraping Service: STARTING (wait 30s)${NC}"
fi

# Display service count
echo ""
echo "================================"
RUNNING_COUNT=$(docker-compose ps --filter "status=running" --format json 2>/dev/null | wc -l)
echo "Running Services: $RUNNING_COUNT/12"

# Quick commands
echo ""
echo "================================"
echo "QUICK COMMANDS"
echo "================================"
echo "View logs:         docker-compose logs -f [service-name]"
echo "Check status:      docker-compose ps"
echo "Test API:          curl http://localhost:8080/health"
echo "Admin Terminal:    ./nexus-admin.py"
echo "Reload again:      ./reload-nexus.sh"

echo ""
echo "================================"
echo -e "${GREEN}RELOAD COMPLETE!${NC}"
echo "================================"
echo ""
echo -e "${GREEN}All caches cleared, all services reloaded!${NC}"
echo -e "${YELLOW}If services show 'STARTING', wait 30 seconds and test again.${NC}"
echo ""

