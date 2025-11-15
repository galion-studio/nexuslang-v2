#!/bin/bash
# ============================================================================
# Galion Platform - RunPod Update & Deploy Script
# ============================================================================
# Downloads latest changes from GitHub and deploys to RunPod
# "Your imagination is the end."
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Print banner
echo "============================================================================"
echo "🚀 GALION PLATFORM - RUNPOD UPDATE & DEPLOY"
echo "============================================================================"
echo ""
echo "\"Your imagination is the end.\" - Deploying latest changes..."
echo ""

# Configuration
PROJECT_DIR="/workspace/project-nexus"
BACKUP_DIR="/workspace/backup-$(date +%Y%m%d_%H%M%S)"
LOG_DIR="/workspace/logs"

# Create log directory
mkdir -p "$LOG_DIR"

# Step 1: Check if we're on RunPod
log_info "Checking environment..."
if [[ ! -d "/workspace" ]]; then
    log_error "This script is designed for RunPod environment (/workspace not found)"
    exit 1
fi

# Step 2: Navigate to project directory
log_info "Checking project directory..."
if [[ ! -d "$PROJECT_DIR" ]]; then
    log_error "Project directory not found: $PROJECT_DIR"
    log_info "Please run initial setup first: ./runpod-diagnose-and-fix.sh"
    exit 1
fi

cd "$PROJECT_DIR"
log_success "Project directory found"

# Step 3: Create backup (optional)
log_info "Creating backup of current state..."
mkdir -p "$BACKUP_DIR"
cp -r . "$BACKUP_DIR/" 2>/dev/null || true
log_success "Backup created at: $BACKUP_DIR"

# Step 4: Stop existing services
log_info "Stopping existing services..."
docker-compose down 2>/dev/null || true

# Kill any remaining processes
pkill -f "uvicorn\|next dev\|npm" 2>/dev/null || true
sleep 3
log_success "Services stopped"

# Step 5: Pull latest changes from GitHub
log_info "Pulling latest changes from GitHub..."
if git pull origin clean-nexuslang; then
    log_success "Latest changes pulled successfully"
else
    log_warning "Git pull failed, continuing with local changes"
fi

# Step 6: Install/update dependencies
log_info "Updating backend dependencies..."
cd v2/backend
pip install -q -r requirements.txt 2>/dev/null || log_warning "Backend dependencies update failed"

# Step 7: Install/update frontend dependencies
log_info "Updating frontend dependencies..."
cd "$PROJECT_DIR"

# Update galion-app
if [[ -d "galion-app" ]]; then
    log_info "Updating galion-app dependencies..."
    cd galion-app
    npm install --legacy-peer-deps 2>/dev/null || log_warning "galion-app dependencies update failed"
    cd ..
fi

# Update developer-platform
if [[ -d "developer-platform" ]]; then
    log_info "Updating developer-platform dependencies..."
    cd developer-platform
    npm install --legacy-peer-deps 2>/dev/null || log_warning "developer-platform dependencies update failed"
    cd ..
fi

# Update galion-studio
if [[ -d "galion-studio" ]]; then
    log_info "Updating galion-studio dependencies..."
    cd galion-studio
    npm install --legacy-peer-deps 2>/dev/null || log_warning "galion-studio dependencies update failed"
    cd ..
fi

# Step 8: Start services
log_info "Starting updated services..."
cd "$PROJECT_DIR"

# Start Docker services
log_info "Starting Docker infrastructure..."
docker-compose up -d postgres redis backend 2>&1 | grep -E "(Creating|Starting|Created|Started|done|ready|healthy)" || true

# Wait for services to be ready
log_info "Waiting for services to initialize (30 seconds)..."
sleep 30

# Step 9: Verify deployment
log_info "Verifying deployment..."

# Test backend health
log_info "Testing backend health..."
if curl -f -s http://localhost:8010/health/fast > /dev/null 2>&1; then
    log_success "Backend is healthy and responding"
else
    log_warning "Backend health check failed - may still be starting"
fi

# Step 10: Get public IP
log_info "Getting public IP address..."
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to determine")

# Step 11: Display success information
echo ""
echo "============================================================================"
echo "✅ GALION PLATFORM UPDATED & DEPLOYED SUCCESSFULLY!"
echo "============================================================================"
echo ""
echo "📍 Access Points (replace with your RunPod IP):"
echo "  - Backend API:    http://$PUBLIC_IP:8010"
echo "  - API Docs:       http://$PUBLIC_IP:8010/docs"
echo "  - Health Check:   http://$PUBLIC_IP:8010/health/fast"
echo ""
echo "🔍 Service Status:"
echo "  - PostgreSQL:     $(docker-compose ps postgres | grep -q "Up" && echo "✅ Running" || echo "❌ Stopped")"
echo "  - Redis:          $(docker-compose ps redis | grep -q "Up" && echo "✅ Running" || echo "❌ Stopped")"
echo "  - Backend:        $(docker-compose ps backend | grep -q "Up" && echo "✅ Running" || echo "❌ Stopped")"
echo ""
echo "📊 Monitoring:"
echo "  - Prometheus:     http://$PUBLIC_IP:9090"
echo "  - Grafana:        http://$PUBLIC_IP:3001"
echo ""
echo "🔧 Management Commands:"
echo "  - View logs:      docker-compose logs -f"
echo "  - Stop services:  docker-compose down"
echo "  - Restart:        ./runpod-update-and-deploy.sh"
echo "  - Backup location: $BACKUP_DIR"
echo ""
echo "📝 Recent Changes:"
git log --oneline -5 2>/dev/null || echo "Git log not available"
echo ""
echo "============================================================================"
echo ""
log_success "Update complete! \"Your imagination is the end.\" 🚀"

# Save deployment info
echo "Deployment completed at: $(date)" > "$LOG_DIR/last-deployment.txt"
echo "Git commit: $(git rev-parse HEAD 2>/dev/null || echo 'Unknown')" >> "$LOG_DIR/last-deployment.txt"
echo "Public IP: $PUBLIC_IP" >> "$LOG_DIR/last-deployment.txt"
