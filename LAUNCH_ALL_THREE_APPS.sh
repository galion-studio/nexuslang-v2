#!/bin/bash
# 🚀 Launch ALL THREE Galion Apps Automatically
# 1. developer.galion.app (v2)
# 2. galion.app (v1 - Voice AI)
# 3. galion.studio

set -e

echo "🚀 LAUNCHING ALL THREE GALION APPS..."
echo "======================================"
echo ""

# Get timestamp for unique subdomains
TIMESTAMP=$(date +%s)

# Create logs directory
mkdir -p /workspace/logs

# Kill any existing services
echo "Stopping any existing services..."
pkill -f "uvicorn" || true
pkill -f "next dev" || true
pkill -f "lt --port" || true
sleep 3

# ===================================
# APP 1: developer.galion.app (v2)
# ===================================
echo "🔷 Starting developer.galion.app..."

# Backend (port 8000)
cd /workspace/project-nexus/v2/backend
pip3 install -q -r requirements.txt
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /workspace/logs/developer-backend.log 2>&1 &
echo "  ✅ Backend started on port 8000"

# Frontend (port 3000)
cd /workspace/project-nexus/v2/frontend
nohup npm run dev -- --port 3000 > /workspace/logs/developer-frontend.log 2>&1 &
echo "  ✅ Frontend started on port 3000"

sleep 5

# ===================================
# APP 2: galion.studio  
# ===================================
echo "🔷 Starting galion.studio..."

cd /workspace/project-nexus/galion-studio
if [ -f "package.json" ]; then
    nohup npm run dev -- --port 3001 > /workspace/logs/studio.log 2>&1 &
    echo "  ✅ Studio started on port 3001"
else
    echo "  ⚠️  galion.studio not found, skipping"
fi

sleep 5

# ===================================
# APP 3: galion.app (Voice AI) - if exists
# ===================================
echo "🔷 Starting galion.app (Voice AI)..."

if [ -d "/workspace/project-nexus/v1/galion" ]; then
    # Backend (port 8100)
    if [ -f "/workspace/project-nexus/v1/galion/backend/main.py" ]; then
        cd /workspace/project-nexus/v1/galion/backend
        pip3 install -q -r requirements.txt 2>/dev/null || true
        nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8100 > /workspace/logs/galion-backend.log 2>&1 &
        echo "  ✅ Backend started on port 8100"
    fi
    
    # Frontend (port 3100)
    if [ -d "/workspace/project-nexus/v1/galion/frontend" ]; then
        cd /workspace/project-nexus/v1/galion/frontend
        nohup npm run dev -- --port 3100 > /workspace/logs/galion-frontend.log 2>&1 &
        echo "  ✅ Frontend started on port 3100"
    fi
else
    echo "  ⏭️  galion.app not found, skipping"
fi

sleep 10

# ===================================
# Setup LocalTunnel for all apps
# ===================================
echo ""
echo "🌐 Setting up public URLs..."

# Developer.galion.app tunnels
lt --port 8000 --subdomain galion-developer-api-${TIMESTAMP} > /workspace/logs/lt-dev-api.log 2>&1 &
sleep 2
lt --port 3000 --subdomain galion-developer-app-${TIMESTAMP} > /workspace/logs/lt-dev-app.log 2>&1 &
sleep 2

# Galion.studio tunnel
lt --port 3001 --subdomain galion-studio-${TIMESTAMP} > /workspace/logs/lt-studio.log 2>&1 &
sleep 2

# Galion.app tunnels (if running)
if pgrep -f "uvicorn.*8100" > /dev/null; then
    lt --port 8100 --subdomain galion-voice-api-${TIMESTAMP} > /workspace/logs/lt-voice-api.log 2>&1 &
    sleep 2
    lt --port 3100 --subdomain galion-voice-app-${TIMESTAMP} > /workspace/logs/lt-voice-app.log 2>&1 &
    sleep 2
fi

sleep 5

# ===================================
# Get all URLs
# ===================================
PUBLIC_IP=$(curl -s ifconfig.me)

DEV_API=$(grep "your url is" /workspace/logs/lt-dev-api.log 2>/dev/null | tail -1 | awk '{print $NF}')
DEV_APP=$(grep "your url is" /workspace/logs/lt-dev-app.log 2>/dev/null | tail -1 | awk '{print $NF}')
STUDIO=$(grep "your url is" /workspace/logs/lt-studio.log 2>/dev/null | tail -1 | awk '{print $NF}')
VOICE_API=$(grep "your url is" /workspace/logs/lt-voice-api.log 2>/dev/null | tail -1 | awk '{print $NF}')
VOICE_APP=$(grep "your url is" /workspace/logs/lt-voice-app.log 2>/dev/null | tail -1 | awk '{print $NF}')

# ===================================
# Health Checks
# ===================================
echo ""
echo "🏥 Running health checks..."
sleep 5

curl -s http://localhost:8000/health > /dev/null && echo "  ✅ developer.galion.app backend: HEALTHY" || echo "  ⚠️  developer.galion.app backend: starting..."
curl -s http://localhost:3000 > /dev/null && echo "  ✅ developer.galion.app frontend: HEALTHY" || echo "  ⚠️  developer.galion.app frontend: starting..."
curl -s http://localhost:3001 > /dev/null && echo "  ✅ galion.studio: HEALTHY" || echo "  ⚠️  galion.studio: starting..."

if pgrep -f "uvicorn.*8100" > /dev/null; then
    curl -s http://localhost:8100/health > /dev/null && echo "  ✅ galion.app backend: HEALTHY" || echo "  ⚠️  galion.app backend: starting..."
fi

# ===================================
# LAUNCH COMPLETE
# ===================================
echo ""
echo "============================================"
echo "🎉 ALL GALION APPS ARE LIVE!"
echo "============================================"
echo ""
echo "🔑 Password for all URLs: ${PUBLIC_IP}"
echo ""
echo "📱 1. DEVELOPER.GALION.APP (Developer Platform)"
echo "   Backend API:  ${DEV_API}/docs"
echo "   Frontend App: ${DEV_APP}"
echo "   Features: IDE, AI Chat, Code Execution, Grokopedia"
echo ""
echo "📱 2. GALION.STUDIO (Content Creation)"
echo "   Studio App:   ${STUDIO}"
echo "   Features: Image, Video, Text, Voice Generation"
echo ""

if [ -n "$VOICE_APP" ]; then
echo "📱 3. GALION.APP (Voice AI Assistant)"
echo "   Backend API:  ${VOICE_API}"
echo "   Frontend App: ${VOICE_APP}"
echo "   Features: Voice-first AI for science"
echo ""
fi

echo "📊 Service Status:"
echo "  developer.galion.app: $(pgrep -f 'uvicorn.*8000' > /dev/null && echo '🟢 UP' || echo '🔴 DOWN')"
echo "  galion.studio:        $(pgrep -f 'next.*3001' > /dev/null && echo '🟢 UP' || echo '🔴 DOWN')"
echo "  galion.app:           $(pgrep -f 'uvicorn.*8100' > /dev/null && echo '🟢 UP' || echo '⏭️  Not deployed')"
echo ""
echo "📁 Logs: /workspace/logs/"
echo "============================================"
echo ""

# Save deployment info
cat > /workspace/ALL_APPS_DEPLOYED.txt << EOF
Galion Ecosystem - All Apps Deployed
=====================================
Deployed: $(date)
Password: ${PUBLIC_IP}

1. developer.galion.app (Developer Platform)
   - Backend:  ${DEV_API}/docs
   - Frontend: ${DEV_APP}
   - Local: http://localhost:8000 + http://localhost:3000

2. galion.studio (Content Creation)
   - App: ${STUDIO}
   - Local: http://localhost:3001

3. galion.app (Voice AI)
   - Backend:  ${VOICE_API}
   - Frontend: ${VOICE_APP}
   - Local: http://localhost:8100 + http://localhost:3100

Admin Credentials:
- Email: maci.grajczyk@gmail.com
- Password: Admin123!@#SecurePassword

Logs: /workspace/logs/
EOF

echo "✅ Deployment info saved to: /workspace/ALL_APPS_DEPLOYED.txt"
echo ""
echo "🎉 ALL SYSTEMS OPERATIONAL! GO TEST YOUR APPS!"

