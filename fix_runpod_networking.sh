#!/bin/bash
# Fix RunPod Networking Issues
# This script addresses common RunPod connectivity problems

set -e

echo "🔧 RunPod Networking Fix - Complete Solution"
echo "============================================"

# Method 1: Check RunPod environment and networking setup
echo ""
echo "1. Checking RunPod environment..."
if [ -f /.dockerenv ] || [ -f /run/.containerenv ]; then
    echo "✅ Running in Docker container"
    CONTAINER_MODE=true
else
    echo "✅ Running in VM environment"
    CONTAINER_MODE=false
fi

# Check if we're in RunPod by looking for RunPod-specific files
if [ -d "/runpod-volume" ] || [ -n "$RUNPOD_POD_ID" ] || [ -f "/.runpod" ]; then
    echo "✅ Confirmed: Running on RunPod platform"
    RUNPOD_ENV=true
else
    echo "⚠️  Not clearly identified as RunPod environment"
    RUNPOD_ENV=false
fi

# Method 2: Handle RunPod-specific networking requirements
echo ""
echo "2. Configuring RunPod networking..."

# For RunPod, we need to handle their specific networking setup
if [ "$RUNPOD_ENV" = true ]; then
    echo "🔧 Detected RunPod environment - using optimized configuration"

    # RunPod often requires binding to all interfaces explicitly
    # and may need specific port handling
    export RUNPOD_MODE=true
else
    echo "🔧 Using standard networking configuration"
    export RUNPOD_MODE=false
fi

# Method 3: Kill existing server and restart with proper binding
echo ""
echo "3. Restarting server with proper configuration..."

# Kill existing processes
pkill -f uvicorn || true
sleep 2

# Start server with RunPod-optimized configuration
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
cd /workspace/project-nexus/v2/backend

echo "Starting server with RunPod-optimized binding..."
if [ "$RUNPOD_ENV" = true ]; then
    # RunPod-specific startup
    nohup python -m uvicorn main_simple:app \
        --host 0.0.0.0 \
        --port 8080 \
        --workers 1 \
        --log-level info \
        --access-log \
        --no-access-log \
        --proxy-headers \
        > /workspace/logs/galion-backend-fixed.log 2>&1 &
else
    # Standard startup
    nohup python -m uvicorn main_simple:app \
        --host 0.0.0.0 \
        --port 8080 \
        --workers 1 \
        --log-level info \
        --access-log \
        > /workspace/logs/galion-backend-fixed.log 2>&1 &
fi

SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

# Wait for startup
sleep 5

# Method 4: Test connectivity
echo ""
echo "4. Testing connectivity..."

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

# Method 5: Check if port is actually bound correctly
echo ""
echo "5. Verifying port binding..."
ss -tlnp | grep 8080

# Method 6: RunPod-specific networking information
echo ""
echo "6. RunPod Networking Information..."

if [ "$RUNPOD_ENV" = true ]; then
    echo "🔍 IMPORTANT: RunPod Container Networking"
    echo ""
    echo "RunPod containers typically expose services through:"
    echo "   • HTTP Proxy (ports 80/443) - RECOMMENDED"
    echo "   • Direct port exposure (if configured in template)"
    echo "   • Jupyter interface integration"
    echo ""
    echo "For external access, you need to:"
    echo "   1. Use RunPod's HTTP proxy feature (port 80/443)"
    echo "   2. Configure your application to run on port 80/443"
    echo "   3. Or ensure your template exposes the required ports"
    echo ""
    echo "📋 RunPod HTTP Proxy Setup:"
    echo "   - Start your server on port 80 or 443"
    echo "   - RunPod will proxy external requests to your container"
    echo "   - External URL will be: https://[POD_ID].proxy.runpod.net"
fi

# Method 7: Get public IP and test external access
echo ""
echo "7. Testing external access..."
PUBLIC_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "unknown")

if [ "$PUBLIC_IP" != "unknown" ]; then
    echo "Public IP detected: $PUBLIC_IP"

    # Test external connection from inside (may not work in containers)
    echo "Testing external access from inside container..."
    echo "Note: This often fails in containerized environments"

    if curl -s --max-time 10 http://$PUBLIC_IP:8080/health > /dev/null; then
        echo "✅ External access from inside: SUCCESS"
        echo "🎉 Server should be accessible externally!"
        echo "   URL: http://$PUBLIC_IP:8080"
        echo "   Health: http://$PUBLIC_IP:8080/health"
        echo "   Docs: http://$PUBLIC_IP:8080/docs"
    else
        echo "⚠️  External access from inside: FAILED (expected in containers)"
        echo ""
        echo "🔍 This is NORMAL for RunPod containers!"
        echo ""
        echo "📋 To access your server externally:"
        echo "   1. Use RunPod's HTTP proxy: https://[YOUR_POD_ID].proxy.runpod.net"
        echo "   2. Or configure port exposure in your RunPod template"
        echo "   3. Or run server on port 80/443 for HTTP proxy"
        echo ""
        echo "🧪 Test from OUTSIDE RunPod:"
        echo "   curl http://$PUBLIC_IP:8080/health"
    fi
else
    echo "❌ Could not determine public IP"
fi

# Method 8: Show current server status and RunPod-specific advice
echo ""
echo "8. Server status:"
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server process is running (PID: $SERVER_PID)"
else
    echo "❌ Server process is not running"
fi

echo ""
echo "🎯 FINAL RECOMMENDATION:"
if [ "$RUNPOD_ENV" = true ]; then
    echo "For RunPod containers, use HTTP proxy (recommended):"
    echo "   1. Change server to port 80: --port 80"
    echo "   2. Access via: https://[POD_ID].proxy.runpod.net"
    echo "   3. Alternative: Configure port exposure in template"
else
    echo "Standard networking should work:"
    echo "   Access via: http://$PUBLIC_IP:8080"
fi

echo ""
echo "🔧 Logs are available at: /workspace/logs/galion-backend-fixed.log"
echo "============================================"
echo "Fix attempt complete!"
