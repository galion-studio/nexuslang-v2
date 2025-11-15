#!/bin/bash

# Fix Next.js App Router vs Pages Router conflicts
# Removes conflicting pages files to allow App Router to work

set -e

echo "🔧 FIXING NEXT.JS ROUTER CONFLICTS"
echo "==================================="

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

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to fix a single app
fix_app_router() {
    local app_dir=$1

    if [[ ! -d "$app_dir" ]]; then
        log_error "$app_dir directory not found"
        return 1
    fi

    log_info "Fixing router conflicts in $app_dir..."

    cd "$app_dir"

    # Check for conflicting files
    conflicting_files=(
        "pages/index.tsx:app/page.tsx"
        "pages/generate/image.tsx:app/generate/image/page.tsx"
        "pages/dashboard.tsx:app/dashboard/page.tsx"
        "pages/login.tsx:app/login/page.tsx"
        "pages/generate/text.tsx:app/generate/text/page.tsx"
    )

    for conflict in "${conflicting_files[@]}"; do
        IFS=':' read -r pages_file app_file <<< "$conflict"

        if [[ -f "$pages_file" ]] && [[ -f "$app_file" ]]; then
            log_warning "Removing conflicting file: $pages_file (keeping $app_file)"
            rm -f "$pages_file"
        elif [[ -f "$pages_file" ]]; then
            log_info "Keeping pages file: $pages_file (no app conflict)"
        elif [[ -f "$app_file" ]]; then
            log_info "Using app router file: $app_file"
        fi
    done

    # Try to build to verify fix
    log_info "Testing build after conflict resolution..."
    if npm run build; then
        log_success "$app_dir build successful after conflict fix"
    else
        log_error "$app_dir still has build issues"
        return 1
    fi

    cd ..
    return 0
}

# Fix galion-studio (the one we know exists)
fix_app_router "galion-studio"

# Try to find and fix other apps if they exist in nested directory
if [[ -d "nexuslang-v2" ]]; then
    log_info "Checking for apps in nested directory..."

    for app in galion-app developer-platform; do
        if [[ -d "nexuslang-v2/$app" ]]; then
            log_info "Found $app in nested directory, moving and fixing..."
            mv "nexuslang-v2/$app" .
            fix_app_router "$app"
        fi
    done
fi

# Final verification
log_info "Final verification of all apps..."

apps_found=0
apps_working=0

for app in galion-studio galion-app developer-platform; do
    if [[ -d "$app" ]]; then
        ((apps_found++))
        log_info "Checking $app..."

        if [[ -d "$app/.next" ]]; then
            log_success "$app has build artifacts (.next directory)"
            ((apps_working++))
        elif [[ -f "$app/package.json" ]]; then
            log_info "$app exists but needs building"
        fi
    fi
done

echo ""
log_info "Summary: $apps_working/$apps_found apps ready for production"

if [[ $apps_working -gt 0 ]]; then
    log_success "Frontend router conflicts resolved!"
    echo "You can now start the frontend services."
else
    log_error "No apps are ready for production"
    exit 1
fi
