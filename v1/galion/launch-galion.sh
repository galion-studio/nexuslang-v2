#!/bin/bash
# GALION.APP - Master Launch Script (Linux/Mac)
# Launches all services in the correct order

set -e

echo "================================"
echo "   GALION.APP - LAUNCH SYSTEM   "
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Check if Docker is running
echo -e "${YELLOW}[1/6] Checking Docker...${NC}"
if docker version > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${RED}✗ Docker is not running!${NC}"
    echo -e "${YELLOW}Please start Docker and try again.${NC}"
    exit 1
fi

# Check if ports are available
echo ""
echo -e "${YELLOW}[2/6] Checking ports...${NC}"
ports=(3000 8000 8001 8003 8004 8005 8080 9090)
ports_in_use=()

for port in "${ports[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        ports_in_use+=($port)
    fi
done

if [ ${#ports_in_use[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠ Warning: The following ports are already in use: ${ports_in_use[*]}${NC}"
    echo -e "${YELLOW}Services using these ports may fail to start.${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ All required ports are available${NC}"
fi

# Start backend services
echo ""
echo -e "${YELLOW}[3/6] Starting backend services...${NC}"
docker-compose up -d

sleep 5

# Check backend health
echo ""
echo -e "${YELLOW}[4/6] Checking backend health...${NC}"
max_retries=30
retry_count=0
backend_healthy=false

while [ $retry_count -lt $max_retries ] && [ "$backend_healthy" = false ]; do
    if curl -s -f http://localhost:8080/health > /dev/null 2>&1; then
        backend_healthy=true
        echo -e "${GREEN}✓ Backend services are healthy${NC}"
    else
        ((retry_count++))
        echo -e "${YELLOW}Waiting for backend... ($retry_count/$max_retries)${NC}"
        sleep 2
    fi
done

if [ "$backend_healthy" = false ]; then
    echo -e "${RED}✗ Backend services failed to start!${NC}"
    echo -e "${YELLOW}Check logs with: docker-compose logs${NC}"
    exit 1
fi

# Install frontend dependencies if needed
echo ""
echo -e "${YELLOW}[5/6] Preparing frontend...${NC}"
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi

# Start frontend
echo ""
echo -e "${YELLOW}[6/6] Starting frontend...${NC}"
cd frontend

# Start frontend in background
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# Wait for frontend to start
echo -e "${YELLOW}Waiting for frontend to start...${NC}"
sleep 10

frontend_healthy=false
retry_count=0

while [ $retry_count -lt 30 ] && [ "$frontend_healthy" = false ]; do
    if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
        frontend_healthy=true
    else
        ((retry_count++))
        sleep 2
    fi
done

# Show status
echo ""
echo "================================"
echo "   LAUNCH COMPLETE!   "
echo "================================"
echo ""

echo -e "${NC}Services Status:${NC}"
echo ""

# Check each service
declare -A services=(
    ["Frontend"]="http://localhost:3000:3000"
    ["API Gateway"]="http://localhost:8080/health:8080"
    ["Auth Service"]="http://localhost:8000/health:8000"
    ["User Service"]="http://localhost:8001/health:8001"
    ["Voice Service"]="http://localhost:8003/health:8003"
    ["Document Service"]="http://localhost:8004/health:8004"
    ["Permissions Service"]="http://localhost:8005/health:8005"
)

for service in "${!services[@]}"; do
    IFS=':' read -r url port <<< "${services[$service]}"
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $service (port $port)${NC}"
    else
        echo -e "${RED}✗ $service (port $port)${NC}"
    fi
done

echo ""
echo -e "${NC}Access Points:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  Frontend:      http://localhost:3000${NC}"
echo -e "${CYAN}  API Gateway:   http://localhost:8080${NC}"
echo -e "${CYAN}  API Docs:      http://localhost:3000/docs${NC}"
echo -e "${CYAN}  Status Page:   http://localhost:3000/status${NC}"
echo -e "${CYAN}  Analytics:     http://localhost:3000/analytics${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${NC}Quick Actions:${NC}"
echo -e "${GRAY}  • Register:    http://localhost:3000/register${NC}"
echo -e "${GRAY}  • Login:       http://localhost:3000/login${NC}"
echo -e "${GRAY}  • Dashboard:   http://localhost:3000/dashboard${NC}"
echo ""

echo -e "${NC}Useful Commands:${NC}"
echo -e "${GRAY}  View Logs:     docker-compose logs -f${NC}"
echo -e "${GRAY}  Stop All:      docker-compose down${NC}"
echo -e "${GRAY}  Restart:       docker-compose restart${NC}"
echo -e "${GRAY}  Status:        docker-compose ps${NC}"
echo ""

echo -e "${YELLOW}Opening browser...${NC}"
sleep 2

# Open browser (cross-platform)
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:3000
elif command -v open > /dev/null; then
    open http://localhost:3000
fi

echo ""
echo -e "${GREEN}🚀 GALION.APP IS LIVE! 🚀${NC}"
echo ""
echo -e "${GRAY}Press Ctrl+C to stop monitoring (services will continue running)${NC}"
echo ""

# Monitor services
trap 'echo ""; echo "Monitoring stopped. Services are still running."; echo "To stop all services: docker-compose down"; exit 0' INT

while true; do
    sleep 5
    
    # Quick health check
    health_status=""
    for service in "${!services[@]}"; do
        IFS=':' read -r url port <<< "${services[$service]}"
        if curl -s -f "$url" > /dev/null 2>&1; then
            health_status+="✓ "
        else
            health_status+="✗ "
        fi
    done
    
    echo -ne "\r$(date '+%H:%M:%S') Health: $health_status"
done

