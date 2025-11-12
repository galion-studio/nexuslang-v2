#!/bin/bash
# ===============================================
# Nexus Documentation Server
# Quick start script for serving status page and API docs
# ===============================================

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   🚀 Nexus Documentation Server             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python detected: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version)
    echo "✓ Python detected: $PYTHON_VERSION"
else
    echo "✗ Python not found! Please install Python 3.7+"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt install python3"
    exit 1
fi

# Get local IP address
echo ""
echo "🔍 Detecting network configuration..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
else
    # Linux
    LOCAL_IP=$(hostname -I | awk '{print $1}')
fi

if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="localhost"
fi

echo "   Local IP: $LOCAL_IP"

# Choose port
PORT=8888
echo "   Port: $PORT"

# Check if port is available
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo ""
    echo "⚠️  Port $PORT is already in use!"
    echo "   Attempting to use port 9999 instead..."
    PORT=9999
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   📡 Server Starting...                      ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

echo "Access your documentation at:"
echo ""
echo "  📊 Status Page:"
echo "     http://localhost:$PORT/nexus-status.html"
echo "     http://$LOCAL_IP:$PORT/nexus-status.html"
echo ""
echo "  📚 API Documentation:"
echo "     http://localhost:$PORT/api-docs/index.html"
echo "     http://$LOCAL_IP:$PORT/api-docs/index.html"
echo ""
echo "  📖 Service Details:"
echo "     http://localhost:$PORT/docs/"
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   Share with others on your network:         ║"
echo "║   http://$LOCAL_IP:$PORT/nexus-status.html"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "💡 Tip: For public internet access, see:"
echo "   PUBLIC_ACCESS_GUIDE.md"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "═══════════════════════════════════════════════"

# Try to open in browser (macOS and Linux)
sleep 2
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:$PORT/nexus-status.html" 2>/dev/null
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:$PORT/nexus-status.html" 2>/dev/null
fi

# Start Python HTTP server
$PYTHON_CMD -m http.server $PORT

