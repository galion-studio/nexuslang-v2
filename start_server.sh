#!/bin/bash
echo "🚀 Starting Nexus Lang V2 Server"
echo "==============================="

# Kill any existing servers
pkill -f uvicorn
sleep 1

# Set environment
cd /workspace/project-nexus/v2/backend
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2

# Start server in background
echo "Starting server on port 8080..."
python -m uvicorn main_simple:app --host 0.0.0.0 --port 8080 --workers 1 --log-level info --access-log > /dev/null 2>&1 &

# Get PID
SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

# Wait and test
sleep 2
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server is running!"
    curl -s http://localhost:8080/health
    echo ""
    echo "🌐 Access URLs:"
    echo "   http://213.173.105.83:8080"
    echo "   Health: http://213.173.105.83:8080/health"
    echo "   Docs: http://213.173.105.83:8080/docs"
else
    echo "❌ Server failed to start"
fi
