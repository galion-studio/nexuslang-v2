#!/bin/bash
# Test which RunPod ports are actually accessible externally

echo "🧪 Testing RunPod Port Accessibility"
echo "==================================="

EXTERNAL_IP=213.173.105.83
EXPOSED_PORTS=("$RUNPOD_TCP_PORT_22" "$RUNPOD_TCP_PORT_5432" "$RUNPOD_TCP_PORT_6379")

echo "Testing external access to exposed ports:"
echo "External IP: $EXTERNAL_IP"
echo ""

for port in "${EXPOSED_PORTS[@]}"; do
    if [ -n "$port" ] && [ "$port" != "0" ]; then
        echo "Testing port $port..."
        # Use timeout and nc to test connectivity
        if timeout 5 bash -c "echo > /dev/tcp/$EXTERNAL_IP/$port" 2>/dev/null; then
            echo "✅ Port $port: ACCESSIBLE"
        else
            echo "❌ Port $port: NOT ACCESSIBLE"
        fi
        echo ""
    fi
done

echo "🔍 Port Status Summary:"
echo "• Port 22 ($RUNPOD_TCP_PORT_22): SSH access"
echo "• Port 5432 ($RUNPOD_TCP_PORT_5432): Database/Web service"
echo "• Port 6379 ($RUNPOD_TCP_PORT_6379): Redis/Cache service"
echo ""
echo "💡 Recommendation: Try binding your web server to port $RUNPOD_TCP_PORT_5432"
echo "   This is commonly used for web applications in containerized environments."
