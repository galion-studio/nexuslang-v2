#!/bin/bash
# Use one of the RunPod exposed ports

echo "🔧 Using RunPod Exposed Port"
echo "============================"

# Get the exposed ports from environment
SSH_PORT=$RUNPOD_TCP_PORT_22
DB_PORT=$RUNPOD_TCP_PORT_5432
REDIS_PORT=$RUNPOD_TCP_PORT_6379

echo "RunPod exposed ports:"
echo "• SSH: $SSH_PORT"
echo "• Database: $DB_PORT"
echo "• Redis: $REDIS_PORT"

# Try to use the database port (5432) which is commonly used for web services
EXTERNAL_PORT=$DB_PORT
INTERNAL_PORT=3000

echo ""
echo "Using external port: $EXTERNAL_PORT (mapped to internal port: $INTERNAL_PORT)"

# Stop existing servers
echo "1. Stopping existing servers..."
pkill -f uvicorn || true
sleep 2

# Start server on the internal port
echo "2. Starting FastAPI on internal port $INTERNAL_PORT..."
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
cd /workspace/project-nexus/v2/backend

nohup python -m uvicorn main_simple:app \
    --host 0.0.0.0 \
    --port $INTERNAL_PORT \
    --workers 1 \
    --log-level info \
    > /workspace/logs/galion-exposed-port.log 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > /workspace/logs/server-exposed-port.pid
sleep 3

# Test internal connection
echo "3. Testing internal connection..."
if curl -f http://localhost:$INTERNAL_PORT/health > /dev/null 2>&1; then
    echo "✅ FastAPI running on port $INTERNAL_PORT"
else
    echo "❌ FastAPI not responding on port $INTERNAL_PORT"
    tail -10 /workspace/logs/galion-exposed-port.log
    exit 1
fi

# Configure nginx to proxy from external port to internal port
echo "4. Configuring nginx proxy..."
if [ -w /etc/nginx/sites-enabled/ ]; then
    # Create a new server block for the exposed port
    cat >> /etc/nginx/sites-enabled/default << EOF

server {
    listen $EXTERNAL_PORT;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:$INTERNAL_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

    # Reload nginx
    nginx -t && nginx -s reload
    echo "✅ nginx configured for port $EXTERNAL_PORT"
else
    echo "❌ Cannot modify nginx config"
    exit 1
fi

# Test external access
echo "5. Testing external access..."
sleep 2

EXTERNAL_IP=213.173.105.83
echo "Testing: http://$EXTERNAL_IP:$EXTERNAL_PORT/health"
if curl -f --max-time 10 http://$EXTERNAL_IP:$EXTERNAL_PORT/health > /dev/null 2>&1; then
    echo "✅ External access working on port $EXTERNAL_PORT!"
    echo ""
    echo "🌐 Your API is now accessible at:"
    echo "   http://$EXTERNAL_IP:$EXTERNAL_PORT"
    echo "   http://$EXTERNAL_IP:$EXTERNAL_PORT/health"
    echo "   http://$EXTERNAL_IP:$EXTERNAL_PORT/docs"
else
    echo "❌ External access not working on port $EXTERNAL_PORT"
    echo ""
    echo "💡 This port may not be exposed by RunPod"
    echo "   Check your RunPod template configuration"
fi

echo ""
echo "📊 Current Status:"
echo "• FastAPI PID: $SERVER_PID (port $INTERNAL_PORT)"
echo "• nginx proxy: port $EXTERNAL_PORT → $INTERNAL_PORT"
echo "• External IP: $EXTERNAL_IP"
