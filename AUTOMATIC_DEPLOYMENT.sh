#!/bin/bash
# ============================================================================
# GALION.STUDIO AUTOMATIC DEPLOYMENT SCRIPT
# ============================================================================
# This script automatically deploys the complete Galion Platform on RunPod
# Run this ONCE in your RunPod terminal to deploy everything

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

log_header() {
    echo -e "${CYAN}================================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}================================================================================${NC}"
}

# Configuration
PROJECT_DIR="/workspace/project-nexus"
BACKEND_DIR="$PROJECT_DIR/v2/backend"
GALION_APP_DIR="$PROJECT_DIR/galion-app"
DEVELOPER_PLATFORM_DIR="$PROJECT_DIR/developer-platform"
GALION_STUDIO_DIR="$PROJECT_DIR/galion-studio"
LOG_DIR="/workspace/logs"

BACKEND_PORT=8080
GALION_APP_PORT=3010
DEVELOPER_PLATFORM_PORT=3020
GALION_STUDIO_PORT=3030

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed or not in PATH"
        return 1
    fi
    return 0
}

wait_for_service() {
    local url="$1"
    local timeout="${2:-30}"
    local interval="${3:-2}"

    log_info "Waiting for service at $url (timeout: ${timeout}s)"

    local count=0
    while [ $count -lt $timeout ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            log_success "Service is ready!"
            return 0
        fi
        sleep $interval
        count=$((count + interval))
        echo -n "."
    done

    echo ""
    log_error "Service failed to respond within ${timeout} seconds"
    return 1
}

kill_process_on_port() {
    local port="$1"
    local process_name="$2"

    log_info "Checking for processes on port $port..."
    if lsof -ti:$port > /dev/null 2>&1; then
        log_warning "Found process on port $port, terminating..."
        kill -9 $(lsof -ti:$port) 2>/dev/null || true
        sleep 2
    fi
}

cleanup_processes() {
    log_info "Cleaning up existing processes..."

    # Kill any existing processes
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "next.*dev" 2>/dev/null || true
    pkill -f "npm.*run.*dev" 2>/dev/null || true

    # Kill processes on specific ports
    kill_process_on_port $BACKEND_PORT "backend"
    kill_process_on_port $GALION_APP_PORT "galion-app"
    kill_process_on_port $DEVELOPER_PLATFORM_PORT "developer-platform"
    kill_process_on_port $GALION_STUDIO_PORT "galion-studio"

    sleep 3
    log_success "Cleanup complete"
}

# ============================================================================
# DEPLOYMENT FUNCTIONS
# ============================================================================

deploy_backend() {
    log_header "DEPLOYING BACKEND (Port $BACKEND_PORT)"

    log_step "1. Setting up environment variables"
    export PYTHONPATH="$PROJECT_DIR:$PROJECT_DIR/v2"
    export PORT=$BACKEND_PORT
    export HOST="0.0.0.0"
    log_success "Environment configured"

    log_step "2. Installing Python dependencies"
    cd "$PROJECT_DIR"
    pip install -q -r requirements.txt
    log_success "Dependencies installed"

    log_step "3. Creating log directory"
    mkdir -p "$LOG_DIR"
    log_success "Log directory created"

    log_step "4. Starting backend server"
    cd "$BACKEND_DIR"
    nohup python -m uvicorn main:app \
        --host "$HOST" \
        --port "$BACKEND_PORT" \
        --workers 2 \
        > "$LOG_DIR/galion-backend.log" 2>&1 &
    local backend_pid=$!

    log_success "Backend server started (PID: $backend_pid)"

    log_step "5. Waiting for backend to be ready"
    wait_for_service "http://localhost:$BACKEND_PORT/health"

    log_step "6. Testing backend health"
    local health_response=$(curl -s "http://localhost:$BACKEND_PORT/health")
    if [[ "$health_response" == *"healthy"* ]]; then
        log_success "Backend health check PASSED"
        echo "Response: $health_response"
    else
        log_error "Backend health check FAILED"
        echo "Response: $health_response"
        return 1
    fi

    log_success "Backend deployment COMPLETE"
    echo ""
}

deploy_galion_app() {
    log_header "DEPLOYING GALION-APP (Port $GALION_APP_PORT)"

    log_step "1. Installing Node.js dependencies"
    cd "$GALION_APP_DIR"
    npm install --silent
    log_success "Dependencies installed"

    log_step "2. Starting Galion App"
    nohup npm run dev > "$LOG_DIR/galion-app.log" 2>&1 &
    local app_pid=$!

    log_success "Galion App started (PID: $app_pid)"

    log_step "3. Waiting for Galion App to be ready"
    wait_for_service "http://localhost:$GALION_APP_PORT"

    log_success "Galion App deployment COMPLETE (http://localhost:$GALION_APP_PORT)"
    echo ""
}

deploy_developer_platform() {
    log_header "DEPLOYING DEVELOPER-PLATFORM (Port $DEVELOPER_PLATFORM_PORT)"

    log_step "1. Installing Node.js dependencies"
    cd "$DEVELOPER_PLATFORM_DIR"
    npm install --silent
    log_success "Dependencies installed"

    log_step "2. Starting Developer Platform"
    nohup npm run dev > "$LOG_DIR/developer-platform.log" 2>&1 &
    local dev_pid=$!

    log_success "Developer Platform started (PID: $dev_pid)"

    log_step "3. Waiting for Developer Platform to be ready"
    wait_for_service "http://localhost:$DEVELOPER_PLATFORM_PORT"

    log_success "Developer Platform deployment COMPLETE (http://localhost:$DEVELOPER_PLATFORM_PORT)"
    echo ""
}

deploy_galion_studio() {
    log_header "DEPLOYING GALION-STUDIO (Port $GALION_STUDIO_PORT)"

    log_step "1. Installing Node.js dependencies"
    cd "$GALION_STUDIO_DIR"
    npm install --silent
    log_success "Dependencies installed"

    log_step "2. Starting Galion Studio"
    nohup npm run dev > "$LOG_DIR/galion-studio.log" 2>&1 &
    local studio_pid=$!

    log_success "Galion Studio started (PID: $studio_pid)"

    log_step "3. Waiting for Galion Studio to be ready"
    wait_for_service "http://localhost:$GALION_STUDIO_PORT"

    log_success "Galion Studio deployment COMPLETE (http://localhost:$GALION_STUDIO_PORT)"
    echo ""
}

get_public_ip() {
    log_info "Getting RunPod public IP..."
    PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "Unable to determine")

    if [[ "$PUBLIC_IP" == "Unable to determine" ]]; then
        log_warning "Could not determine public IP automatically"
        log_info "Please check your RunPod dashboard for the public IP"
        PUBLIC_IP="YOUR_RUNPOD_IP"
    else
        log_success "Public IP: $PUBLIC_IP"
    fi
}

show_final_status() {
    log_header "🎉 DEPLOYMENT COMPLETE - GALION PLATFORM IS LIVE!"

    echo ""
    echo "=================================================================================="
    echo "🚀 GALION PLATFORM - ALL SERVICES RUNNING"
    echo "=================================================================================="
    echo ""
    echo "🌐 PUBLIC ACCESS URLs (using your RunPod IP: $PUBLIC_IP):"
    echo ""
    echo "  📊 Backend API:     http://$PUBLIC_IP:$BACKEND_PORT"
    echo "  🔍 API Health:      http://$PUBLIC_IP:$BACKEND_PORT/health"
    echo "  📚 API Docs:        http://$PUBLIC_IP:$BACKEND_PORT/docs"
    echo ""
    echo "  🎤 Galion App:      http://$PUBLIC_IP:$GALION_APP_PORT"
    echo "  💻 Dev Platform:    http://$PUBLIC_IP:$DEVELOPER_PLATFORM_PORT"
    echo "  🏢 Galion Studio:    http://$PUBLIC_IP:$GALION_STUDIO_PORT"
    echo ""
    echo "=================================================================================="
    echo "🌐 CLOUDFLARE DOMAIN ACCESS (after DNS configuration):"
    echo "=================================================================================="
    echo ""
    echo "  🏢 galion.studio           → Galion Studio (Corporate)"
    echo "  🎤 app.galion.studio       → Galion App (Voice Interface)"
    echo "  💻 developer.galion.studio → Developer Platform (IDE)"
    echo "  📊 api.galion.studio       → Backend API"
    echo ""
    echo "=================================================================================="
    echo "🔧 MONITORING & MANAGEMENT"
    echo "=================================================================================="
    echo ""
    echo "  📝 View Logs:"
    echo "    tail -f $LOG_DIR/galion-backend.log"
    echo "    tail -f $LOG_DIR/galion-app.log"
    echo "    tail -f $LOG_DIR/developer-platform.log"
    echo "    tail -f $LOG_DIR/galion-studio.log"
    echo ""
    echo "  🔍 Check Processes:"
    echo "    ps aux | grep -E '(uvicorn|npm|next)' | grep -v grep"
    echo ""
    echo "  🛑 Stop All Services:"
    echo "    pkill -f uvicorn && pkill -f 'npm.*run.*dev'"
    echo ""
    echo "=================================================================================="
    echo "✅ VERIFICATION CHECKLIST"
    echo "=================================================================================="
    echo ""
    echo "  ✅ Backend Health:     curl http://localhost:$BACKEND_PORT/health"
    echo "  ✅ Galion App:         curl http://localhost:$GALION_APP_PORT"
    echo "  ✅ Developer Platform: curl http://localhost:$DEVELOPER_PLATFORM_PORT"
    echo "  ✅ Galion Studio:      curl http://localhost:$GALION_STUDIO_PORT"
    echo ""
    echo "=================================================================================="
    echo ""
    echo "🎯 YOUR GALION PLATFORM IS NOW FULLY OPERATIONAL!"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Configure Cloudflare DNS to point to $PUBLIC_IP"
    echo "   2. Test all URLs above"
    echo "   3. Start accepting users!"
    echo ""
    echo "=================================================================================="
}

# ============================================================================
# MAIN DEPLOYMENT SCRIPT
# ============================================================================

main() {
    log_header "🚀 GALION PLATFORM AUTOMATIC DEPLOYMENT"
    echo ""
    log_info "This script will deploy the complete Galion Platform on RunPod"
    log_info "Estimated deployment time: 5-10 minutes"
    echo ""

    # Pre-flight checks
    log_step "Performing pre-flight checks..."

    if [[ ! -d "$PROJECT_DIR" ]]; then
        log_error "Project directory not found: $PROJECT_DIR"
        log_error "Please ensure the project is uploaded to /workspace/project-nexus"
        exit 1
    fi

    check_command "python"
    check_command "pip"
    check_command "node"
    check_command "npm"
    check_command "curl"

    log_success "Pre-flight checks passed"
    echo ""

    # Clean up existing processes
    cleanup_processes

    # Deploy components
    deploy_backend
    deploy_galion_app
    deploy_developer_platform
    deploy_galion_studio

    # Get public IP
    get_public_ip

    # Show final status
    show_final_status

    log_header "🎉 DEPLOYMENT SUCCESSFUL!"
    log_info "Your Galion Platform is now running on RunPod!"
    log_info "Configure Cloudflare DNS to point domains to: $PUBLIC_IP"
}

# Run main function
main "$@"
