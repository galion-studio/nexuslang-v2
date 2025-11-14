#!/bin/bash
echo "🚀 Starting Nexus Lang V2 Server - Final Version"
echo "==============================================="

# Kill any existing processes
pkill -f uvicorn || true
sleep 2

# Set environment
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
cd /workspace/project-nexus/v2/backend

# Create logs directory
mkdir -p /workspace/logs

# Start server in background
echo "Starting server on http://0.0.0.0:8080"
echo "External access: http://213.173.105.83:8080"
echo ""

nohup python -m uvicorn main_simple:app \
    --host 0.0.0.0 \
    --port 8080 \
    --workers 1 \
    --log-level info \
    --access-log \
    > /workspace/logs/galion-backend.log 2>&1 &

SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

# Wait for startup
sleep 3

# Test if it's running
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server process is running"

    # Test local access
    if curl -s http://localhost:8080/health > /dev/null; then
        echo "✅ Local health check: PASSED"
        echo ""
        echo "🎉 SERVER IS READY!"
        echo "=================="
        echo "Local:  http://localhost:8080"
        echo "External: http://213.173.105.83:8080"
        echo "Health:  http://213.173.105.83:8080/health"
        echo "Docs:    http://213.173.105.83:8080/docs"
        echo ""
        echo "PID: $SERVER_PID"
        echo "Logs: tail -f /workspace/logs/galion-backend.log"
    else
        echo "❌ Local health check: FAILED"
        echo "Check logs: tail -f /workspace/logs/galion-backend.log"
    fi
else
    echo "❌ Server failed to start"
    echo "Check logs: tail -f /workspace/logs/galion-backend.log"
fi
