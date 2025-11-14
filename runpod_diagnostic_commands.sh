#!/bin/bash
echo "🔍 RunPod Network Diagnostic"
echo "============================"

echo ""
echo "1. Server processes:"
ps aux | grep uvicorn | grep -v grep

echo ""
echo "2. Listening ports:"
ss -tlnp | grep 8080

echo ""
echo "3. Local test:"
curl -s http://localhost:8080/health | head -5

echo ""
echo "4. Network interfaces:"
ip addr show | grep -E "(inet |lo:)" | head -10

echo ""
echo "5. Firewall rules:"
iptables -L -n | head -20 2>/dev/null || echo "No iptables"

echo ""
echo "6. External IP:"
curl -s ifconfig.me || echo "Could not get IP"

echo ""
echo "7. Test external from inside:"
timeout 5 curl -v http://213.173.105.83:8080/health 2>&1 | head -10

echo ""
echo "8. Container networking:"
echo "Container IP: $(hostname -i 2>/dev/null || echo 'unknown')"
echo "Gateway: $(ip route | grep default | awk '{print $3}' 2>/dev/null || echo 'unknown')"
