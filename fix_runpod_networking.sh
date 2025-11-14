#!/bin/bash
# Fix RunPod Networking Issues
# This script addresses common RunPod connectivity problems

set -e

echo "🔧 Fixing RunPod Networking Issues"
echo "==================================="

# Method 1: Check if we're running in a container vs VM
echo ""
echo "1. Checking RunPod environment..."
if [ -f /.dockerenv ] || [ -f /run/.containerenv ]; then
    echo "✅ Running in Docker container"
    CONTAINER_MODE=true
else
    echo "✅ Running in VM environment"
    CONTAINER_MODE=false
fi

# Method 2: Kill existing server and restart with proper binding
echo ""
echo "2. Restarting server with proper configuration..."

# Kill existing processes
pkill -f uvicorn || true
sleep 2

# Start server with explicit binding
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
cd /workspace/project-nexus/v2/backend

echo "Starting server with explicit 0.0.0.0 binding..."
nohup python -m uvicorn main_simple:app \
    --host 0.0.0.0 \
    --port 8080 \
    --workers 1 \
    --log-level info \
    --access-log \
    > /workspace/logs/galion-backend-fixed.log 2>&1 &

SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

# Wait for startup
sleep 5

# Method 3: Test connectivity
echo ""
echo "3. Testing connectivity..."

# Test localhost
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Localhost connection: SUCCESS"
else
    echo "❌ Localhost connection: FAILED"
fi

# Test 0.0.0.0
if curl -s http://0.0.0.0:8080/health > /dev/null; then
    echo "✅ 0.0.0.0 connection: SUCCESS"
else
    echo "❌ 0.0.0.0 connection: FAILED"
fi

# Method 4: Check if port is actually bound correctly
echo ""
echo "4. Verifying port binding..."
ss -tlnp | grep 8080

# Method 5: Get public IP and test external access
echo ""
echo "5. Testing external access..."
PUBLIC_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "unknown")

if [ "$PUBLIC_IP" != "unknown" ]; then
    echo "Public IP detected: $PUBLIC_IP"

    # Test external connection from inside (should work if networking is correct)
    echo "Testing external access from inside container..."
    if curl -s --max-time 10 http://$PUBLIC_IP:8080/health > /dev/null; then
        echo "✅ External access from inside: SUCCESS"
        echo "🎉 Server should be accessible externally!"
        echo "   URL: http://$PUBLIC_IP:8080"
        echo "   Health: http://$PUBLIC_IP:8080/health"
        echo "   Docs: http://$PUBLIC_IP:8080/docs"
    else
        echo "❌ External access from inside: FAILED"
        echo ""
        echo "🔍 Troubleshooting steps:"
        echo "   1. Check RunPod firewall settings"
        echo "   2. Verify port exposure in RunPod configuration"
        echo "   3. Check if RunPod requires specific port mapping"
        echo "   4. Try accessing from outside the RunPod environment"
    fi
else
    echo "❌ Could not determine public IP"
fi

# Method 6: Show current server status
echo ""
echo "6. Server status:"
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server process is running (PID: $SERVER_PID)"
else
    echo "❌ Server process is not running"
fi

echo ""
echo "📋 Next steps:"
echo "   1. Try accessing http://$PUBLIC_IP:8080 from outside RunPod"
echo "   2. If still failing, check RunPod network/firewall settings"
echo "   3. Verify your RunPod template exposes port 8080"
echo "   4. Check RunPod documentation for port exposure requirements"

echo ""
echo "🔧 Logs are available at: /workspace/logs/galion-backend-fixed.log"
echo "==================================="
echo "Fix attempt complete!"
