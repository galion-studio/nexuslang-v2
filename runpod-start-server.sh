#!/bin/bash
# ============================================================================
# Galion Studio - RunPod Server Startup Script
# ============================================================================
# This script starts the Galion backend server on RunPod
# Compatible with Cloudflare (uses port 8080)

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

# Print banner
echo "============================================================================"
echo "🚀 Galion Studio Backend Server - RunPod Deployment"
echo "============================================================================"
echo ""

# Configuration
PROJECT_DIR="/workspace/project-nexus"
BACKEND_DIR="$PROJECT_DIR/v2/backend"
LOG_DIR="/workspace/logs"
PORT=8080
HOST="0.0.0.0"
WORKERS=2

# Create log directory
mkdir -p "$LOG_DIR"

# Step 1: Check if project exists
log_info "Checking project directory..."
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "Project directory not found: $PROJECT_DIR"
    log_info "Please ensure your code is uploaded to RunPod"
    exit 1
fi
log_success "Project directory found"

# Step 2: Check backend directory
log_info "Checking backend directory..."
if [ ! -d "$BACKEND_DIR" ]; then
    log_error "Backend directory not found: $BACKEND_DIR"
    exit 1
fi
log_success "Backend directory found"

# Step 3: Set environment variables
log_info "Setting environment variables..."
export PYTHONPATH="$PROJECT_DIR:$PROJECT_DIR/v2"
export PORT=$PORT
export HOST=$HOST
export LOG_LEVEL="INFO"

log_success "Environment configured"
log_info "  PYTHONPATH: $PYTHONPATH"
log_info "  PORT: $PORT"
log_info "  HOST: $HOST"

# Step 4: Install dependencies
log_info "Installing Python dependencies..."
cd "$PROJECT_DIR"

if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    log_success "Dependencies installed"
else
    log_warning "No requirements.txt found, skipping dependency installation"
fi

# Step 5: Check if port is already in use
log_info "Checking if port $PORT is available..."
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    log_warning "Port $PORT is already in use. Attempting to kill existing process..."
    pkill -f "uvicorn.*$PORT" || true
    sleep 2
    
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        log_error "Could not free port $PORT. Please check manually:"
        lsof -i :$PORT
        exit 1
    fi
    log_success "Port $PORT is now available"
else
    log_success "Port $PORT is available"
fi

# Step 6: Test import
log_info "Testing Python imports..."
cd "$BACKEND_DIR"
python -c "from main_simple import app; print('✅ Import successful')" 2>&1 | tee -a "$LOG_DIR/startup.log"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    log_error "Import test failed. Check logs:"
    tail -20 "$LOG_DIR/startup.log"
    exit 1
fi

# Step 7: Start the server
log_info "Starting Galion backend server..."
echo ""
echo "============================================================================"
echo "🎯 Server Configuration"
echo "============================================================================"
echo "  Port: $PORT"
echo "  Host: $HOST"
echo "  Workers: $WORKERS"
echo "  Backend Dir: $BACKEND_DIR"
echo "  Log File: $LOG_DIR/galion-backend.log"
echo "============================================================================"
echo ""

# Start server in background
nohup python -m uvicorn main_simple:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level info \
    > "$LOG_DIR/galion-backend.log" 2>&1 &

SERVER_PID=$!

# Wait a moment for server to start
sleep 3

# Step 8: Verify server is running
log_info "Verifying server startup..."

if ps -p $SERVER_PID > /dev/null; then
    log_success "Server process is running (PID: $SERVER_PID)"
else
    log_error "Server process failed to start"
    log_error "Check logs: tail -f $LOG_DIR/galion-backend.log"
    exit 1
fi

# Test health endpoint
log_info "Testing health endpoint..."
sleep 2

if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    log_success "Health check passed!"
else
    log_warning "Health check failed. Server may still be starting up..."
    log_info "Check logs: tail -f $LOG_DIR/galion-backend.log"
fi

# Step 9: Get public IP
log_info "Getting public IP address..."
PUBLIC_IP=$(curl -s ifconfig.me || echo "Unable to determine")

# Step 10: Display success information
echo ""
echo "============================================================================"
echo "✅ Galion Studio Backend Server Started Successfully!"
echo "============================================================================"
echo ""
echo "📍 Server Access Points:"
echo "  - Local:     http://localhost:$PORT"
echo "  - Public IP: http://$PUBLIC_IP:$PORT"
echo "  - Domain:    https://galion.studio (after Cloudflare config)"
echo ""
echo "🔍 API Endpoints:"
echo "  - Root:      http://$PUBLIC_IP:$PORT/"
echo "  - Health:    http://$PUBLIC_IP:$PORT/health"
echo "  - Docs:      http://$PUBLIC_IP:$PORT/docs"
echo ""
echo "📊 Monitoring:"
echo "  - View logs:   tail -f $LOG_DIR/galion-backend.log"
echo "  - Check status: curl http://localhost:$PORT/health"
echo "  - Process ID:   $SERVER_PID"
echo ""
echo "🔧 Management Commands:"
echo "  - Stop server:  kill $SERVER_PID"
echo "  - Restart:      $0"
echo ""
echo "☁️  Cloudflare Configuration:"
echo "  1. Go to Cloudflare Dashboard → galion.studio → DNS"
echo "  2. Add A record: @ → $PUBLIC_IP (Proxy ON)"
echo "  3. SSL/TLS → Set to 'Flexible' or 'Full'"
echo "  4. Wait 1-2 minutes for DNS propagation"
echo "  5. Test: https://galion.studio/health"
echo ""
echo "============================================================================"
echo ""

# Save PID to file
echo $SERVER_PID > "$LOG_DIR/server.pid"

log_success "Server is ready! 🚀"
log_info "Logs are being written to: $LOG_DIR/galion-backend.log"

