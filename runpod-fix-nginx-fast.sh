#!/bin/bash
# Quick fix: Configure nginx to proxy to FastAPI on port 3000

echo "🚀 Quick nginx proxy fix for RunPod"
echo "====================================="

# Stop any existing servers
echo "1. Stopping existing servers..."
pkill -f uvicorn || true
sleep 2

# Start FastAPI on port 3000 (internal only)
echo "2. Starting FastAPI on port 3000..."
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
cd /workspace/project-nexus/v2/backend

nohup python -m uvicorn main_simple:app \
    --host 127.0.0.1 \
    --port 3000 \
    --workers 1 \
    --log-level info \
    > /workspace/logs/galion-nginx.log 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > /workspace/logs/server-nginx.pid
sleep 3

# Test internal connection
echo "3. Testing internal connection..."
if curl -f http://127.0.0.1:3000/health > /dev/null 2>&1; then
    echo "✅ FastAPI running on port 3000"
else
    echo "❌ FastAPI not responding on port 3000"
    tail -10 /workspace/logs/galion-nginx.log
    exit 1
fi

# Configure nginx to proxy (if we have permissions)
echo "4. Configuring nginx proxy..."
if [ -w /etc/nginx/sites-enabled/ ]; then
    # Backup and replace nginx config
    cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup.$(date +%s) 2>/dev/null

    cat > /etc/nginx/sites-enabled/default << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

    # Reload nginx
    nginx -t && nginx -s reload
    echo "✅ nginx configured and reloaded"
else
    echo "❌ Cannot modify nginx config (no permissions)"
    echo "💡 Try: sudo ./runpod-fix-nginx-fast.sh"
    exit 1
fi

# Test external access
echo "5. Testing external access..."
sleep 2

echo "Testing: http://213.173.105.83/health"
if curl -f --max-time 10 http://213.173.105.83/health > /dev/null 2>&1; then
    echo "✅ External access working!"
    echo "🌐 Your API is now accessible at:"
    echo "   http://213.173.105.83"
    echo "   https://a51059ucg22sxt.proxy.runpod.net"
else
    echo "❌ External access still not working"
    echo "Checking nginx status..."
    ps aux | grep nginx | grep -v grep
fi

echo ""
echo "📊 Status:"
echo "• FastAPI PID: $SERVER_PID"
echo "• Internal: http://127.0.0.1:3000"
echo "• External: http://213.173.105.83"
echo "• Proxy: https://a51059ucg22sxt.proxy.runpod.net"
