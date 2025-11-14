#!/bin/bash
# Network Diagnostic Script for RunPod
# Run this on your RunPod instance to diagnose connectivity issues

echo "🔍 Network Diagnostic for RunPod Server"
echo "========================================"

# 1. Check server processes
echo ""
echo "1. Checking server processes..."
ps aux | grep uvicorn | grep -v grep

# 2. Check listening ports
echo ""
echo "2. Checking listening ports..."
ss -tlnp | grep 8080

# 3. Check if port is accessible locally
echo ""
echo "3. Testing local connectivity..."
curl -s http://localhost:8080/health | head -5

# 4. Check network interfaces
echo ""
echo "4. Checking network interfaces..."
ip addr show | grep -E "(inet |lo:)" | head -10

# 5. Check iptables/firewall rules
echo ""
echo "5. Checking firewall rules..."
iptables -L -n | head -20 2>/dev/null || echo "iptables not available or no rules"

# 6. Check if external IP is reachable from inside
echo ""
echo "6. Testing external connectivity from inside..."
curl -s --connect-timeout 5 ifconfig.me || echo "Could not get external IP"

# 7. Try to connect to external IP from inside (this should fail if firewall blocks)
echo ""
echo "7. Testing connection to external IP from inside..."
timeout 5 curl -v http://213.173.105.83:8080/health 2>&1 | head -10

# 8. Check RunPod specific networking
echo ""
echo "8. Checking RunPod networking..."
echo "Container IP: $(hostname -i 2>/dev/null || echo 'unknown')"
echo "Gateway: $(ip route | grep default | awk '{print $3}' 2>/dev/null || echo 'unknown')"

echo ""
echo "========================================"
echo "Diagnostic complete. Check results above."
