#!/bin/bash
# ============================================================================
# Galion Studio - RunPod Restart Helper Script
# ============================================================================
# This script diagnoses and restarts the Galion backend server on RunPod

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "============================================================================"
echo "🔧 Galion Studio - RunPod Server Restart Helper"
echo "============================================================================"
echo ""

# Configuration
PROJECT_DIR="/workspace/project-nexus"
BACKEND_DIR="$PROJECT_DIR/v2/backend"
LOG_DIR="/workspace/logs"
PORT=8080

# Step 1: Check current status
echo "🔍 Current Server Status:"
echo "=========================="

log_info "Checking for running uvicorn processes..."
if ps aux | grep -q "[u]vicorn.*main:app"; then
    log_warning "Found running uvicorn processes:"
    ps aux | grep "[u]vicorn.*main:app"
else
    log_info "No uvicorn processes currently running"
fi

log_info "Checking port $PORT..."
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warning "Port $PORT is in use:"
    lsof -i :$PORT
else
    log_info "Port $PORT is available"
fi

log_info "Testing health endpoint..."
if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    log_success "Health check passed!"
else
    log_warning "Health check failed"
fi

echo ""

# Step 2: Stop existing processes
echo "🛑 Stopping Existing Processes:"
echo "==============================="

log_info "Stopping any existing server processes..."
if [ -f "$LOG_DIR/server.pid" ]; then
    PID=$(cat "$LOG_DIR/server.pid")
    if ps -p $PID > /dev/null; then
        kill $PID 2>/dev/null || true
        log_success "Killed server process (PID: $PID)"
    else
        log_warning "PID file exists but process not found"
    fi
    rm -f "$LOG_DIR/server.pid"
fi

log_info "Killing any remaining uvicorn processes..."
pkill -f "uvicorn.*main:app" 2>/dev/null || log_info "No uvicorn processes to kill"

log_info "Waiting for processes to stop..."
sleep 2

echo ""

# Step 3: Start fresh server
echo "🚀 Starting Fresh Server:"
echo "========================="

log_info "Setting environment variables..."
export PYTHONPATH="$PROJECT_DIR:$PROJECT_DIR/v2"
export PORT=$PORT

log_info "Installing/updating dependencies..."
cd "$PROJECT_DIR"
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    log_success "Dependencies installed"
fi

log_info "Testing Python imports..."
cd "$BACKEND_DIR"
if python -c "from main import app; print('✅ Import successful')" 2>&1; then
    log_success "Import test passed"
else
    log_error "Import test failed. Check the logs above."
    exit 1
fi

log_info "Starting server on port $PORT..."
mkdir -p "$LOG_DIR"

# Start server in background
nohup python -m uvicorn main:app \
    --host "0.0.0.0" \
    --port "$PORT" \
    --workers 2 \
    --log-level info \
    > "$LOG_DIR/galion-backend.log" 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > "$LOG_DIR/server.pid"

log_info "Waiting for server to start..."
sleep 5

# Step 4: Verify startup
echo ""
echo "✅ Verification:"
echo "================"

if ps -p $SERVER_PID > /dev/null; then
    log_success "Server process is running (PID: $SERVER_PID)"
else
    log_error "Server process failed to start"
    log_info "Check logs: tail -f $LOG_DIR/galion-backend.log"
    exit 1
fi

log_info "Testing health endpoint..."
if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    log_success "Health check passed!"
else
    log_warning "Health check failed - server may still be starting"
fi

# Get public IP
log_info "Getting public IP address..."
PUBLIC_IP=$(curl -s ifconfig.me || echo "Unable to determine")

echo ""
echo "============================================================================"
echo "🎉 Galion Studio Server Restart Complete!"
echo "============================================================================"
echo ""
echo "📍 Server Access Points:"
echo "  - Local:     http://localhost:$PORT"
echo "  - Public IP: http://$PUBLIC_IP:$PORT"
echo "  - Domain:    https://galion.studio (after Cloudflare config)"
echo ""
echo "🔍 API Endpoints:"
echo "  - Health:    http://$PUBLIC_IP:$PORT/health"
echo "  - Docs:      http://$PUBLIC_IP:$PORT/docs"
echo ""
echo "📊 Monitoring:"
echo "  - View logs:   tail -f $LOG_DIR/galion-backend.log"
echo "  - Check status: curl http://localhost:$PORT/health"
echo ""
echo "☁️  Cloudflare DNS Update (if needed):"
echo "  Current IP: $PUBLIC_IP"
echo "  Go to Cloudflare Dashboard → galion.studio → DNS"
echo "  Update A record @ → $PUBLIC_IP (Proxy ON)"
echo ""
echo "============================================================================"

log_success "Restart completed successfully! 🚀"
