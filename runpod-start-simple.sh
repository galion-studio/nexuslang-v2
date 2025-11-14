#!/bin/bash
# ============================================================================
# RunPod Simple Server Startup Script
# ============================================================================
# This script starts the SIMPLIFIED web server that is more reliable
# Use this if the regular server has import issues

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}🚀 Starting Simplified Nexus Lang V2 Server${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Configuration
PROJECT_DIR="/workspace/project-nexus"
BACKEND_DIR="$PROJECT_DIR/v2/backend"
LOG_DIR="/workspace/logs"
PORT=8080

# Create log directory
mkdir -p "$LOG_DIR"

# Kill existing processes
echo -e "${YELLOW}[1/5]${NC} Stopping any existing servers..."
pkill -f "uvicorn.*8080" || true
sleep 2

# Set environment
echo -e "${YELLOW}[2/5]${NC} Setting up environment..."
cd "$BACKEND_DIR"
export PYTHONPATH="$PROJECT_DIR:$PROJECT_DIR/v2"
export PORT=$PORT
export HOST="0.0.0.0"
export WORKERS=2

# Install minimal dependencies
echo -e "${YELLOW}[3/5]${NC} Installing dependencies..."
pip install -q fastapi uvicorn psutil

# Start server using simplified main
echo -e "${YELLOW}[4/5]${NC} Starting server..."
nohup python -m uvicorn main_simple:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 2 \
    > "$LOG_DIR/galion-simple.log" 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > "$LOG_DIR/server-simple.pid"
sleep 3

# Verify
echo -e "${YELLOW}[5/5]${NC} Verifying server..."
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✅ Server is running (PID: $SERVER_PID)${NC}"
else
    echo -e "❌ Server failed to start. Check logs:"
    tail -20 "$LOG_DIR/galion-simple.log"
    exit 1
fi

# Test health endpoint
if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Health check pending... (server may still be starting)${NC}"
fi

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me || echo "Unable to determine")

# Success message
echo ""
echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}✅ Server Started Successfully!${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo "📍 Access URLs:"
echo "  • Local:     http://localhost:$PORT"
echo "  • Public IP: http://$PUBLIC_IP:$PORT"
echo "  • Health:    http://$PUBLIC_IP:$PORT/health"
echo "  • Docs:      http://$PUBLIC_IP:$PORT/docs"
echo ""
echo "📊 Monitoring:"
echo "  • View logs:   tail -f $LOG_DIR/galion-simple.log"
echo "  • Check health: curl http://localhost:$PORT/health"
echo "  • Stop server:  kill $SERVER_PID"
echo ""
echo "☁️  For Cloudflare, point DNS A record to: $PUBLIC_IP"
echo ""

