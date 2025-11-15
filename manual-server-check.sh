#!/bin/bash
# ============================================
# Manual RunPod Server Health Check
# ============================================
# Run this on your RunPod instance to verify everything is working

echo "🔍 Galion Platform - Manual Server Health Check"
echo "==============================================="
echo ""

# 1. PM2 Services Status
echo "1️⃣  PM2 Services Status:"
echo "-----------------------"
pm2 status
echo ""

# 2. System Resources
echo "2️⃣  System Resources:"
echo "--------------------"
echo "CPU & Memory:"
free -h
echo ""
echo "Disk Usage:"
df -h /
echo ""

# 3. Nginx Status
echo "3️⃣  Nginx Status:"
echo "----------------"
systemctl status nginx --no-pager -l | head -10
echo ""

# 4. Service Health Checks
echo "4️⃣  Service Health Checks:"
echo "-------------------------"

# Backend API
echo "Backend API (port 8000):"
if curl -s --max-time 5 http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is responding"
    curl -s http://localhost:8000/health | jq . 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "❌ Backend is not responding"
fi
echo ""

# Galion Studio
echo "Galion Studio (port 3030):"
if curl -s --max-time 5 http://localhost:3030 > /dev/null 2>&1; then
    echo "✅ Galion Studio is responding"
else
    echo "❌ Galion Studio is not responding"
fi
echo ""

# Galion App
echo "Galion App (port 3000):"
if curl -s --max-time 5 http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Galion App is responding"
else
    echo "❌ Galion App is not responding"
fi
echo ""

# Developer Platform
echo "Developer Platform (port 3003):"
if curl -s --max-time 5 http://localhost:3003 > /dev/null 2>&1; then
    echo "✅ Developer Platform is responding"
else
    echo "❌ Developer Platform is not responding"
fi
echo ""

# 5. Recent Errors
echo "5️⃣  Recent PM2 Errors (last 20 lines):"
echo "-------------------------------------"
pm2 logs --lines 20 --err 2>/dev/null | tail -20 || echo "No recent errors"
echo ""

# 6. Network Ports
echo "6️⃣  Listening Ports:"
echo "-------------------"
ss -tlnp | grep -E ":(8000|3000|3003|3030|80)" | head -10
echo ""

# 7. External Access Check
echo "7️⃣  External Access Check:"
echo "-------------------------"
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to detect")
echo "External IP: $EXTERNAL_IP"
echo ""
echo "Test these URLs from outside:"
echo "• Backend API: http://$EXTERNAL_IP:8000/health"
echo "• Galion Studio: http://$EXTERNAL_IP:3030"
echo "• Galion App: http://$EXTERNAL_IP:3000"
echo "• Developer Platform: http://$EXTERNAL_IP:3003"
echo ""

echo "==============================================="
echo "✅ Manual health check complete!"
echo "==============================================="
