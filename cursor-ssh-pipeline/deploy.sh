#!/bin/bash
# ============================================
# Automated Deployment to RunPod
# ============================================
# One-command deployment from Cursor

set -e

# Parse arguments
TARGET="${1:-all}"
SKIP_BUILD="${2:-false}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  DEPLOYING TO RUNPOD${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Functions
write_step() {
    echo -e "${BLUE}[$1]${NC} $2"
}

write_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

write_error() {
    echo -e "${RED}✗ $1${NC}"
}

write_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Check SSH connection
write_step "1/6" "Testing SSH connection..."
if ssh -o ConnectTimeout=5 runpod "echo 'connected'" &>/dev/null; then
    write_success "SSH connection verified"
else
    write_error "Cannot connect to RunPod. Run setup-local-ssh.sh first"
    exit 1
fi

# Pull latest code
write_step "2/6" "Pulling latest code from GitHub..."
ssh runpod << 'EOF'
cd /nexuslang-v2 && \
git fetch origin && \
git checkout clean-nexuslang && \
git pull origin clean-nexuslang
EOF

if [ $? -eq 0 ]; then
    write_success "Code updated"
else
    write_error "Failed to pull code"
    exit 1
fi

# Install dependencies
write_step "3/6" "Installing dependencies..."
ssh runpod << 'EOF'
cd /nexuslang-v2 && \
pip3 install -q fastapi uvicorn psutil pydantic python-multipart && \
echo 'Backend dependencies installed' && \
for app in galion-studio galion-app developer-platform; do
    if [ -d "$app" ]; then
        echo "Installing $app dependencies..."
        cd "$app" && npm install --silent && cd ..
    fi
done
EOF

if [ $? -eq 0 ]; then
    write_success "Dependencies installed"
else
    write_error "Failed to install dependencies"
fi

# Build frontend (if not skipped)
if [ "$SKIP_BUILD" != "true" ] && ([ "$TARGET" == "all" ] || [ "$TARGET" == "frontend" ]); then
    write_step "4/6" "Building frontend applications..."
    ssh runpod << 'EOF'
cd /nexuslang-v2 && \
for app in galion-studio galion-app developer-platform; do
    if [ -d "$app" ]; then
        echo "Building $app..."
        cd "$app" && npm run build && cd ..
    fi
done
EOF
    
    if [ $? -eq 0 ]; then
        write_success "Frontend built"
    else
        write_error "Frontend build failed (continuing anyway...)"
    fi
else
    write_info "Skipping frontend build"
fi

# Stop services
write_step "5/6" "Restarting services..."
ssh runpod "pm2 delete all 2>/dev/null || true" &>/dev/null

# Start services
ssh runpod << 'EOF'
cd /nexuslang-v2 && \
echo 'Starting backend...' && \
cd v2/backend && pm2 start python3 --name galion-backend -- main_simple.py --host 0.0.0.0 --port 8000 && cd ../.. && \
echo 'Starting frontends...' && \
cd galion-studio && pm2 start npm --name galion-studio -- run dev -- -p 3001 && cd .. && \
cd galion-app && pm2 start npm --name galion-app -- run dev -- -p 3003 && cd .. && \
if [ -d 'developer-platform' ]; then cd developer-platform && pm2 start npm --name developer-platform -- run dev -- -p 3002 && cd ..; fi && \
pm2 save && \
echo 'Services started'
EOF

if [ $? -eq 0 ]; then
    write_success "Services started"
else
    write_error "Failed to start services"
    exit 1
fi

# Verify deployment
write_step "6/6" "Verifying deployment..."
sleep 5

ssh runpod << 'EOF'
pm2 status && \
echo '' && \
echo 'Testing backend...' && \
curl -s http://localhost:8000/health | head -c 100
EOF

echo ""
echo -e "${CYAN}============================================${NC}"
write_success "Deployment complete!"
echo -e "${CYAN}============================================${NC}"
echo ""
write_info "To view logs: ./remote-exec.sh 'pm2 logs'"
write_info "To check status: ./remote-exec.sh 'pm2 status'"
echo ""

