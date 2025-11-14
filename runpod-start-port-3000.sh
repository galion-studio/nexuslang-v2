#!/bin/bash
# ============================================================================
# RunPod Server Startup Script for Port 3000
# ============================================================================
# Uses port 3000 to avoid nginx conflicts

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}🚀 Starting Nexus Lang V2 Server on Port 3000${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Configuration
PROJECT_DIR="/workspace/project-nexus"
BACKEND_DIR="$PROJECT_DIR/v2/backend"
LOG_DIR="/workspace/logs"
PORT=3000  # Using port 3000 to avoid nginx conflicts

# Create log directory
mkdir -p "$LOG_DIR"

# Kill existing processes
echo -e "${YELLOW}[1/5]${NC} Stopping any existing servers..."
pkill -f "uvicorn.*:80" || true
pkill -f "uvicorn.*:8080" || true
pkill -f "uvicorn.*:3000" || true
sleep 2

# Set environment
echo -e "${YELLOW}[2/5]${NC} Setting up environment..."
cd "$BACKEND_DIR"
export PYTHONPATH="$PROJECT_DIR:$PROJECT_DIR/v2"
export PORT=$PORT
export HOST="0.0.0.0"
export WORKERS=1

# Install minimal dependencies
echo -e "${YELLOW}[3/5]${NC} Installing dependencies..."
pip install -q fastapi uvicorn psutil

# Start server on port 3000
echo -e "${YELLOW}[4/5]${NC} Starting server on port $PORT..."
nohup python -m uvicorn main_simple:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level info \
    --access-log \
    --proxy-headers \
    > "$LOG_DIR/galion-port-3000.log" 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > "$LOG_DIR/server-port-3000.pid"
sleep 3

# Verify
echo -e "${YELLOW}[5/5]${NC} Verifying server..."
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✅ Server is running (PID: $SERVER_PID)${NC}"
else
    echo -e "${RED}❌ Server failed to start. Check logs:${NC}"
    tail -20 "$LOG_DIR/galion-port-3000.log"
    exit 1
fi

# Test health endpoint
if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Health check pending... (server may still be starting)${NC}"
fi

# Get RunPod information
POD_ID=$(echo $RUNPOD_POD_ID || echo "a51059ucg22sxt")
PUBLIC_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "213.173.105.83")

# Success message
echo ""
echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}✅ Server Started Successfully on Port 3000!${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo "🔗 Access URLs:"
echo "  • Local:          http://localhost:$PORT"
echo "  • Direct IP:      http://$PUBLIC_IP:$PORT"
echo "  • Health:         http://$PUBLIC_IP:$PORT/health"
echo "  • API Docs:       http://$PUBLIC_IP:$PORT/docs"
echo ""
echo "⚠️  Note: Port 3000 may not work with RunPod proxy"
echo "   Try accessing via direct IP first"
echo ""
echo "📊 Monitoring:"
echo "  • View logs:      tail -f $LOG_DIR/galion-port-3000.log"
echo "  • Check health:   curl http://localhost:$PORT/health"
echo "  • Stop server:    kill $SERVER_PID"
echo ""
echo "🧪 Test Commands:"
echo "  curl http://$PUBLIC_IP:$PORT/health"
echo "  curl http://$PUBLIC_IP:$PORT/"
echo ""

echo -e "${BLUE}============================================================================${NC}"
