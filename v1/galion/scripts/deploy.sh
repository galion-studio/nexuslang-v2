#!/bin/bash
# Zero-downtime deployment script for GALION
# Performs rolling updates service by service
# Usage: ./scripts/deploy.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Zero-Downtime Deployment                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check service health
check_health() {
    local port=$1
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s http://localhost:$port/health >/dev/null 2>&1; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    return 1
}

# Function to deploy a service with zero downtime
deploy_service() {
    local service=$1
    local health_port=$2
    
    echo -e "${YELLOW}Deploying $service...${NC}"
    
    # Build new image
    echo "  Building new image..."
    docker compose build $service
    
    # Get current container ID
    OLD_CONTAINER=$(docker compose ps -q $service)
    
    # Start new container alongside old one
    echo "  Starting new container..."
    docker compose up -d --no-deps --scale $service=2 $service
    
    # Wait for new container to be healthy
    echo "  Waiting for health check..."
    sleep 10  # Initial wait for startup
    
    if [ -n "$health_port" ]; then
        if check_health $health_port; then
            echo -e "  ${GREEN}✓ New container is healthy${NC}"
        else
            echo -e "  ${RED}✗ Health check failed, rolling back...${NC}"
            docker compose up -d --no-deps --scale $service=1 $service
            docker stop $(docker compose ps -q $service | grep -v $OLD_CONTAINER) 2>/dev/null || true
            return 1
        fi
    else
        # For frontends without health port, just wait
        sleep 20
        echo -e "  ${GREEN}✓ Container started${NC}"
    fi
    
    # Stop old container
    echo "  Removing old container..."
    if [ -n "$OLD_CONTAINER" ]; then
        docker stop $OLD_CONTAINER 2>/dev/null || true
    fi
    
    # Scale back to 1 (keeps only new container)
    docker compose up -d --no-deps --scale $service=1 $service
    
    echo -e "  ${GREEN}✓ $service deployed successfully${NC}"
    echo ""
}

# Main deployment sequence
echo "Starting deployment at $(date)"
echo ""

# Backend services (with health checks)
deploy_service "app-api" "8001"
deploy_service "studio-api" "8003"
deploy_service "app-voice" "8002"
deploy_service "studio-realtime" "8004"

# Frontend services (no state, faster deployment)
echo -e "${YELLOW}Deploying frontends...${NC}"
docker compose build app-frontend studio-frontend
docker compose up -d --no-deps app-frontend studio-frontend
echo -e "${GREEN}✓ Frontends deployed${NC}"
echo ""

# Verify all services
echo -e "${YELLOW}Verifying deployment...${NC}"
./scripts/health-check.sh

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Deployment Complete!                              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Completed at: $(date)"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Monitor metrics in Grafana"
echo "  2. Check error logs: docker compose logs -f"
echo "  3. Verify user-facing functionality"
echo ""

exit 0

