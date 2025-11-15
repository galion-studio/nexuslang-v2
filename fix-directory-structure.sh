#!/bin/bash

# Fix Directory Structure and Dependencies
# Corrects the nested directory issues and installs missing dependencies

echo "🔧 FIXING DIRECTORY STRUCTURE AND DEPENDENCIES"
echo "=============================================="

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

# Check current directory structure
log_info "Analyzing current directory structure..."
pwd
ls -la | head -10

# Check if we're in the right place
if [[ -d "galion-studio" ]] && [[ -d "v2/backend" ]]; then
    log_success "Already in correct directory structure"
else
    # Check if directories are nested in nexuslang-v2
    if [[ -d "nexuslang-v2" ]]; then
        log_info "Found nested nexuslang-v2 directory, moving contents..."
        cd nexuslang-v2
        # Move everything up one level
        for item in *; do
            if [[ "$item" != "." && "$item" != ".." ]]; then
                mv "$item" ..
            fi
        done
        cd ..
        rmdir nexuslang-v2 2>/dev/null || true
        log_success "Fixed nested directory structure"
    else
        log_error "Cannot find proper directory structure"
        exit 1
    fi
fi

# Now verify we have the correct structure
log_info "Verifying directory structure..."
missing_dirs=()

for dir in galion-app galion-studio developer-platform; do
    if [[ ! -d "$dir" ]]; then
        missing_dirs+=("$dir")
        log_error "Missing: $dir"
    else
        log_success "Found: $dir"
    fi
done

if [[ -d "v2/backend" ]]; then
    log_success "Found: v2/backend"
else
    log_error "Missing: v2/backend"
    missing_dirs+=("v2/backend")
fi

# Install frontend dependencies
log_info "Installing frontend dependencies..."

for dir in galion-studio "${missing_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        log_info "Installing dependencies in $dir..."
        cd "$dir"
        if npm install; then
            log_success "$dir dependencies installed"
        else
            log_error "Failed to install $dir dependencies"
        fi
        cd ..
    fi
done

# Ensure Next.js is available globally (fallback)
log_info "Ensuring Next.js CLI is available..."
if ! command -v next &> /dev/null; then
    log_info "Installing Next.js globally..."
    npm install -g next
fi

# Install backend dependencies
log_info "Installing backend dependencies..."
if [[ -d "v2/backend" ]]; then
    cd v2/backend
    if pip3 install fastapi uvicorn psutil; then
        log_success "Backend dependencies installed"
    else
        log_error "Failed to install backend dependencies"
    fi
    cd ../..
else
    log_error "Backend directory not found"
fi

# Final verification
log_info "Final verification..."
echo ""
echo "Directory structure:"
ls -la | grep -E "(galion|developer|v2)"

echo ""
echo "Node modules status:"
for dir in galion-app galion-studio developer-platform; do
    if [[ -d "$dir" ]]; then
        node_modules_status="❌ missing"
        if [[ -d "$dir/node_modules" ]]; then
            node_modules_status="✅ exists"
        fi
        echo "$dir: $node_modules_status"
    fi
done

echo ""
log_success "Directory structure and dependencies fix complete!"
echo "You can now run the frontend build script."
