#!/bin/bash
echo "🔧 Background Server Fix"
echo "========================"

# Method 1: Try with explicit working directory and environment
echo "Method 1: Starting with explicit paths..."
cd /workspace/project-nexus/v2/backend
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
export PYTHONUNBUFFERED=1

# Kill any existing processes
pkill -f uvicorn || true
sleep 1

# Start server with different background method
python -m uvicorn main_simple:app \
    --host 0.0.0.0 \
    --port 8080 \
    --workers 1 \
    --log-level info \
    --access-log &
SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"
sleep 2

# Check if it's still running
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server is running in background!"
    echo "PID: $SERVER_PID"

    # Test local connection
    sleep 1
    if curl -s http://localhost:8080/health > /dev/null; then
        echo "✅ Health check passed!"
        echo ""
        echo "🎉 SUCCESS! Server is accessible at:"
        echo "   http://213.173.105.83:8080"
        echo "   Health: http://213.173.105.83:8080/health"
    else
        echo "❌ Health check failed"
    fi
else
    echo "❌ Server failed to stay running"
    echo "Checking what went wrong..."
    ps aux | grep python | grep -v grep
fi
