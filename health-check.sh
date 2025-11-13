#!/bin/bash
#
# Health Check Script for Galion Ecosystem
# Verifies all services are running and responding
#
# Usage: ./health-check.sh
# Exit code: 0 if all healthy, 1 if any service is down

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Checking Galion Ecosystem Health..."
echo ""

ALL_HEALTHY=true

# Check PostgreSQL
echo -n "PostgreSQL (port 5432): "
if pg_isready -h localhost -U nexus &> /dev/null || docker exec nexus-postgres pg_isready -U nexus &> /dev/null; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Down${NC}"
    ALL_HEALTHY=false
fi

# Check Redis
echo -n "Redis (port 6379):      "
if redis-cli ping &> /dev/null || docker exec nexus-redis redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Down${NC}"
    ALL_HEALTHY=false
fi

# Check Backend API
echo -n "Backend API (8000):     "
if curl -sf http://localhost:8000/health &> /dev/null; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Down${NC}"
    ALL_HEALTHY=false
fi

# Check Developer Frontend
echo -n "developer.galion (3000):"
if curl -sf http://localhost:3000 &> /dev/null; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Down${NC}"
    ALL_HEALTHY=false
fi

# Check Galion Studio
echo -n "galion.studio (3001):   "
if curl -sf http://localhost:3001 &> /dev/null; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Down${NC}"
    ALL_HEALTHY=false
fi

echo ""

if [ "$ALL_HEALTHY" = true ]; then
    echo -e "${GREEN}✅ All services are healthy!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some services are not healthy${NC}"
    echo ""
    echo "Check logs:"
    echo "  docker-compose -f docker-compose.production.yml logs"
    exit 1
fi

