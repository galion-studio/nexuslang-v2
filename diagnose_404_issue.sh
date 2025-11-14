#!/bin/bash
# Diagnose 404 Issue with RunPod Proxy

echo "🔍 Diagnosing 404 Issue with RunPod Proxy"
echo "=========================================="

echo ""
echo "1. Checking server processes..."
ps aux | grep uvicorn | grep -v grep

echo ""
echo "2. Checking listening ports..."
ss -tlnp | grep -E ":(80|8080)"

echo ""
echo "3. Testing local access to port 80..."
curl -s http://localhost:80/health || echo "❌ Local port 80 not accessible"

echo ""
echo "4. Testing local access to port 8080..."
curl -s http://localhost:8080/health || echo "❌ Local port 8080 not accessible"

echo ""
echo "5. Testing direct IP access (port 80)..."
curl -s --max-time 5 http://213.173.105.83:80/health || echo "❌ Direct IP port 80 not accessible"

echo ""
echo "6. Testing direct IP access (port 8080)..."
curl -s --max-time 5 http://213.173.105.83:8080/health || echo "❌ Direct IP port 8080 not accessible"

echo ""
echo "7. Testing RunPod proxy..."
curl -v --max-time 10 https://a51059ucg22sxt.proxy.runpod.net/health 2>&1 | head -10

echo ""
echo "8. Checking firewall/iptables..."
iptables -L -n 2>/dev/null | head -10 || echo "No iptables found"

echo ""
echo "9. Checking RunPod environment..."
env | grep -i runpod || echo "No RunPod environment variables found"

echo ""
echo "10. Server logs (last 10 lines)..."
tail -10 /workspace/logs/galion-http-proxy.log 2>/dev/null || echo "No proxy logs found"
tail -10 /workspace/logs/galion-backend.log 2>/dev/null || echo "No backend logs found"

echo ""
echo "=========================================="
echo "DIAGNOSIS COMPLETE"
echo ""
echo "Possible issues:"
echo "• RunPod proxy not configured for port 80"
echo "• Server not binding correctly to port 80"
echo "• RunPod networking restrictions"
echo "• Wrong proxy URL format"
