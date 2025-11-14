#!/bin/bash
echo "🚀 Final Server Setup - Port 8080"
echo "================================="

# Kill any running servers
pkill -f uvicorn
sleep 2

# Start server on port 8080 (which is exposed in RunPod)
cd /workspace/project-nexus/v2/backend
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2

echo "Starting server on port 8080..."
python -m uvicorn main_simple:app --host 0.0.0.0 --port 8080 --workers 1 --log-level info --access-log > /dev/null 2>&1 &

SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

# Wait and verify
sleep 3

if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server is running!"
    echo ""
    echo "🌐 EXTERNAL ACCESS URLs:"
    echo "======================"
    echo "Main Site:    http://213.173.105.83:8080"
    echo "Health Check: http://213.173.105.83:8080/health"
    echo "API Docs:     http://213.173.105.83:8080/docs"
    echo "Scientific APIs: http://213.173.105.83:8080/api/v1/scientific-capabilities"
    echo ""
    echo "🔍 Verification:"
    curl -s http://localhost:8080/health
    echo ""
    echo "🎯 TEST: Open http://213.173.105.83:8080 in your browser!"
else
    echo "❌ Server failed to start"
fi
