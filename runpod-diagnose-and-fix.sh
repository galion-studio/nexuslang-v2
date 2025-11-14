#!/bin/bash
# ============================================================================
# RunPod Web Server Diagnostic & Fix Script
# ============================================================================
# This script diagnoses and fixes common web server issues on RunPod
# Run this on your RunPod instance to identify and fix problems

set +e  # Don't exit on errors, we want to see all diagnostics

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

log_section() {
    echo ""
    echo "============================================================================"
    echo "$1"
    echo "============================================================================"
    echo ""
}

# Print banner
log_section "🔍 RunPod Web Server Diagnostic & Fix Tool"

# Configuration
PROJECT_DIR="/workspace/project-nexus"
BACKEND_DIR="$PROJECT_DIR/v2/backend"
LOG_DIR="/workspace/logs"
PORT=8080

# ============================================================================
# STEP 1: Environment Check
# ============================================================================
log_section "STEP 1: Checking Environment"

log_info "Current directory: $(pwd)"
log_info "Current user: $(whoami)"
log_info "Python version: $(python --version 2>&1)"
log_info "Pip version: $(pip --version 2>&1)"

# Check if project directory exists
if [ -d "$PROJECT_DIR" ]; then
    log_success "Project directory found: $PROJECT_DIR"
else
    log_error "Project directory NOT found: $PROJECT_DIR"
    log_info "Your code needs to be uploaded to RunPod"
    exit 1
fi

# Check backend directory
if [ -d "$BACKEND_DIR" ]; then
    log_success "Backend directory found: $BACKEND_DIR"
else
    log_error "Backend directory NOT found: $BACKEND_DIR"
    exit 1
fi

# ============================================================================
# STEP 2: Check Running Processes
# ============================================================================
log_section "STEP 2: Checking Running Processes"

log_info "Checking for existing uvicorn processes..."
UVICORN_PROCS=$(ps aux | grep uvicorn | grep -v grep)
if [ -n "$UVICORN_PROCS" ]; then
    log_warning "Found running uvicorn processes:"
    echo "$UVICORN_PROCS"
    log_info "Killing existing processes..."
    pkill -f uvicorn || true
    sleep 2
    log_success "Old processes terminated"
else
    log_info "No existing uvicorn processes found"
fi

# Check port usage
log_info "Checking port $PORT..."
PORT_USAGE=$(lsof -i :$PORT 2>/dev/null)
if [ -n "$PORT_USAGE" ]; then
    log_warning "Port $PORT is in use:"
    echo "$PORT_USAGE"
    log_info "Killing process on port $PORT..."
    fuser -k $PORT/tcp || true
    sleep 2
else
    log_success "Port $PORT is available"
fi

# ============================================================================
# STEP 3: Check Dependencies
# ============================================================================
log_section "STEP 3: Checking Python Dependencies"

cd "$PROJECT_DIR"

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    log_success "requirements.txt found"
    
    log_info "Checking key dependencies..."
    
    # Check FastAPI
    if python -c "import fastapi" 2>/dev/null; then
        log_success "FastAPI: Installed"
    else
        log_error "FastAPI: NOT installed"
        log_info "Installing FastAPI..."
        pip install fastapi uvicorn -q
    fi
    
    # Check uvicorn
    if python -c "import uvicorn" 2>/dev/null; then
        log_success "Uvicorn: Installed"
    else
        log_error "Uvicorn: NOT installed"
        log_info "Installing Uvicorn..."
        pip install uvicorn -q
    fi
    
    # Check psutil
    if python -c "import psutil" 2>/dev/null; then
        log_success "psutil: Installed"
    else
        log_warning "psutil: NOT installed"
        log_info "Installing psutil..."
        pip install psutil -q
    fi
    
    log_info "Installing all requirements..."
    pip install -q -r requirements.txt 2>&1 | tail -10
    
else
    log_warning "requirements.txt NOT found"
    log_info "Installing minimal dependencies..."
    pip install -q fastapi uvicorn psutil
fi

# ============================================================================
# STEP 4: Test Python Imports
# ============================================================================
log_section "STEP 4: Testing Python Imports"

# Set PYTHONPATH for proper module resolution
export PYTHONPATH="$PROJECT_DIR:$PROJECT_DIR/v2:$BACKEND_DIR"
log_info "PYTHONPATH set to: $PYTHONPATH"

# Test basic imports
log_info "Testing FastAPI import..."
if python -c "from fastapi import FastAPI" 2>/dev/null; then
    log_success "FastAPI import successful"
else
    log_error "FastAPI import failed"
fi

# Test main.py import from backend directory
log_info "Testing main.py import..."
cd "$BACKEND_DIR"
IMPORT_TEST=$(python -c "from main import app; print('OK')" 2>&1)
if echo "$IMPORT_TEST" | grep -q "OK"; then
    log_success "main.py imports successful"
else
    log_error "main.py imports failed:"
    echo "$IMPORT_TEST"
    log_warning "Server may have degraded functionality but can still start"
fi

# ============================================================================
# STEP 5: Check Logs
# ============================================================================
log_section "STEP 5: Checking Existing Logs"

mkdir -p "$LOG_DIR"

if [ -f "$LOG_DIR/galion-backend.log" ]; then
    log_info "Found existing log file. Last 20 lines:"
    tail -20 "$LOG_DIR/galion-backend.log"
else
    log_info "No existing log file found (this is normal for first run)"
fi

# ============================================================================
# STEP 6: Start Server
# ============================================================================
log_section "STEP 6: Starting Web Server"

# Set PYTHONPATH for absolute imports (main.py now uses absolute imports)
export PYTHONPATH="$PROJECT_DIR:$PROJECT_DIR/v2:$BACKEND_DIR"

log_info "Server configuration:"
log_info "  - Host: 0.0.0.0"
log_info "  - Port: $PORT"
log_info "  - Workers: 2"
log_info "  - Backend Dir: $BACKEND_DIR"
log_info "  - Log File: $LOG_DIR/galion-backend.log"
log_info "  - PYTHONPATH: $PYTHONPATH"

# Start server from backend directory with absolute imports
log_info "Starting server in background..."
cd "$BACKEND_DIR"
nohup python -m uvicorn main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 2 \
    --log-level info \
    > "$LOG_DIR/galion-backend.log" 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > "$LOG_DIR/server.pid"

log_info "Server process started (PID: $SERVER_PID)"
log_info "Waiting for server to initialize (5 seconds)..."
sleep 5

# ============================================================================
# STEP 7: Verify Server is Running
# ============================================================================
log_section "STEP 7: Verifying Server Status"

# Check if process is still running
if ps -p $SERVER_PID > /dev/null 2>&1; then
    log_success "Server process is running (PID: $SERVER_PID)"
else
    log_error "Server process died. Check logs:"
    tail -30 "$LOG_DIR/galion-backend.log"
    exit 1
fi

# Test health endpoint
log_info "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:$PORT/health 2>&1)
if echo "$HEALTH_RESPONSE" | grep -q "healthy\|status"; then
    log_success "Health check passed!"
    echo "$HEALTH_RESPONSE" | python -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    log_warning "Health check failed or incomplete response"
    echo "Response: $HEALTH_RESPONSE"
    log_info "Server may still be initializing. Check logs:"
    tail -20 "$LOG_DIR/galion-backend.log"
fi

# Test root endpoint
log_info "Testing root endpoint..."
ROOT_RESPONSE=$(curl -s http://localhost:$PORT/ 2>&1)
if echo "$ROOT_RESPONSE" | grep -q "Nexus\|message\|version"; then
    log_success "Root endpoint working!"
else
    log_warning "Root endpoint returned unexpected response"
fi

# ============================================================================
# STEP 8: Network Information
# ============================================================================
log_section "STEP 8: Network Information"

# Get public IP
log_info "Getting public IP address..."
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "Unable to determine")
log_info "Public IP: $PUBLIC_IP"

# Check if port is accessible
log_info "Checking if port is listening..."
LISTENING=$(netstat -tuln 2>/dev/null | grep ":$PORT " || ss -tuln 2>/dev/null | grep ":$PORT ")
if [ -n "$LISTENING" ]; then
    log_success "Port $PORT is listening"
    echo "$LISTENING"
else
    log_warning "Port $PORT may not be listening properly"
fi

# ============================================================================
# STEP 9: Final Status Report
# ============================================================================
log_section "✅ DIAGNOSTIC COMPLETE - SUMMARY"

echo "📋 Server Status:"
echo "  - Process ID: $SERVER_PID"
echo "  - Port: $PORT"
echo "  - Log File: $LOG_DIR/galion-backend.log"
echo ""
echo "🌐 Access URLs:"
echo "  - Local:     http://localhost:$PORT"
echo "  - Public IP: http://$PUBLIC_IP:$PORT"
echo "  - Health:    http://$PUBLIC_IP:$PORT/health"
echo "  - Docs:      http://$PUBLIC_IP:$PORT/docs"
echo ""
echo "☁️  Cloudflare Configuration:"
echo "  1. Go to Cloudflare Dashboard → galion.studio → DNS"
echo "  2. Add A record: @ → $PUBLIC_IP (Proxy ON)"
echo "  3. Add A record: www → $PUBLIC_IP (Proxy ON)"
echo "  4. SSL/TLS → Set to 'Flexible' or 'Full'"
echo "  5. Wait 1-2 minutes, then test: https://galion.studio/health"
echo ""
echo "📊 Monitoring Commands:"
echo "  - View logs:      tail -f $LOG_DIR/galion-backend.log"
echo "  - Check health:   curl http://localhost:$PORT/health"
echo "  - Check process:  ps aux | grep $SERVER_PID"
echo "  - Stop server:    kill $SERVER_PID"
echo ""
echo "🔍 Troubleshooting:"
if ps -p $SERVER_PID > /dev/null 2>&1; then
    log_success "✅ Server is RUNNING"
else
    log_error "❌ Server is NOT running - check logs above"
fi

echo ""
log_info "Showing last 30 lines of log:"
tail -30 "$LOG_DIR/galion-backend.log"

log_section "🎉 Setup Complete!"

