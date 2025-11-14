#!/bin/bash
# Configure nginx to proxy to FastAPI app on port 3000

echo "🔧 Configuring nginx to proxy to FastAPI"
echo "=========================================="

# Check if we can modify nginx config
if [ ! -w /etc/nginx/sites-enabled/ ]; then
    echo "❌ Cannot modify nginx config (no write permissions)"
    echo "💡 Try using port 3000 instead with: ./runpod-start-port-3000.sh"
    exit 1
fi

echo "1. Backing up current nginx config..."
cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup.$(date +%s) 2>/dev/null || echo "Could not backup config"

echo "2. Creating new nginx config to proxy to port 3000..."

# Create nginx config that proxies to our FastAPI app
cat > /etc/nginx/sites-enabled/default << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    # Proxy to FastAPI app on port 3000
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

echo "3. Testing nginx config..."
nginx -t 2>/dev/null || echo "nginx config test failed"

echo "4. Reloading nginx..."
systemctl reload nginx 2>/dev/null || service nginx reload 2>/dev/null || nginx -s reload 2>/dev/null || echo "Could not reload nginx"

echo "5. Starting FastAPI on port 3000..."
cd /workspace/project-nexus

# Kill any existing servers
pkill -f uvicorn || true
sleep 2

# Start on port 3000
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
cd /workspace/project-nexus/v2/backend

echo "Starting FastAPI on port 3000..."
nohup python -m uvicorn main_simple:app \
    --host 127.0.0.1 \
    --port 3000 \
    --workers 1 \
    --log-level info \
    --access-log \
    > /workspace/logs/galion-nginx-proxy.log 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > /workspace/logs/server-nginx-proxy.pid

sleep 3

echo "6. Testing the setup..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ nginx proxy working!"
    echo "🌐 Your app should now be accessible at:"
    echo "   http://a51059ucg22sxt.proxy.runpod.net"
    echo "   http://213.173.105.83"
else
    echo "❌ nginx proxy not working"
    echo "Check logs: tail -f /workspace/logs/galion-nginx-proxy.log"
fi

echo ""
echo "=========================================="
echo "nginx proxy configuration complete!"
