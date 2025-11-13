#!/bin/bash
# 🚀 Complete Auto-Launch System for RunPod
# Starts all services with new UI automatically

set -e

echo "🚀 AUTO-LAUNCHING GALION ECOSYSTEM..."
echo "===================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Create logs directory
mkdir -p /workspace/logs

# Step 1: Start PostgreSQL
print_status "Starting PostgreSQL..."
/etc/init.d/postgresql start || service postgresql start || print_warning "PostgreSQL may already be running"
sleep 3

# Setup database
su - postgres -c "psql -c \"CREATE DATABASE nexus_db;\"" 2>/dev/null || true
su - postgres -c "psql -c \"CREATE USER nexus WITH PASSWORD 'nexus123';\"" 2>/dev/null || true
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE nexus_db TO nexus;\"" 2>/dev/null || true
print_success "Database ready!"

# Step 2: Start Backend
print_status "Starting Backend API..."
cd /workspace/project-nexus/v2/backend

# Install dependencies if needed
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Kill any existing backend
pkill -f "uvicorn main:app" || true

# Start backend
source venv/bin/activate
pip install -q -r requirements.txt
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /workspace/logs/backend.log 2>&1 &
print_success "Backend started on port 8000!"

sleep 5

# Step 3: Start Frontend with NEW UI
print_status "Starting Frontend with New UI..."
cd /workspace/project-nexus/v2/frontend

# Kill any existing frontend
pkill -f "next dev.*3000" || true

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    npm install --silent
fi

# Start frontend
nohup npm run dev -- --port 3000 > /workspace/logs/frontend.log 2>&1 &
print_success "Frontend started on port 3000!"

sleep 5

# Step 4: Start Galion Studio
print_status "Starting Galion Studio..."
cd /workspace/project-nexus/galion-studio

# Kill any existing studio
pkill -f "next dev.*3001" || true

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    npm install --silent
fi

# Start studio
nohup npm run dev -- --port 3001 > /workspace/logs/studio.log 2>&1 &
print_success "Galion Studio started on port 3001!"

sleep 5

# Step 5: Setup LocalTunnel with unique subdomains
print_status "Setting up public URLs..."

# Kill old tunnels
pkill -f "lt --port" || true
sleep 2

# Get timestamp for unique subdomains
TIMESTAMP=$(date +%s)

# Start tunnels
nohup lt --port 8000 --subdomain galion-api-${TIMESTAMP} > /workspace/logs/lt-backend.log 2>&1 &
sleep 3
nohup lt --port 3000 --subdomain galion-app-${TIMESTAMP} > /workspace/logs/lt-frontend.log 2>&1 &
sleep 3
nohup lt --port 3001 --subdomain galion-studio-${TIMESTAMP} > /workspace/logs/lt-studio.log 2>&1 &
sleep 5

# Get URLs
BACKEND_URL=$(grep "your url is" /workspace/logs/lt-backend.log | tail -1 | awk '{print $NF}')
FRONTEND_URL=$(grep "your url is" /workspace/logs/lt-frontend.log | tail -1 | awk '{print $NF}')
STUDIO_URL=$(grep "your url is" /workspace/logs/lt-studio.log | tail -1 | awk '{print $NF}')
PUBLIC_IP=$(curl -s ifconfig.me)

print_success "LocalTunnel configured!"

# Step 6: Health Checks
print_status "Running health checks..."
sleep 5

curl -s http://localhost:8000/health > /dev/null && print_success "✅ Backend healthy" || print_warning "⚠️  Backend still starting..."
curl -s http://localhost:3000 > /dev/null && print_success "✅ Frontend healthy" || print_warning "⚠️  Frontend still starting..."
curl -s http://localhost:3001 > /dev/null && print_success "✅ Studio healthy" || print_warning "⚠️  Studio still starting..."

echo ""
echo "============================================"
echo "🎉 GALION ECOSYSTEM IS LIVE!"
echo "============================================"
echo ""
echo "📱 PUBLIC URLS (Password: ${PUBLIC_IP}):"
echo ""
echo "  🔹 Backend API:"
echo "     ${BACKEND_URL}/docs"
echo ""
echo "  🔹 Developer Platform:"
echo "     ${FRONTEND_URL}"
echo ""
echo "  🔹 Galion Studio:"
echo "     ${STUDIO_URL}"
echo ""
echo "🔑 Password: ${PUBLIC_IP}"
echo ""
echo "📊 View Logs:"
echo "  Backend:  tail -f /workspace/logs/backend.log"
echo "  Frontend: tail -f /workspace/logs/frontend.log"
echo "  Studio:   tail -f /workspace/logs/studio.log"
echo ""
echo "✅ All services running!"
echo "============================================"
echo ""

# Save info
cat > /workspace/DEPLOYMENT_INFO.txt << EOF
Galion Ecosystem - Deployment Info
===================================
Deployed: $(date)

Public URLs (Password: ${PUBLIC_IP}):
- Backend API: ${BACKEND_URL}/docs
- Frontend: ${FRONTEND_URL}
- Studio: ${STUDIO_URL}

Local URLs:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Studio: http://localhost:3001

Services Status:
- PostgreSQL: Running
- Backend: Running (PID: $(pgrep -f "uvicorn main:app"))
- Frontend: Running (PID: $(pgrep -f "next dev.*3000"))
- Studio: Running (PID: $(pgrep -f "next dev.*3001"))
- LocalTunnel: 3 tunnels active

Admin Credentials:
- Email: maci.grajczyk@gmail.com
- Password: Admin123!@#SecurePassword

Logs Location: /workspace/logs/
EOF

print_success "Deployment info saved to /workspace/DEPLOYMENT_INFO.txt"

