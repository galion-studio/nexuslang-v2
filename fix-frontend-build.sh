#!/bin/bash

# Fix Frontend Build Issues for Galion Ecosystem
# Build all frontend apps and fix port conflicts

set -e

echo "🔧 FIXING FRONTEND BUILD ISSUES"
echo "==============================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Stop all current services
log_info "Stopping all current services..."
pm2 stop all
pm2 delete all

# Build and start each frontend app
build_and_start() {
    local app_name=$1
    local port=$2

    log_info "Building $app_name..."

    if [[ -d "$app_name" ]]; then
        cd "$app_name"

        # Build the app
        if npm run build; then
            log_success "$app_name built successfully"

            # Start in production mode
            if pm2 start npm --name "$app_name" -- run start -- -p "$port"; then
                log_success "$app_name started on port $port"
            else
                log_error "Failed to start $app_name"
            fi
        else
            log_error "Failed to build $app_name"
        fi

        cd ..
    else
        log_error "$app_name directory not found"
    fi
}

# Build and start each app
build_and_start "galion-studio" "3001"
build_and_start "developer-platform" "3002"
build_and_start "galion-app" "3003"

# Ensure backend is running
log_info "Ensuring backend is running..."
cd v2/backend
pm2 start python3 --name "galion-backend" -- main_simple.py --host 0.0.0.0 --port 8000
cd ../..

# Save PM2 configuration
pm2 save

echo ""
log_info "Checking final status..."
pm2 status

echo ""
echo "🧪 Testing endpoints..."
echo "Health: $(curl -s http://localhost/health)"
echo "API: $(curl -s http://localhost/api/health | head -c 50)..."

echo ""
log_success "Frontend build fix complete!"
echo "If services are still failing, check PM2 logs: pm2 logs"
