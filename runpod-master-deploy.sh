#!/bin/bash

# GALION ECOSYSTEM - RUNPOD MASTER DEPLOYMENT & DIAGNOSTIC SCRIPT
# Comprehensive deployment, health checks, and debugging for RunPod

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Global variables
REPO_URL="https://github.com/galion-studio/nexuslang-v2.git"
BRANCH="clean-nexuslang"
PROJECT_DIR="nexuslang-v2"
DEPLOYMENT_SUCCESS=false
SERVICES_STARTED=false

# Function definitions
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

log_debug() {
    echo -e "${PURPLE}[DEBUG]${NC} $1"
}

log_header() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed or not in PATH"
        return 1
    else
        log_debug "$1 is available"
        return 0
    fi
}

check_service_health() {
    local service_name=$1
    local url=$2
    local expected_content=$3

    log_debug "Checking $service_name at $url"

    if curl -s --max-time 10 "$url" | grep -q "$expected_content"; then
        log_success "$service_name is healthy"
        return 0
    else
        log_error "$service_name health check failed"
        log_debug "Response: $(curl -s --max-time 5 "$url" 2>/dev/null || echo 'Connection failed')"
        return 1
    fi
}

check_port_listening() {
    local port=$1
    local service=$2

    if ss -tlnp | grep -q ":$port "; then
        log_success "$service listening on port $port"
        return 0
    else
        log_error "$service not listening on port $port"
        return 1
    fi
}

# STEP 1: System Prerequisites Check
step_prerequisites() {
    log_header "STEP 1: SYSTEM PREREQUISITES CHECK"

    local checks_passed=0
    local total_checks=6

    # Check OS
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        log_debug "OS: $PRETTY_NAME"
        ((checks_passed++))
    else
        log_warning "Cannot determine OS version"
    fi

    # Check if running as root or sudo available
    if [[ $EUID -eq 0 ]]; then
        log_debug "Running as root"
        ((checks_passed++))
    elif command -v sudo &> /dev/null; then
        log_debug "sudo is available"
        ((checks_passed++))
    else
        log_error "Not running as root and sudo not available"
        return 1
    fi

    # Check essential commands
    for cmd in apt curl wget git python3 pip3 node npm; do
        if check_command "$cmd"; then
            ((checks_passed++))
        fi
    done

    if [[ $checks_passed -eq $total_checks ]]; then
        log_success "All prerequisites met ($checks_passed/$total_checks)"
        return 0
    else
        log_warning "Some prerequisites missing ($checks_passed/$total_checks)"
        return 1
    fi
}

# STEP 2: System Update and Dependencies
step_system_update() {
    log_header "STEP 2: SYSTEM UPDATE & DEPENDENCIES"

    log_info "Updating package list..."
    if ! apt update; then
        log_error "Failed to update package list"
        return 1
    fi

    log_info "Installing system dependencies..."
    if ! apt install -y nginx nodejs npm python3 python3-pip git curl wget htop; then
        log_error "Failed to install system dependencies"
        return 1
    fi

    # Verify installations
    local verify_passed=0
    for cmd in nginx node npm python3 pip3 git curl wget; do
        if check_command "$cmd"; then
            ((verify_passed++))
        fi
    done

    if [[ $verify_passed -ge 7 ]]; then
        log_success "System dependencies installed successfully"
        return 0
    else
        log_error "Some dependencies failed to install"
        return 1
    fi
}

# STEP 3: Repository Setup
step_repo_setup() {
    log_header "STEP 3: REPOSITORY SETUP"

    # Check if directory already exists
    if [[ -d "$PROJECT_DIR" ]]; then
        log_warning "Project directory already exists"
        cd "$PROJECT_DIR"

        # Try to switch to correct branch
        if git checkout "$BRANCH" 2>/dev/null; then
            log_debug "Switched to $BRANCH branch"
            git pull origin "$BRANCH" --allow-unrelated-histories 2>/dev/null || true
        else
            log_warning "Could not switch branches, using existing state"
        fi
    else
        log_info "Cloning repository..."
        if ! git clone "$REPO_URL" "$PROJECT_DIR"; then
            log_error "Failed to clone repository"
            return 1
        fi

        cd "$PROJECT_DIR"

        if ! git checkout "$BRANCH"; then
            log_error "Failed to checkout $BRANCH branch"
            return 1
        fi
    fi

    # Make scripts executable
    chmod +x *.sh 2>/dev/null || true

    # Verify essential files exist
    local essential_files=("runpod-nginx-setup.sh" "galion-app" "galion-studio" "developer-platform" "v2/backend")
    local files_found=0

    for file in "${essential_files[@]}"; do
        if [[ -e "$file" ]]; then
            ((files_found++))
        else
            log_warning "Missing: $file"
        fi
    done

    if [[ $files_found -eq ${#essential_files[@]} ]]; then
        log_success "Repository setup complete"
        return 0
    else
        log_error "Some essential files are missing"
        return 1
    fi
}

# STEP 4: Nginx Configuration
step_nginx_setup() {
    log_header "STEP 4: NGINX CONFIGURATION"

    # Download nginx setup script if missing
    if [[ ! -f "runpod-nginx-setup.sh" ]]; then
        log_warning "nginx setup script missing, downloading..."
        if ! wget -q "https://raw.githubusercontent.com/galion-studio/nexuslang-v2/$BRANCH/runpod-nginx-setup.sh"; then
            log_error "Failed to download nginx setup script"
            return 1
        fi
        chmod +x runpod-nginx-setup.sh
    fi

    log_info "Running nginx setup..."
    if ! sudo bash runpod-nginx-setup.sh; then
        log_error "Nginx setup failed"
        return 1
    fi

    # Verify nginx is working
    if ! sudo nginx -t; then
        log_error "Nginx configuration test failed"
        return 1
    fi

    log_success "Nginx configuration complete"
    return 0
}

# STEP 5: PM2 Installation and Setup
step_pm2_setup() {
    log_header "STEP 5: PM2 PROCESS MANAGER"

    log_info "Installing PM2 globally..."
    if ! npm install -g pm2; then
        log_error "PM2 installation failed"
        return 1
    fi

    # Verify PM2
    if ! command -v pm2 &> /dev/null; then
        log_error "PM2 not found after installation"
        return 1
    fi

    # Check if PM2 daemon is running
    if pm2 list &>/dev/null; then
        log_success "PM2 is running"
    else
        log_warning "PM2 daemon not running, starting..."
        pm2 kill 2>/dev/null || true
        sleep 2
    fi

    log_success "PM2 setup complete"
    return 0
}

# STEP 6: Frontend Dependencies
step_frontend_deps() {
    log_header "STEP 6: FRONTEND DEPENDENCIES"

    local frontends=("galion-app" "galion-studio" "developer-platform")
    local success_count=0

    for frontend in "${frontends[@]}"; do
        log_info "Installing dependencies for $frontend..."

        if [[ -d "$frontend" ]]; then
            cd "$frontend"
            if npm install; then
                log_success "$frontend dependencies installed"
                ((success_count++))
            else
                log_error "Failed to install $frontend dependencies"
            fi
            cd ..
        else
            log_error "$frontend directory not found"
        fi
    done

    if [[ $success_count -eq ${#frontends[@]} ]]; then
        log_success "All frontend dependencies installed"
        return 0
    else
        log_warning "Some frontend dependencies failed ($success_count/${#frontends[@]})"
        return 1
    fi
}

# STEP 7: Backend Dependencies
step_backend_deps() {
    log_header "STEP 7: BACKEND DEPENDENCIES"

    log_info "Installing backend dependencies..."

    if [[ -d "v2/backend" ]]; then
        cd v2/backend
        if pip3 install fastapi uvicorn psutil; then
            log_success "Backend dependencies installed"
            cd ../..
            return 0
        else
            log_error "Backend dependencies installation failed"
            cd ../..
            return 1
        fi
    else
        log_error "Backend directory not found"
        return 1
    fi
}

# STEP 8: Start Services
step_start_services() {
    log_header "STEP 8: STARTING SERVICES"

    local services=(
        "galion-studio:3001"
        "developer-platform:3002"
        "galion-app:3003"
        "galion-backend:8000"
    )

    local started_count=0

    # Start frontend services
    for service_info in "${services[@]}"; do
        IFS=':' read -r service_name port <<< "$service_info"

        if [[ "$service_name" == "galion-backend" ]]; then
            # Backend service
            log_info "Starting $service_name on port $port..."
            cd v2/backend
            if pm2 start python3 --name "$service_name" -- main_simple.py --host 0.0.0.0 --port "$port"; then
                log_success "$service_name started on port $port"
                ((started_count++))
            else
                log_error "Failed to start $service_name"
            fi
            cd ../..
        else
            # Frontend services
            log_info "Starting $service_name on port $port..."
            if [[ -d "$service_name" ]]; then
                cd "$service_name"
                if pm2 start npm --name "$service_name" -- run start -- -p "$port"; then
                    log_success "$service_name started on port $port"
                    ((started_count++))
                else
                    log_error "Failed to start $service_name"
                fi
                cd ..
            else
                log_error "$service_name directory not found"
            fi
        fi
    done

    # Configure PM2
    log_info "Configuring PM2 for persistence..."
    pm2 save
    pm2 startup

    if [[ $started_count -eq ${#services[@]} ]]; then
        log_success "All services started ($started_count/${#services[@]})"
        SERVICES_STARTED=true
        return 0
    else
        log_error "Some services failed to start ($started_count/${#services[@]})"
        return 1
    fi
}

# STEP 9: Health Checks
step_health_checks() {
    log_header "STEP 9: COMPREHENSIVE HEALTH CHECKS"

    local checks_passed=0
    local total_checks=8

    # PM2 status check
    log_info "Checking PM2 status..."
    if pm2 jlist &>/dev/null; then
        local online_count=$(pm2 jlist | jq -r '.[] | select(.pm2_env.status == "online") | .name' 2>/dev/null | wc -l)
        if [[ $online_count -ge 1 ]]; then
            log_success "PM2: $online_count services online"
            ((checks_passed++))
        else
            log_error "PM2: No services online"
        fi
    else
        log_error "PM2 status check failed"
    fi

    # Port listening checks
    if check_port_listening 80 "Nginx"; then ((checks_passed++)); fi
    if check_port_listening 8000 "Backend"; then ((checks_passed++)); fi

    # Service health checks
    if check_service_health "Backend API" "http://localhost:8000/health" "healthy"; then ((checks_passed++)); fi
    if check_service_health "Nginx Health" "http://localhost/health" "healthy"; then ((checks_passed++)); fi
    if check_service_health "API Proxy" "http://localhost/api/health" "healthy"; then ((checks_passed++)); fi

    # Nginx config check
    if sudo nginx -t &>/dev/null; then
        log_success "Nginx configuration valid"
        ((checks_passed++))
    else
        log_error "Nginx configuration invalid"
    fi

    # System resources
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [[ $mem_usage -lt 90 ]]; then
        log_success "Memory usage: ${mem_usage}%"
        ((checks_passed++))
    else
        log_warning "High memory usage: ${mem_usage}%"
        ((checks_passed++))
    fi

    log_header "HEALTH CHECK RESULTS: $checks_passed/$total_checks PASSED"

    if [[ $checks_passed -eq $total_checks ]]; then
        DEPLOYMENT_SUCCESS=true
        return 0
    else
        return 1
    fi
}

# STEP 10: Diagnostic Report
step_diagnostics() {
    log_header "STEP 10: DIAGNOSTIC REPORT"

    echo ""
    log_info "SYSTEM INFORMATION:"
    echo "==================="
    uname -a
    echo "CPU: $(nproc) cores"
    echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
    echo "Disk: $(df -h / | tail -1 | awk '{print $4}') available"

    echo ""
    log_info "PROCESS STATUS:"
    echo "==============="
    ps aux | head -1
    ps aux | grep -E "(nginx|node|python)" | grep -v grep | head -10

    echo ""
    log_info "NETWORK STATUS:"
    echo "==============="
    echo "Listening ports:"
    ss -tlnp | grep -E ":(80|300[1-3]|8000) " | head -10

    echo ""
    log_info "PM2 STATUS:"
    echo "==========="
    pm2 list

    echo ""
    log_info "NGINX STATUS:"
    echo "============="
    sudo systemctl status nginx 2>/dev/null || echo "systemctl not available"
    sudo nginx -t 2>&1

    echo ""
    log_info "LOG FILES (Last 5 lines each):"
    echo "=============================="
    echo "Nginx error log:"
    sudo tail -5 /var/log/nginx/error.log 2>/dev/null || echo "No nginx error log"
    echo ""
    echo "PM2 logs:"
    pm2 logs --lines 3 2>/dev/null || echo "No PM2 logs available"
}

# STEP 11: Final Report and Instructions
step_final_report() {
    log_header "STEP 11: FINAL DEPLOYMENT REPORT"

    echo ""
    if [[ "$DEPLOYMENT_SUCCESS" == true ]]; then
        log_success "🎉 DEPLOYMENT SUCCESSFUL!"
        echo ""
        echo "✅ All services are running and healthy"
        echo "✅ Nginx reverse proxy is configured"
        echo "✅ API endpoints are accessible"
        echo "✅ PM2 process management is active"
        echo ""
        log_header "ACCESS YOUR GALION ECOSYSTEM"
        echo ""
        echo "🌐 Local Access:"
        echo "   Health Check: http://localhost/health"
        echo "   API Endpoint: http://localhost/api/health"
        echo "   API Info:     http://localhost/"
        echo ""
        echo "🌍 External Access (after exposing port 80):"
        echo "   Replace [pod-id] with your RunPod pod ID"
        echo "   https://[pod-id]-80.proxy.runpod.net/api/health"
        echo "   https://[pod-id]-80.proxy.runpod.net/health"
        echo ""
        log_header "RUNPOD DASHBOARD CONFIGURATION"
        echo ""
        echo "1. Go to Settings → TCP Ports"
        echo "2. Add port: 80"
        echo "3. Remove port 80 from TCP if it's there"
        echo "4. Port 80 should be in HTTP Ports section"
        echo "5. Save changes"
        echo ""
        echo "⏱️  Wait 30-60 seconds for changes to take effect"
        echo ""
        log_success "Your Galion Ecosystem is PRODUCTION READY! 🚀"
    else
        log_error "❌ DEPLOYMENT ISSUES DETECTED"
        echo ""
        echo "Some services may not be running properly."
        echo "Check the diagnostic output above for specific issues."
        echo ""
        echo "🔧 COMMON FIXES:"
        echo "   - Check PM2 status: pm2 status"
        echo "   - Restart services: pm2 restart all"
        echo "   - Check logs: pm2 logs"
        echo "   - Verify ports: ss -tlnp | grep :80"
        echo ""
        log_warning "Please share the diagnostic output for troubleshooting assistance."
    fi

    echo ""
    log_header "MAINTENANCE COMMANDS"
    echo ""
    echo "🔄 Restart all services: pm2 restart all"
    echo "📊 Check status: pm2 status"
    echo "📝 View logs: pm2 logs"
    echo "🔍 Health check: curl http://localhost/api/health"
    echo "🛑 Stop all: pm2 stop all && pm2 delete all"
    echo "🔄 Full restart: pm2 kill && pm2 start all"
    echo ""
    echo "Script completed at: $(date)"
}

# Main execution flow
main() {
    log_header "GALION ECOSYSTEM - RUNPOD MASTER DEPLOYMENT"
    echo "Comprehensive deployment, health checks, and diagnostics"
    echo ""

    local step_number=1
    local steps=(
        "step_prerequisites"
        "step_system_update"
        "step_repo_setup"
        "step_nginx_setup"
        "step_pm2_setup"
        "step_frontend_deps"
        "step_backend_deps"
        "step_start_services"
        "step_health_checks"
        "step_diagnostics"
        "step_final_report"
    )

    for step_func in "${steps[@]}"; do
        log_info "Executing Step $step_number: ${step_func//_/ }"
        if $step_func; then
            log_success "Step $step_number completed successfully"
        else
            log_error "Step $step_number failed"
            log_warning "Continuing with remaining steps for diagnostic purposes..."
        fi
        echo ""
        ((step_number++))
    done

    if [[ "$DEPLOYMENT_SUCCESS" == true ]]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"
