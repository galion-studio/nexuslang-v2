#!/bin/bash
echo "📺 Starting Server with Screen"
echo "=============================="

# Check if screen is available
if ! command -v screen &> /dev/null; then
    echo "❌ screen not available, installing..."
    apt-get update && apt-get install -y screen
fi

# Kill any existing processes
pkill -f uvicorn || true
sleep 1

# Start server in screen session
echo "Starting server in screen session 'galion-server'..."
screen -dmS galion-server bash -c "
cd /workspace/project-nexus/v2/backend
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
export PYTHONUNBUFFERED=1
python -m uvicorn main_simple:app --host 0.0.0.0 --port 8080 --workers 1 --log-level info --access-log
"

sleep 2

# Check if screen session exists
if screen -list | grep -q galion-server; then
    echo "✅ Server screen session created!"
    echo ""
    echo "To view server: screen -r galion-server"
    echo "To detach: Ctrl+A, D"
    echo "To stop: screen -X -S galion-server quit"
    echo ""

    # Test if server is responding
    sleep 2
    if curl -s http://localhost:8080/health > /dev/null; then
        echo "🎉 SUCCESS! Server is running!"
        echo "External access: http://213.173.105.83:8080"
        echo "Health check: http://213.173.105.83:8080/health"
        echo "API docs: http://213.173.105.83:8080/docs"
    else
        echo "❌ Server not responding yet, waiting..."
        sleep 3
        if curl -s http://localhost:8080/health > /dev/null; then
            echo "🎉 Server is now running!"
            echo "External access: http://213.173.105.83:8080"
        else
            echo "❌ Still not responding. Check screen session:"
            echo "screen -r galion-server"
        fi
    fi
else
    echo "❌ Failed to create screen session"
fi
