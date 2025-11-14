#!/bin/bash
echo "🔄 Testing Port 3000 (often allowed by default)"
echo "=============================================="

# Kill current server
pkill -f uvicorn
sleep 1

# Start on port 3000
cd /workspace/project-nexus/v2/backend
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2

echo "Starting server on port 3000..."
python -m uvicorn main_simple:app --host 0.0.0.0 --port 3000 --workers 1 --log-level info --access-log > /dev/null 2>&1 &

SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

sleep 2

if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server running on port 3000"
    curl -s http://localhost:3000/health | head -2
    echo ""
    echo "🌐 Test these URLs:"
    echo "   http://213.173.105.83:3000"
    echo "   Health: http://213.173.105.83:3000/health"
else
    echo "❌ Server failed to start on port 3000"
fi
