#!/bin/bash
# Use socat to forward an exposed port to our FastAPI server

echo "🔌 RunPod Port Forwarding with socat"
echo "===================================="

# Get exposed ports
EXTERNAL_PORT=$RUNPOD_TCP_PORT_5432  # Use the database port
INTERNAL_PORT=3000

echo "Port mapping:"
echo "• External port: $EXTERNAL_PORT"
echo "• Internal port: $INTERNAL_PORT"
echo "• External IP: 213.173.105.83"

# Stop existing servers
echo "1. Stopping existing servers..."
pkill -f uvicorn || true
pkill -f socat || true
sleep 2

# Start FastAPI server
echo "2. Starting FastAPI on port $INTERNAL_PORT..."
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
cd /workspace/project-nexus/v2/backend

nohup python -m uvicorn main_simple:app \
    --host 127.0.0.1 \
    --port $INTERNAL_PORT \
    --workers 1 \
    --log-level info \
    > /workspace/logs/galion-socat.log 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > /workspace/logs/server-socat.pid
sleep 3

# Test internal connection
echo "3. Testing internal FastAPI..."
if curl -f http://127.0.0.1:$INTERNAL_PORT/health > /dev/null 2>&1; then
    echo "✅ FastAPI running on port $INTERNAL_PORT"
else
    echo "❌ FastAPI not responding"
    exit 1
fi

# Install socat if not present
echo "4. Checking socat..."
if ! command -v socat &> /dev/null; then
    echo "Installing socat..."
    apt-get update && apt-get install -y socat
fi

# Start socat port forwarding
echo "5. Starting socat port forwarding..."
echo "Forwarding: 0.0.0.0:$EXTERNAL_PORT → 127.0.0.1:$INTERNAL_PORT"

nohup socat TCP-LISTEN:$EXTERNAL_PORT,fork TCP:127.0.0.1:$INTERNAL_PORT \
    > /workspace/logs/socat.log 2>&1 &

SOCAT_PID=$!
echo $SOCAT_PID > /workspace/logs/socat.pid
sleep 2

# Test socat forwarding
echo "6. Testing socat forwarding..."
if curl -f --max-time 5 http://127.0.0.1:$EXTERNAL_PORT/health > /dev/null 2>&1; then
    echo "✅ Local port forwarding working"
else
    echo "❌ Local port forwarding not working"
    tail -10 /workspace/logs/socat.log
fi

# Test external access
echo "7. Testing external access..."
EXTERNAL_IP=213.173.105.83

echo "Testing: http://$EXTERNAL_IP:$EXTERNAL_PORT/health"
if curl -f --max-time 10 http://$EXTERNAL_IP:$EXTERNAL_PORT/health > /dev/null 2>&1; then
    echo ""
    echo "🎉 SUCCESS! External access working!"
    echo ""
    echo "🌐 Your API is accessible at:"
    echo "   http://$EXTERNAL_IP:$EXTERNAL_PORT"
    echo "   http://$EXTERNAL_IP:$EXTERNAL_PORT/health"
    echo "   http://$EXTERNAL_IP:$EXTERNAL_PORT/docs"
    echo ""
    echo "📊 Status:"
    echo "• FastAPI PID: $SERVER_PID (port $INTERNAL_PORT)"
    echo "• socat PID: $SOCAT_PID (forwarding $EXTERNAL_PORT → $INTERNAL_PORT)"
else
    echo ""
    echo "❌ External access not working on port $EXTERNAL_PORT"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "• Check if port $EXTERNAL_PORT is actually exposed by RunPod"
    echo "• Verify your RunPod template exposes this port"
    echo "• Try a different exposed port"
    echo ""
    echo "Available exposed ports:"
    env | grep RUNPOD_TCP_PORT
fi

echo ""
echo "🛑 To stop: kill $SERVER_PID $SOCAT_PID"
