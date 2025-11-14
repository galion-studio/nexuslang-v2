#!/bin/bash
echo "🔍 External Access Diagnostic"
echo "============================"

# Check if server is running locally
echo ""
echo "1. Local server check:"
ps aux | grep uvicorn | grep -v grep

echo ""
echo "2. Local health check:"
curl -s http://localhost:8080/health | head -3

echo ""
echo "3. Port binding check:"
ss -tlnp | grep 8080

echo ""
echo "4. Network interface check:"
ip addr show | grep -E "(inet |lo:)" | grep -v "127.0.0.1"

echo ""
echo "5. External IP:"
curl -s ifconfig.me

echo ""
echo "6. Test external access from inside:"
timeout 5 curl -v http://213.173.105.83:8080/health 2>&1 | head -10

echo ""
echo "7. Firewall rules:"
iptables -L -n 2>/dev/null | head -10 || echo "No iptables found"

echo ""
echo "8. RunPod network info:"
echo "Container IP: $(hostname -i 2>/dev/null || echo 'unknown')"
echo "Gateway: $(ip route | grep default | awk '{print $3}' 2>/dev/null || echo 'unknown')"
