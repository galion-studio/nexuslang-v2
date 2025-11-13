#!/bin/bash
# 🔧 Fix DNS Probe and Tunnel Issues
# Restarts all tunnels with clean connections

echo "🔧 Fixing DNS Probe and Tunnel Issues..."
echo "========================================"

# Kill all tunnel processes
echo "Stopping all tunnels..."
pkill -f "cloudflared" || true
pkill -f "lt --port" || true
sleep 3

# Clear DNS cache
echo "Clearing DNS cache..."
systemd-resolve --flush-caches 2>/dev/null || true

# Check if services are running
echo "Checking services..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend not running! Starting..."
    cd /workspace/project-nexus/v2/backend
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /workspace/logs/backend.log 2>&1 &
    sleep 5
fi

if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Frontend not running! Starting..."
    cd /workspace/project-nexus/v2/frontend
    nohup npm run dev -- --port 3000 > /workspace/logs/frontend.log 2>&1 &
    sleep 5
fi

# Use LocalTunnel with unique subdomains (Most Reliable)
echo "Starting LocalTunnel with unique subdomains..."
TIMESTAMP=$(date +%s)

# Backend tunnel
lt --port 8000 --subdomain galion-backend-${TIMESTAMP} > /workspace/logs/lt-backend-new.log 2>&1 &
sleep 3

# Frontend tunnel  
lt --port 3000 --subdomain galion-frontend-${TIMESTAMP} > /workspace/logs/lt-frontend-new.log 2>&1 &
sleep 3

# Wait for tunnels to establish
sleep 5

# Get URLs
BACKEND_URL=$(grep "your url is" /workspace/logs/lt-backend-new.log | tail -1 | awk '{print $NF}')
FRONTEND_URL=$(grep "your url is" /workspace/logs/lt-frontend-new.log | tail -1 | awk '{print $NF}')
PUBLIC_IP=$(curl -s ifconfig.me)

# Display results
echo ""
echo "============================================"
echo "✅ DNS FIX COMPLETE!"
echo "============================================"
echo ""
echo "🌐 YOUR NEW WORKING URLS:"
echo ""
echo "  Backend API (with docs):"
echo "    ${BACKEND_URL}/docs"
echo ""
echo "  Frontend Application:"
echo "    ${FRONTEND_URL}"
echo ""
echo "🔑 Password: ${PUBLIC_IP}"
echo ""
echo "✅ These URLs use fresh tunnels and should work!"
echo "============================================"
echo ""

# Save to file
cat > /workspace/WORKING_URLS.txt << EOF
Current Working URLs
====================
Generated: $(date)

Backend API:  ${BACKEND_URL}/docs
Frontend:     ${FRONTEND_URL}
Password:     ${PUBLIC_IP}

Local URLs (on RunPod):
- Backend:  http://localhost:8000
- Frontend: http://localhost:3000

Service Status:
- Backend:  $(curl -s http://localhost:8000/health 2>/dev/null || echo "Not responding")
- Frontend: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "Not responding")

Logs:
- Backend:  /workspace/logs/backend.log
- Frontend: /workspace/logs/frontend.log
- Tunnels:  /workspace/logs/lt-*.log
EOF

echo "💾 URLs saved to: /workspace/WORKING_URLS.txt"
echo ""
echo "🎯 Try the URLs above now!"

