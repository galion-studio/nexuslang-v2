#!/bin/bash
# Check what ports RunPod exposes

echo "🔍 Checking RunPod Exposed Ports"
echo "=================================="

echo "RunPod Environment Variables:"
env | grep RUNPOD_TCP_PORT || echo "No TCP port mappings found"

echo ""
echo "Current listening ports:"
ss -tlnp | grep LISTEN

echo ""
echo "Testing connectivity to exposed ports..."

# Test the mapped ports
if [ -n "$RUNPOD_TCP_PORT_22" ]; then
    echo "Testing SSH port mapping: $RUNPOD_TCP_PORT_22"
    timeout 3 nc -zv 213.173.105.83 $RUNPOD_TCP_PORT_22 2>/dev/null && echo "✅ SSH port accessible" || echo "❌ SSH port not accessible"
fi

if [ -n "$RUNPOD_TCP_PORT_5432" ]; then
    echo "Testing port 5432 mapping: $RUNPOD_TCP_PORT_5432"
    timeout 3 nc -zv 213.173.105.83 $RUNPOD_TCP_PORT_5432 2>/dev/null && echo "✅ Port 5432 accessible" || echo "❌ Port 5432 not accessible"
fi

echo ""
echo "🔧 RunPod Port Exposure Rules:"
echo "• Ports must be explicitly exposed in the pod template"
echo "• Common exposed ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)"
echo "• Custom ports need template configuration"
echo ""
echo "💡 Solutions:"
echo "1. Use port 80 with nginx proxy (recommended)"
echo "2. Configure your RunPod template to expose port 3000"
echo "3. Use a pre-exposed port from the mappings above"
