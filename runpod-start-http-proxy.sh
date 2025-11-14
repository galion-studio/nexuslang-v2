#!/bin/bash
# ============================================================================
# RunPod HTTP Proxy Server Startup Script
# ============================================================================
# This starts the server on port 80 for RunPod's HTTP proxy feature
# Access via: https://[POD_ID].proxy.runpod.net

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}🚀 Starting Nexus Lang V2 Server for RunPod HTTP Proxy${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Configuration
PROJECT_DIR="/workspace/project-nexus"
BACKEND_DIR="$PROJECT_DIR/v2/backend"
LOG_DIR="/workspace/logs"
PORT=80  # RunPod HTTP proxy port

# Create log directory
mkdir -p "$LOG_DIR"

# Kill existing processes
echo -e "${YELLOW}[1/5]${NC} Stopping any existing servers..."
pkill -f "uvicorn.*:80" || true
pkill -f "uvicorn.*:8080" || true
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

# Start server on port 80 for HTTP proxy
echo -e "${YELLOW}[4/5]${NC} Starting server on port $PORT..."
nohup python -m uvicorn main_simple:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level info \
    --access-log \
    --proxy-headers \
    > "$LOG_DIR/galion-http-proxy.log" 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > "$LOG_DIR/server-http-proxy.pid"
sleep 3

# Verify
echo -e "${YELLOW}[5/5]${NC} Verifying server..."
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✅ Server is running (PID: $SERVER_PID)${NC}"
else
    echo -e "${RED}❌ Server failed to start. Check logs:${NC}"
    tail -20 "$LOG_DIR/galion-http-proxy.log"
    exit 1
fi

# Test health endpoint
if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Health check pending... (server may still be starting)${NC}"
fi

# Get RunPod information
POD_ID=$(echo $RUNPOD_POD_ID || echo "YOUR_POD_ID")
PUBLIC_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "unknown")

# Success message
echo ""
echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}✅ Server Started Successfully for RunPod HTTP Proxy!${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo "🔗 Access URLs:"
echo "  • Local:          http://localhost:$PORT"
echo "  • RunPod Proxy:   https://$POD_ID.proxy.runpod.net"
echo "  • Direct IP:      http://$PUBLIC_IP:$PORT (if port exposed)"
echo "  • Health:         https://$POD_ID.proxy.runpod.net/health"
echo "  • API Docs:       https://$POD_ID.proxy.runpod.net/docs"
echo ""
echo "📊 Monitoring:"
echo "  • View logs:      tail -f $LOG_DIR/galion-http-proxy.log"
echo "  • Check health:   curl http://localhost:$PORT/health"
echo "  • Stop server:    kill $SERVER_PID"
echo ""
echo "⚠️  Note: Replace 'YOUR_POD_ID' with your actual RunPod pod ID"
echo "   You can find your pod ID in the RunPod dashboard URL"
echo ""
echo "🔧 To find your Pod ID:"
echo "   1. Go to RunPod dashboard"
echo "   2. Select your pod"
echo "   3. Copy the pod ID from the URL or pod details"
echo ""

echo -e "${BLUE}============================================================================${NC}"
