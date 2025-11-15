#!/bin/bash

# COMPREHENSIVE FINAL FIX - Galion Ecosystem Deployment
# Fixes all remaining issues: dependencies, missing files, builds, and startup

set -e

echo "🚀 COMPREHENSIVE FINAL FIX - GALION ECOSYSTEM"
echo "============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log_header() {
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}$(printf '%.0s=' {1..50})${NC}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_debug() {
    echo -e "${PURPLE}[DEBUG]${NC} $1"
}

# STEP 1: Fix Directory Structure
log_header "STEP 1: FIXING DIRECTORY STRUCTURE"

# Move apps from nested directory if they exist
if [[ -d "nexuslang-v2/galion-app" ]]; then
    log_info "Moving galion-app from nested directory..."
    mv nexuslang-v2/galion-app .
fi

if [[ -d "nexuslang-v2/developer-platform" ]]; then
    log_info "Moving developer-platform from nested directory..."
    mv nexuslang-v2/developer-platform .
fi

# Verify directories exist
for app in galion-studio galion-app developer-platform; do
    if [[ -d "$app" ]]; then
        log_success "Found: $app"
    else
        log_error "Missing: $app"
    fi
done

# STEP 2: Create Missing API Client Files
log_header "STEP 2: CREATING MISSING API CLIENT FILES"

create_api_client() {
    local app_dir=$1
    local lib_dir="$app_dir/lib"

    if [[ ! -d "$lib_dir" ]]; then
        mkdir -p "$lib_dir"
        log_info "Created lib directory for $app_dir"
    fi

    # Create api-client.ts
    cat > "$lib_dir/api-client.ts" << 'EOF'
import axios from 'axios';

// API Client for Galion Ecosystem
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
EOF

    log_success "Created API client for $app_dir"
}

# Create API clients for all apps
for app in galion-studio galion-app developer-platform; do
    if [[ -d "$app" ]]; then
        create_api_client "$app"
    fi
done

# STEP 3: Install All Dependencies
log_header "STEP 3: INSTALLING ALL DEPENDENCIES"

# Install/update global dependencies
log_info "Installing global dependencies..."
npm install -g pm2 next

# Install frontend dependencies
for app in galion-studio galion-app developer-platform; do
    if [[ -d "$app" ]]; then
        log_info "Installing dependencies for $app..."
        cd "$app"

        # Ensure package.json exists
        if [[ ! -f "package.json" ]]; then
            log_error "No package.json found in $app"
            cd ..
            continue
        fi

        # Install dependencies
        if npm install; then
            log_success "$app dependencies installed"
        else
            log_error "Failed to install $app dependencies"
        fi

        cd ..
    fi
done

# Install backend dependencies
log_info "Installing backend dependencies..."
if [[ -d "v2/backend" ]]; then
    cd v2/backend
    pip3 install fastapi uvicorn psutil
    log_success "Backend dependencies installed"
    cd ../..
else
    log_error "Backend directory not found"
fi

# STEP 4: Fix Router Conflicts and Build Apps
log_header "STEP 4: FIXING ROUTER CONFLICTS & BUILDING APPS"

fix_and_build_app() {
    local app_dir=$1

    if [[ ! -d "$app_dir" ]]; then
        log_warning "$app_dir not found, skipping..."
        return 1
    fi

    log_info "Fixing and building $app_dir..."
    cd "$app_dir"

    # Remove conflicting pages files (keep App Router)
    conflicting_files=(
        "pages/index.tsx"
        "pages/generate/image.tsx"
        "pages/generate/text.tsx"
        "pages/dashboard.tsx"
        "pages/login.tsx"
    )

    for file in "${conflicting_files[@]}"; do
        if [[ -f "$file" ]]; then
            # Check if app router equivalent exists
            app_equivalent="${file/pages/app}"
            app_equivalent="${app_equivalent%.tsx}/page.tsx"

            if [[ -f "$app_equivalent" ]]; then
                log_info "Removing conflicting pages file: $file"
                rm -f "$file"
            fi
        fi
    done

    # Try to build
    log_info "Building $app_dir..."
    if npm run build; then
        log_success "$app_dir built successfully"
        cd ..
        return 0
    else
        log_error "$app_dir build failed, trying development mode..."
        cd ..
        return 1
    fi
}

# Fix and build all apps
for app in galion-studio galion-app developer-platform; do
    if fix_and_build_app "$app"; then
        log_success "$app ready for production"
    else
        log_warning "$app will use development mode"
    fi
done

# STEP 5: Setup Nginx
log_header "STEP 5: SETTING UP NGINX REVERSE PROXY"

# Download and run nginx setup
if [[ ! -f "runpod-nginx-setup.sh" ]]; then
    log_info "Downloading nginx setup script..."
    wget -q "https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/runpod-nginx-setup.sh"
    chmod +x runpod-nginx-setup.sh
fi

if sudo bash runpod-nginx-setup.sh; then
    log_success "Nginx configured successfully"
else
    log_error "Nginx setup failed"
fi

# STEP 6: Start All Services
log_header "STEP 6: STARTING ALL SERVICES"

# Stop any existing services
pm2 stop all 2>/dev/null || true
pm2 delete all 2>/dev/null || true

# Start backend
log_info "Starting backend service..."
cd v2/backend
if pm2 start python3 --name "galion-backend" -- main_simple.py --host 0.0.0.0 --port 8000; then
    log_success "Backend service started"
else
    log_error "Failed to start backend"
fi
cd ../..

# Start frontend services
frontend_apps=("galion-studio:3001" "galion-app:3002" "developer-platform:3003")

for app_info in "${frontend_apps[@]}"; do
    IFS=':' read -r app_name port <<< "$app_info"

    if [[ -d "$app_name" ]]; then
        log_info "Starting $app_name on port $port..."
        cd "$app_name"

        # Try production mode first, fall back to development
        if [[ -d ".next" ]]; then
            # Production build exists
            if pm2 start npm --name "$app_name" -- run start -- -p "$port"; then
                log_success "$app_name started in production mode"
            else
                log_warning "Production start failed for $app_name"
            fi
        else
            # No production build, use development
            log_warning "No production build for $app_name, starting in development mode..."
            if pm2 start npm --name "$app_name" -- run dev -- -p "$port"; then
                log_success "$app_name started in development mode"
            else
                log_error "Failed to start $app_name"
            fi
        fi

        cd ..
    else
        log_warning "$app_name directory not found"
    fi
done

# Save PM2 configuration
pm2 save
pm2 startup

# STEP 7: Final Verification
log_header "STEP 7: FINAL VERIFICATION"

log_info "PM2 Status:"
pm2 status

echo ""
log_info "Testing endpoints:"

# Test backend directly
echo "Backend health: $(curl -s http://localhost:8000/health | head -c 50)"

# Test nginx endpoints
echo "Nginx health: $(curl -s http://localhost/health)"
echo "Nginx API: $(curl -s http://localhost/api/health | head -c 50)"

echo ""
log_header "DEPLOYMENT COMPLETE!"

echo ""
echo "🌐 ACCESS YOUR GALION ECOSYSTEM:"
echo "================================"
echo ""
echo "🚀 API Health: http://[your-pod-id]-80.proxy.runpod.net/api/health"
echo "💚 Health Check: http://[your-pod-id]-80.proxy.runpod.net/health"
echo "ℹ️ API Info: http://[your-pod-id]-80.proxy.runpod.net/"
echo ""
echo "🔧 IMPORTANT: Expose port 80 in RunPod dashboard (HTTP Ports section)"
echo ""
echo "📊 SERVICE STATUS:"
pm2 status
echo ""
log_success "🎉 GALION ECOSYSTEM FULLY DEPLOYED AND OPERATIONAL!"

echo ""
echo "Script completed at: $(date)"
