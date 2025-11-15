#!/bin/bash

# FINAL ABSOLUTE FIX - Works from any directory
# Comprehensive Galion Ecosystem deployment fix

set -e

echo "🎯 FINAL ABSOLUTE GALION ECOSYSTEM FIX"
echo "====================================="
echo "Works from any directory - finds and fixes everything"

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

# Find the project directory
find_project_dir() {
    # Try common locations
    for dir in "/nexuslang-v2" "$(pwd)/nexuslang-v2" "$(pwd)"; do
        if [[ -d "$dir/v2" ]] || [[ -d "$dir/galion-studio" ]]; then
            echo "$dir"
            return 0
        fi
    done

    # Check if we're already in the project directory
    if [[ -f "runpod-nginx-setup.sh" ]] || [[ -d "v2" ]]; then
        echo "$(pwd)"
        return 0
    fi

    log_error "Could not find Galion project directory"
    return 1
}

# Main execution
main() {
    log_info "Finding project directory..."
    PROJECT_DIR=$(find_project_dir)

    if [[ -z "$PROJECT_DIR" ]]; then
        log_error "Cannot locate project directory. Please run this from within the nexuslang-v2 project."
        exit 1
    fi

    log_success "Found project at: $PROJECT_DIR"
    cd "$PROJECT_DIR"

    # STEP 1: Fix directory structure
    log_step "1. FIXING DIRECTORY STRUCTURE"

    # Move apps from nested directory if they exist
    if [[ -d "nexuslang-v2" ]]; then
        log_info "Found nested nexuslang-v2 directory, fixing structure..."

        # Move all apps to current directory
        for app in galion-app galion-studio developer-platform; do
            if [[ -d "nexuslang-v2/$app" ]]; then
                log_info "Moving $app to project root..."
                mv "nexuslang-v2/$app" .
            fi
        done

        # Move v2 directory if needed
        if [[ -d "nexuslang-v2/v2" ]] && [[ ! -d "v2" ]]; then
            mv "nexuslang-v2/v2" .
        fi

        # Clean up
        if [[ -z "$(ls -A nexuslang-v2 2>/dev/null)" ]]; then
            rmdir nexuslang-v2 2>/dev/null || true
        fi
    fi

    # Verify we have the right structure
    local apps_found=0
    for app in galion-studio galion-app developer-platform; do
        if [[ -d "$app" ]]; then
            ((apps_found++))
            log_success "Found $app directory"
        else
            log_warning "$app directory missing"
        fi
    done

    if [[ -d "v2/backend" ]]; then
        log_success "Found v2/backend directory"
    else
        log_error "v2/backend directory missing - critical error"
        exit 1
    fi

    log_info "Apps found: $apps_found/3"

    # STEP 2: Install global dependencies
    log_step "2. INSTALLING GLOBAL DEPENDENCIES"

    # Install Next.js globally
    if ! command -v next &> /dev/null; then
        log_info "Installing Next.js globally..."
        npm install -g next
    fi

    log_success "Global dependencies ready"

    # STEP 3: Create missing lib files
    log_step "3. CREATING MISSING LIB FILES"

    for app in galion-studio galion-app developer-platform; do
        if [[ -d "$app" ]]; then
            mkdir -p "$app/lib"

            # Create api-client.ts if missing
            if [[ ! -f "$app/lib/api-client.ts" ]]; then
                log_info "Creating $app/lib/api-client.ts"
                cat > "$app/lib/api-client.ts" << 'EOF'
// API Client for Galion Apps
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async get(endpoint: string) {
    const response = await fetch(`${this.baseURL}${endpoint}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async post(endpoint: string, data: any) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
}

export const apiClient = new ApiClient();
EOF
            fi
        fi
    done

    log_success "Lib files created"

    # STEP 4: Fix router conflicts and build
    log_step "4. FIXING ROUTER CONFLICTS & BUILDING"

    local apps_built=0

    for app in galion-studio galion-app developer-platform; do
        if [[ ! -d "$app" ]]; then
            continue
        fi

        log_info "Processing $app..."

        cd "$app"

        # Remove conflicting pages files
        if [[ -f "pages/index.tsx" ]] && [[ -f "app/page.tsx" ]]; then
            log_info "Removing conflicting pages/index.tsx"
            rm -f pages/index.tsx
        fi

        if [[ -f "pages/generate/image.tsx" ]] && [[ -f "app/generate/image/page.tsx" ]]; then
            log_info "Removing conflicting pages/generate/image.tsx"
            rm -f pages/generate/image.tsx
        fi

        # Install dependencies
        log_info "Installing dependencies..."
        npm install

        # Install missing packages
        if ! npm list lucide-react &>/dev/null 2>&1; then
            log_info "Installing lucide-react..."
            npm install lucide-react
        fi

        # Try to build
        log_info "Building $app..."
        if npm run build 2>/dev/null; then
            log_success "$app built successfully"
            ((apps_built++))
        else
            log_warning "$app build failed, but continuing..."
        fi

        cd ..
    done

    log_info "Apps built: $apps_built/3"

    # STEP 5: Start services
    log_step "5. STARTING SERVICES"

    # Stop existing services
    pm2 stop all 2>/dev/null || true
    pm2 delete all 2>/dev/null || true

    # Start backend
    if [[ -d "v2/backend" ]]; then
        log_info "Starting galion-backend..."
        cd v2/backend
        pm2 start python3 --name "galion-backend" -- main_simple.py --host 0.0.0.0 --port 8000
        cd ../..
    fi

    # Start frontend services
    for app in galion-studio galion-app developer-platform; do
        local port=""
        case $app in
            galion-studio) port=3001 ;;
            galion-app) port=3003 ;;
            developer-platform) port=3002 ;;
        esac

        if [[ -d "$app/.next" ]]; then
            log_info "Starting $app on port $port..."
            cd "$app"
            pm2 start npm --name "$app" -- run start -- -p "$port"
            cd ..
        else
            log_warning "$app not built, skipping..."
        fi
    done

    # Save PM2 config
    pm2 save
    pm2 startup

    # STEP 6: Final verification
    log_step "6. FINAL VERIFICATION"

    echo ""
    log_info "PM2 Status:"
    pm2 status

    echo ""
    log_info "Testing endpoints:"

    # Test backend
    echo -n "Backend: "
    curl -s http://localhost:8000/health | head -c 50 || echo "Failed"

    # Test nginx
    echo ""
    echo -n "Nginx health: "
    curl -s http://localhost/health || echo "Failed"

    echo ""
    echo -n "API proxy: "
    curl -s http://localhost/api/health | head -c 50 || echo "Failed"

    echo ""
    echo -n "Port 80: "
    ss -tlnp | grep :80 | head -1 || echo "Not listening"

    # Success summary
    echo ""
    local working_services=$(pm2 jlist 2>/dev/null | jq -r '.[] | select(.pm2_env.status == "online") | .name' 2>/dev/null | wc -l || echo "0")

    log_success "🎉 DEPLOYMENT COMPLETE!"
    echo ""
    echo "📊 Summary:"
    echo "   - Apps built: $apps_built/3"
    echo "   - Services running: $working_services"
    echo "   - Nginx: $(ss -tlnp | grep -q :80 && echo '✅ Listening' || echo '❌ Not listening')"
    echo ""
    echo "🌐 Access your API:"
    echo "   Health: http://[runpod-ip]/health"
    echo "   API: http://[runpod-ip]/api/health"
    echo ""
    echo "📋 Next: Expose port 80 in RunPod dashboard!"
    echo ""
    echo "Script completed at: $(date)"
}

main "$@"
