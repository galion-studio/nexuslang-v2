#!/bin/bash
# Start FastAPI directly on an exposed RunPod port

echo "🎯 Direct RunPod Port Binding"
echo "============================"

# Get the exposed ports
PORT_5432=$RUNPOD_TCP_PORT_5432  # 36277
PORT_6379=$RUNPOD_TCP_PORT_6379  # 36278

echo "RunPod exposed ports:"
echo "• Port 5432 maps to: $PORT_5432"
echo "• Port 6379 maps to: $PORT_6379"

# Try the database port first (5432 is commonly used for web apps)
TARGET_PORT=$PORT_5432

echo ""
echo "🚀 Starting FastAPI directly on exposed port: $TARGET_PORT"
echo "External access: http://213.173.105.83:$TARGET_PORT"

# Stop any existing servers
pkill -f uvicorn || true
sleep 2

# Set environment
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
cd /workspace/project-nexus/v2/backend

# Start server directly on the exposed port
echo "Starting server..."
python -m uvicorn main_simple:app \
    --host 0.0.0.0 \
    --port $TARGET_PORT \
    --workers 1 \
    --log-level info \
    --access-log &
# Note: No nohup, so we can see output

SERVER_PID=$!
echo "Server PID: $SERVER_PID"
sleep 3

# Test local connection
echo ""
echo "Testing local connection..."
if curl -f http://localhost:$TARGET_PORT/health > /dev/null 2>&1; then
    echo "✅ Local connection successful"
else
    echo "❌ Local connection failed"
    echo "Checking server process..."
    ps aux | grep uvicorn | grep -v grep
    echo "Last 10 log lines:"
    tail -10 /workspace/logs/galion-*.log 2>/dev/null || echo "No logs found"
    exit 1
fi

# Test external connection
echo ""
echo "Testing external connection..."
EXTERNAL_IP=213.173.105.83

echo "curl http://$EXTERNAL_IP:$TARGET_PORT/health"
if curl -f --max-time 10 http://$EXTERNAL_IP:$TARGET_PORT/health > /dev/null 2>&1; then
    echo ""
    echo "🎉 SUCCESS! External access working!"
    echo ""
    echo "🌐 Your API is now accessible at:"
    echo "   http://$EXTERNAL_IP:$TARGET_PORT"
    echo "   http://$EXTERNAL_IP:$TARGET_PORT/health"
    echo "   http://$EXTERNAL_IP:$TARGET_PORT/docs"
    echo ""
    echo "📊 Server PID: $SERVER_PID"
    echo "🛑 To stop: kill $SERVER_PID"
else
    echo ""
    echo "❌ External access failed"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "1. Check if port $TARGET_PORT is actually exposed by RunPod"
    echo "2. Verify firewall settings"
    echo "3. Try the other exposed port: $PORT_6379"
    echo ""
    echo "🧪 Manual test:"
    echo "curl -v http://$EXTERNAL_IP:$TARGET_PORT/health"
fi
