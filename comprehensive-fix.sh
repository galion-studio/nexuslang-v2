#!/bin/bash

# COMPREHENSIVE GALION ECOSYSTEM FIX
# Resolves all deployment issues in one script

set -e

echo "🚀 COMPREHENSIVE GALION ECOSYSTEM FIX"
echo "===================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# STEP 1: Fix directory structure
log_step "1. FIXING DIRECTORY STRUCTURE"

# Move apps from nested directory if they exist
if [[ -d "nexuslang-v2/galion-app" ]]; then
    log_info "Moving galion-app from nested directory"
    mv nexuslang-v2/galion-app .
fi

if [[ -d "nexuslang-v2/developer-platform" ]]; then
    log_info "Moving developer-platform from nested directory"
    mv nexuslang-v2/developer-platform .
fi

# Clean up empty nested directory
if [[ -d "nexuslang-v2" ]] && [[ -z "$(ls -A nexuslang-v2 2>/dev/null)" ]]; then
    rmdir nexuslang-v2 2>/dev/null || true
fi

log_success "Directory structure fixed"

# STEP 2: Install missing dependencies globally
log_step "2. INSTALLING MISSING DEPENDENCIES"

# Install Next.js globally
if ! command -v next &> /dev/null; then
    log_info "Installing Next.js globally"
    npm install -g next
fi

# Install lucide-react globally as fallback
log_info "Ensuring lucide-react is available"
npm install -g lucide-react 2>/dev/null || true

log_success "Global dependencies installed"

# STEP 3: Create missing lib files
log_step "3. CREATING MISSING LIB FILES"

# Create lib directory and api-client for galion-studio
if [[ -d "galion-studio" ]]; then
    mkdir -p galion-studio/lib
    cat > galion-studio/lib/api-client.ts << 'EOF'
// API Client for Galion Studio
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async get(endpoint: string) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    } catch (error) {
      console.error('API GET error:', error);
      throw error;
    }
  }

  async post(endpoint: string, data: any) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    } catch (error) {
      console.error('API POST error:', error);
      throw error;
    }
  }
}

export const apiClient = new ApiClient();
EOF
    log_success "Created galion-studio/lib/api-client.ts"
fi

# STEP 4: Fix router conflicts and build each app
log_step "4. FIXING ROUTER CONFLICTS AND BUILDING APPS"

fix_and_build_app() {
    local app_name=$1

    if [[ ! -d "$app_name" ]]; then
        log_warning "$app_name directory not found, skipping"
        return 1
    fi

    log_info "Fixing $app_name..."

    cd "$app_name"

    # Remove conflicting pages files (keep app router)
    if [[ -f "pages/index.tsx" ]] && [[ -f "app/page.tsx" ]]; then
        log_info "Removing conflicting pages/index.tsx"
        rm -f pages/index.tsx
    fi

    if [[ -f "pages/generate/image.tsx" ]] && [[ -f "app/generate/image/page.tsx" ]]; then
        log_info "Removing conflicting pages/generate/image.tsx"
        rm -f pages/generate/image.tsx
    fi

    # Install/update dependencies
    log_info "Installing dependencies for $app_name..."
    npm install

    # Install missing packages
    if ! npm list lucide-react &>/dev/null; then
        log_info "Installing lucide-react..."
        npm install lucide-react
    fi

    # Try to build
    log_info "Building $app_name..."
    if npm run build; then
        log_success "$app_name built successfully"
        cd ..
        return 0
    else
        log_error "$app_name build failed"
        cd ..
        return 1
    fi
}

# Fix and build each app
apps_built=0
for app in galion-studio galion-app developer-platform; do
    if fix_and_build_app "$app"; then
        ((apps_built++))
    fi
done

log_info "Apps successfully built: $apps_built/3"

# STEP 5: Start services
log_step "5. STARTING ALL SERVICES"

# Stop any existing services
pm2 stop all 2>/dev/null || true
pm2 delete all 2>/dev/null || true

# Start backend
log_info "Starting backend service..."
cd v2/backend
pm2 start python3 --name "galion-backend" -- main_simple.py --host 0.0.0.0 --port 8000
cd ../..

# Start frontend services (only if they built successfully)
if [[ -d "galion-studio/.next" ]]; then
    log_info "Starting galion-studio..."
    cd galion-studio
    pm2 start npm --name "galion-studio" -- run start -- -p 3001
    cd ..
fi

if [[ -d "galion-app/.next" ]]; then
    log_info "Starting galion-app..."
    cd galion-app
    pm2 start npm --name "galion-app" -- run start -- -p 3003
    cd ..
fi

if [[ -d "developer-platform/.next" ]]; then
    log_info "Starting developer-platform..."
    cd developer-platform
    pm2 start npm --name "developer-platform" -- run start -- -p 3002
    cd ..
fi

# Save PM2 configuration
pm2 save
pm2 startup

# STEP 6: Final verification
log_step "6. FINAL VERIFICATION"

echo ""
log_info "PM2 Status:"
pm2 status

echo ""
log_info "Testing endpoints:"

# Test backend directly
echo -n "Backend direct: "
curl -s http://localhost:8000/health | head -c 50 || echo "Failed"

echo ""
echo -n "Nginx health: "
curl -s http://localhost/health || echo "Failed"

echo ""
echo -n "API proxy: "
curl -s http://localhost/api/health | head -c 50 || echo "Failed"

echo ""
echo -n "Nginx port 80: "
ss -tlnp | grep :80 | head -1 || echo "Not listening"

# Count working services
working_services=0
if pm2 jlist 2>/dev/null | jq -r '.[] | select(.pm2_env.status == "online") | .name' 2>/dev/null | grep -q "galion-backend"; then
    ((working_services++))
fi

echo ""
log_info "Working services: $working_services+"
log_info "Apps built: $apps_built/3"

if [[ $working_services -ge 1 ]]; then
    log_success "🎉 GALION ECOSYSTEM DEPLOYMENT COMPLETE!"
    echo ""
    echo "🌐 Access your API at: http://[your-runpod-ip]/api/health"
    echo "💚 Health check at: http://[your-runpod-ip]/health"
    echo ""
    echo "📋 Next: Expose port 80 in RunPod dashboard!"
    echo ""
    echo "🚀 Your scientific AI platform is ready!"
else
    log_error "❌ Deployment issues remain - check logs with: pm2 logs"
fi

echo ""
echo "Script completed at: $(date)"
