#!/bin/bash
# ============================================================================
# GALION.STUDIO QUICK DEPLOYMENT
# ============================================================================
# Run this in your RunPod terminal to deploy everything automatically

set -e

echo "=================================================================================="
echo "🚀 GALION PLATFORM - QUICK DEPLOYMENT"
echo "=================================================================================="
echo ""

# Configuration
PROJECT_DIR="/workspace/project-nexus"
LOG_DIR="/workspace/logs"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# Step 1: Setup
log_info "Setting up environment..."
cd "$PROJECT_DIR"
export PYTHONPATH="$PROJECT_DIR:$PROJECT_DIR/v2"
mkdir -p "$LOG_DIR"
log_success "Environment ready"

# Step 2: Kill existing processes
log_info "Cleaning up existing processes..."
pkill -f uvicorn 2>/dev/null || true
pkill -f "npm.*run.*dev" 2>/dev/null || true
sleep 2
log_success "Cleanup complete"

# Step 3: Deploy Backend
log_info "Deploying Backend (Port 8080)..."
pip install -q -r requirements.txt
cd v2/backend
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8080 --workers 2 > "$LOG_DIR/galion-backend.log" 2>&1 &
sleep 3
log_success "Backend deployed"

# Step 4: Deploy Galion App
log_info "Deploying Galion App (Port 3010)..."
cd "$PROJECT_DIR/galion-app"
npm install --silent
nohup npm run dev > "$LOG_DIR/galion-app.log" 2>&1 &
sleep 3
log_success "Galion App deployed"

# Step 5: Deploy Developer Platform
log_info "Deploying Developer Platform (Port 3020)..."
cd "$PROJECT_DIR/developer-platform"
npm install --silent
nohup npm run dev > "$LOG_DIR/developer-platform.log" 2>&1 &
sleep 3
log_success "Developer Platform deployed"

# Step 6: Deploy Galion Studio
log_info "Deploying Galion Studio (Port 3030)..."
cd "$PROJECT_DIR/galion-studio"
npm install --silent
nohup npm run dev > "$LOG_DIR/galion-studio.log" 2>&1 &
sleep 3
log_success "Galion Studio deployed"

# Step 7: Get IP and show status
echo ""
echo "=================================================================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=================================================================================="
echo ""

# Get IP
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Check RunPod dashboard")

echo "🌐 Your RunPod IP: $PUBLIC_IP"
echo ""
echo "📊 Services Running:"
echo "  ✅ Backend API:        http://localhost:8080"
echo "  ✅ Galion App:         http://localhost:3010"
echo "  ✅ Developer Platform: http://localhost:3020"
echo "  ✅ Galion Studio:      http://localhost:3030"
echo ""
echo "🌍 Public URLs:"
echo "  ✅ Backend API:        http://$PUBLIC_IP:8080"
echo "  ✅ Galion App:         http://$PUBLIC_IP:3010"
echo "  ✅ Developer Platform: http://$PUBLIC_IP:3020"
echo "  ✅ Galion Studio:      http://$PUBLIC_IP:3030"
echo ""

# Test health
echo "🔍 Testing backend health..."
HEALTH=$(curl -s http://localhost:8080/health)
if [[ "$HEALTH" == *"healthy"* ]]; then
    log_success "Backend health check: PASSED"
else
    log_warning "Backend health check: Check logs"
fi

echo ""
echo "=================================================================================="
echo "🚀 NEXT: Configure Cloudflare DNS"
echo "=================================================================================="
echo ""
echo "1. Go to Cloudflare Dashboard"
echo "2. Select galion.studio domain"
echo "3. Go to DNS settings"
echo "4. Update A records to point to: $PUBLIC_IP"
echo "5. Set SSL to 'Flexible'"
echo "6. Wait 2-3 minutes"
echo ""
echo "7. Test: https://galion.studio"
echo ""
echo "=================================================================================="
echo "🔧 MONITORING COMMANDS"
echo "=================================================================================="
echo ""
echo "View logs:     tail -f $LOG_DIR/*.log"
echo "Check status:  curl http://localhost:8080/health"
echo "Stop all:      pkill -f uvicorn && pkill -f 'npm.*run.*dev'"
echo ""
echo "=================================================================================="
echo ""
log_success "Galion Platform deployment complete!"
echo "🎯 Your platform is now live on RunPod!"
echo ""
