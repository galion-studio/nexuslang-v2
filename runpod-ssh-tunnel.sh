#!/bin/bash
# Create SSH tunnel for immediate access to your API

echo "🔒 RunPod SSH Tunnel for API Access"
echo "==================================="

LOCAL_PORT=8080
REMOTE_PORT=36277
REMOTE_HOST=$RUNPOD_PUBLIC_IP

echo "Tunnel Configuration:"
echo "• Local port: $LOCAL_PORT"
echo "• Remote port: $REMOTE_PORT"
echo "• Remote host: $REMOTE_HOST"
echo ""

echo "🚀 Starting SSH tunnel..."
echo "Command: ssh -L $LOCAL_PORT:localhost:$REMOTE_PORT root@$REMOTE_HOST -N"
echo ""

echo "📋 Instructions:"
echo "1. Open a NEW terminal window on your LOCAL machine"
echo "2. Run this command:"
echo ""
echo "   ssh -L $LOCAL_PORT:localhost:$REMOTE_PORT root@$REMOTE_HOST -N"
echo ""
echo "3. Keep that terminal open (tunnel will run in background)"
echo "4. In your BROWSER, access your API at:"
echo ""
echo "   http://localhost:$LOCAL_PORT"
echo "   http://localhost:$LOCAL_PORT/health"
echo "   http://localhost:$LOCAL_PORT/docs"
echo ""

echo "✅ Your API will be accessible locally while the tunnel runs!"
echo ""

echo "🛑 To stop the tunnel: Press Ctrl+C in the tunnel terminal"
echo ""

echo "💡 Pro tip: Add '-f' to run tunnel in background:"
echo "   ssh -f -L $LOCAL_PORT:localhost:$REMOTE_PORT root@$REMOTE_HOST -N"
