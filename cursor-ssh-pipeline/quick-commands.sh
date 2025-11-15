#!/bin/bash
# ============================================
# Quick Commands for RunPod Management
# ============================================
# Common operations made simple

ACTION="$1"
SERVICE="${2:-all}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$ACTION" ]; then
    echo "Usage: $0 <action> [service]"
    echo ""
    echo "Actions:"
    echo "  status      - Check service status"
    echo "  logs        - View logs"
    echo "  restart     - Restart services"
    echo "  stop        - Stop services"
    echo "  start       - Start services"
    echo "  health      - Health check"
    echo "  shell       - Open interactive shell"
    echo "  pull        - Pull latest code"
    echo "  deploy      - Quick deploy"
    echo "  tunnel      - Start SSH tunnel"
    echo "  ip          - Get RunPod IP"
    exit 1
fi

echo -e "${BLUE}→ $ACTION${NC}"
echo ""

case "$ACTION" in
    status)
        ssh runpod "cd /nexuslang-v2 && pm2 status"
        ;;
    
    logs)
        if [ "$SERVICE" == "all" ]; then
            ssh runpod "cd /nexuslang-v2 && pm2 logs --lines 50"
        else
            ssh runpod "cd /nexuslang-v2 && pm2 logs $SERVICE --lines 50"
        fi
        ;;
    
    restart)
        ssh runpod "cd /nexuslang-v2 && pm2 restart $SERVICE && pm2 status"
        ;;
    
    stop)
        ssh runpod "cd /nexuslang-v2 && pm2 stop $SERVICE && pm2 status"
        ;;
    
    start)
        ssh runpod "cd /nexuslang-v2 && pm2 start $SERVICE && pm2 status"
        ;;
    
    health)
        echo -e "${YELLOW}Backend Health:${NC}"
        ssh runpod "curl -s http://localhost:8000/health | jq . || curl -s http://localhost:8000/health"
        echo ""
        echo -e "${YELLOW}Nginx Health:${NC}"
        ssh runpod "curl -s http://localhost/health | jq . || curl -s http://localhost/health"
        echo ""
        echo -e "${YELLOW}Ports:${NC}"
        ssh runpod "ss -tlnp | grep -E ':(80|8000|3001|3002|3003) '"
        ;;
    
    shell)
        echo -e "${GREEN}Opening shell in /nexuslang-v2...${NC}"
        echo -e "${YELLOW}Type 'exit' to return${NC}"
        echo ""
        ssh runpod -t "cd /nexuslang-v2 && exec bash"
        ;;
    
    pull)
        ssh runpod "cd /nexuslang-v2 && git pull origin clean-nexuslang && git status"
        ;;
    
    deploy)
        echo -e "${GREEN}Running quick deployment...${NC}"
        "$(dirname "$0")/deploy.sh" all true
        ;;
    
    tunnel)
        echo -e "${GREEN}Starting SSH tunnel...${NC}"
        echo -e "${YELLOW}Services will be available at:${NC}"
        echo "  Backend:  http://localhost:8000"
        echo "  Studio:   http://localhost:3001"
        echo "  DevPlatform: http://localhost:3002"
        echo "  App:      http://localhost:3003"
        echo ""
        echo -e "${YELLOW}Press Ctrl+C to stop tunnel${NC}"
        echo ""
        ssh runpod-tunnel -N
        ;;
    
    ip)
        echo -e "${YELLOW}RunPod IP Address:${NC}"
        ssh runpod "curl -s ifconfig.me"
        echo ""
        ;;
    
    *)
        echo "Unknown action: $ACTION"
        echo "Run '$0' without arguments to see available actions"
        exit 1
        ;;
esac

echo ""

