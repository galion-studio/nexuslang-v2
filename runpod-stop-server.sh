#!/bin/bash
# ============================================================================
# Galion Studio - RunPod Server Stop Script
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🛑 Stopping Galion Studio Backend Server..."

LOG_DIR="/workspace/logs"
PID_FILE="$LOG_DIR/server.pid"

# Stop by PID file
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo -e "${YELLOW}[INFO]${NC} Found server PID: $PID"
    
    if ps -p $PID > /dev/null; then
        kill $PID
        echo -e "${GREEN}[SUCCESS]${NC} Server stopped (PID: $PID)"
        rm "$PID_FILE"
    else
        echo -e "${YELLOW}[WARNING]${NC} Server process not found"
        rm "$PID_FILE"
    fi
fi

# Kill any remaining uvicorn processes
echo -e "${YELLOW}[INFO]${NC} Checking for remaining uvicorn processes..."
pkill -f "uvicorn.*main:app" || echo -e "${YELLOW}[INFO]${NC} No uvicorn processes found"

echo -e "${GREEN}[SUCCESS]${NC} Server stopped successfully"

