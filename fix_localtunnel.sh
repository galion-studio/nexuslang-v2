#!/bin/bash
# Fix LocalTunnel IP Issue
# This script will restart LocalTunnel with the correct IP

echo "🔧 Fixing LocalTunnel IP Issue..."
echo ""

# Stop existing LocalTunnel processes
echo "Stopping existing tunnels..."
pkill -f "lt --port" 2>/dev/null

# Wait a moment
sleep 2

# Get current public IP
echo "Getting your current public IP..."
PUBLIC_IP=$(curl -s ifconfig.me)

if [ -z "$PUBLIC_IP" ]; then
    PUBLIC_IP=$(curl -s icanhazip.com)
fi

if [ -z "$PUBLIC_IP" ]; then
    PUBLIC_IP=$(curl -s api.ipify.org)
fi

echo "✅ Your public IP: $PUBLIC_IP"
echo ""

# Start new tunnels
echo "Starting LocalTunnel for Backend (port 8000)..."
nohup lt --port 8000 --subdomain nexuslang-studio > /workspace/logs/lt-backend.log 2>&1 &
sleep 2

echo "Starting LocalTunnel for Frontend (port 3000)..."
nohup lt --port 3000 --subdomain nexuslang-frontend > /workspace/logs/lt-frontend.log 2>&1 &
sleep 2

echo "Starting LocalTunnel for Galion Studio (port 3001)..."
nohup lt --port 3001 --subdomain nexuslang-studio > /workspace/logs/lt-studio.log 2>&1 &
sleep 2

echo ""
echo "✅ LocalTunnel restarted!"
echo ""
echo "🌐 Your URLs:"
echo "  Backend:  https://nexuslang-backend.loca.lt"
echo "  Frontend: https://nexuslang-frontend.loca.lt"
echo "  Studio:   https://nexuslang-studio.loca.lt"
echo ""
echo "🔑 Use this IP as password: $PUBLIC_IP"
echo ""

# Save IP to file
echo "$PUBLIC_IP" > /workspace/current_public_ip.txt
echo "💾 IP saved to: /workspace/current_public_ip.txt"

