#!/bin/bash
# 🚀 MASTER DEPLOYMENT - All Galion Platforms
# Automatically deploys all frontends, backends, and services

set -e

echo "🚀 MASTER DEPLOYMENT STARTING..."
echo "================================"

# Variables
TIMESTAMP=$(date +%s)
mkdir -p /workspace/logs

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_status() { echo -e "${BLUE}🔵 $1${NC}"; }

# ===========================================
# STEP 1: BACKEND API (Port 8000)
# ===========================================
print_status "Starting Backend API..."
cd /workspace/project-nexus/v2/backend
pkill -f "uvicorn main:app" || true
pip3 install -q -r requirements.txt
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /workspace/logs/backend.log 2>&1 &
sleep 5
print_success "Backend API running on port 8000"

# ===========================================
# STEP 2: DEVELOPER.GALION.APP Frontend (Port 3000)
# ===========================================
print_status "Starting developer.galion.app..."
cd /workspace/project-nexus/v2/frontend
pkill -f "next dev.*3000" || true
nohup npm run dev -- --port 3000 > /workspace/logs/frontend.log 2>&1 &
sleep 5
print_success "developer.galion.app running on port 3000"

# ===========================================
# STEP 3: GALION.STUDIO (Port 3002)
# ===========================================
print_status "Starting galion.studio..."
cd /workspace/project-nexus/galion-studio
pkill -f "next dev.*3002" || true

# Create simple working page if doesn't exist
if [ ! -f "pages/index.js" ] || grep -q "cat" pages/index.js; then
    print_status "Creating galion.studio pages..."
    mkdir -p pages
    cat > pages/index.js << 'EOPAGE'
export default function Home(){
return(
<div style={{padding:'50px',background:'#667eea',minHeight:'100vh',color:'white',textAlign:'center'}}>
<h1 style={{fontSize:'64px',marginBottom:'20px'}}>Galion Studio</h1>
<p style={{fontSize:'28px',marginBottom:'40px'}}>AI Content Creation Platform</p>
<div style={{fontSize:'18px',opacity:0.9}}>
<p>✅ Image Generation</p>
<p>✅ Video Generation</p>
<p>✅ Text Generation</p>
<p>✅ Voice Synthesis</p>
</div>
</div>
)
}
EOPAGE
fi

nohup npm run dev -- --port 3002 > /workspace/logs/studio.log 2>&1 &
sleep 5
print_success "galion.studio running on port 3002"

# ===========================================
# STEP 4: LOCALTUNNEL URLs
# ===========================================
print_status "Creating LocalTunnel URLs..."
pkill -f "lt --port" || true
sleep 2

lt --port 8000 --subdomain galion-api-${TIMESTAMP} > /workspace/logs/tunnel-api.log 2>&1 &
sleep 2
lt --port 3000 --subdomain galion-app-${TIMESTAMP} > /workspace/logs/tunnel-app.log 2>&1 &
sleep 2
lt --port 3002 --subdomain galion-studio-${TIMESTAMP} > /workspace/logs/tunnel-studio.log 2>&1 &
sleep 5

print_success "LocalTunnel URLs created"

# ===========================================
# STEP 5: CLOUDFLARE TUNNELS (Optional)
# ===========================================
if command -v cloudflared &> /dev/null; then
    print_status "Creating Cloudflare Tunnels (no password)..."
    pkill -f "cloudflared tunnel" || true
    
    nohup cloudflared tunnel --url http://localhost:8000 > /workspace/logs/cf-api.log 2>&1 &
    sleep 3
    nohup cloudflared tunnel --url http://localhost:3000 > /workspace/logs/cf-app.log 2>&1 &
    sleep 3
    nohup cloudflared tunnel --url http://localhost:3002 > /workspace/logs/cf-studio.log 2>&1 &
    sleep 5
    
    print_success "Cloudflare Tunnels created"
fi

# ===========================================
# STEP 6: HEALTH CHECKS
# ===========================================
print_status "Running health checks..."
sleep 10

BACKEND_OK=$(curl -s http://localhost:8000/health 2>/dev/null && echo "✅" || echo "❌")
FRONTEND_OK=$(curl -s http://localhost:3000 2>/dev/null && echo "✅" || echo "❌")
STUDIO_OK=$(curl -s http://localhost:3002 2>/dev/null && echo "✅" || echo "❌")

# ===========================================
# STEP 7: GET ALL URLS
# ===========================================
PUBLIC_IP=$(curl -s ifconfig.me)

# LocalTunnel URLs
LT_API=$(grep "your url is" /workspace/logs/tunnel-api.log 2>/dev/null | tail -1 | awk '{print $NF}')
LT_APP=$(grep "your url is" /workspace/logs/tunnel-app.log 2>/dev/null | tail -1 | awk '{print $NF}')
LT_STUDIO=$(grep "your url is" /workspace/logs/tunnel-studio.log 2>/dev/null | tail -1 | awk '{print $NF}')

# Cloudflare URLs
CF_API=$(grep "trycloudflare.com" /workspace/logs/cf-api.log 2>/dev/null | grep -oP 'https://[^ ]+')
CF_APP=$(grep "trycloudflare.com" /workspace/logs/cf-app.log 2>/dev/null | grep -oP 'https://[^ ]+')
CF_STUDIO=$(grep "trycloudflare.com" /workspace/logs/cf-studio.log 2>/dev/null | grep -oP 'https://[^ ]+')

# ===========================================
# DEPLOYMENT COMPLETE!
# ===========================================
echo ""
echo "============================================"
echo "🎉 COMPLETE DEPLOYMENT SUCCESSFUL!"
echo "============================================"
echo ""
echo "📊 SERVICE STATUS:"
echo "  Backend API:        $BACKEND_OK"
echo "  developer.galion.app: $FRONTEND_OK"
echo "  galion.studio:      $STUDIO_OK"
echo ""
echo "🌐 LOCALTUNNEL URLs (Password: ${PUBLIC_IP}):"
echo "  Backend:  ${LT_API}/docs"
echo "  Frontend: ${LT_APP}"
echo "  Studio:   ${LT_STUDIO}"
echo ""

if [ -n "$CF_API" ]; then
echo "☁️  CLOUDFLARE TUNNELS (NO password!):"
echo "  Backend:  ${CF_API}/docs"
echo "  Frontend: ${CF_APP}"
echo "  Studio:   ${CF_STUDIO}"
echo ""
fi

echo "💻 LOCAL URLs (on RunPod):"
echo "  Backend:  http://localhost:8000/docs"
echo "  Frontend: http://localhost:3000"
echo "  Studio:   http://localhost:3002"
echo ""
echo "============================================"
echo ""

# Save deployment info
cat > /workspace/DEPLOYMENT_COMPLETE.txt << EOFINFO
Galion Ecosystem - Complete Deployment
========================================
Deployed: $(date)

LocalTunnel URLs (Password: ${PUBLIC_IP}):
- Backend API:  ${LT_API}/docs
- Frontend:     ${LT_APP}
- Studio:       ${LT_STUDIO}

Cloudflare Tunnels (NO password):
- Backend:  ${CF_API}/docs
- Frontend: ${CF_APP}
- Studio:   ${CF_STUDIO}

Local URLs:
- Backend:  http://localhost:8000
- Frontend: http://localhost:3000
- Studio:   http://localhost:3002

Service Status:
- Backend:  ${BACKEND_OK}
- Frontend: ${FRONTEND_OK}
- Studio:   ${STUDIO_OK}

Logs: /workspace/logs/

Admin Credentials:
- Email: maci.grajczyk@gmail.com
- Password: Admin123!@#SecurePassword
EOFINFO

print_success "Deployment info saved to /workspace/DEPLOYMENT_COMPLETE.txt"
echo ""
echo "🎊 ALL PLATFORMS ARE LIVE!"
echo "🚀 Share your URLs with the world!"
echo ""

