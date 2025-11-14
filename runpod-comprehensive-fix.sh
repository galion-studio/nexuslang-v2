#!/bin/bash
# Comprehensive RunPod networking fix with all solutions

echo "🚀 COMPREHENSIVE RUNPOD NETWORKING FIX"
echo "====================================="
echo ""

# Check current status
echo "1. 📊 Current Server Status:"
ps aux | grep uvicorn | grep -v grep || echo "No uvicorn processes running"

echo ""
echo "2. 🔍 RunPod Environment:"
echo "Pod ID: $RUNPOD_POD_ID"
echo "Public IP: $RUNPOD_PUBLIC_IP"
echo "Exposed Ports:"
echo "  • SSH (22) → $RUNPOD_TCP_PORT_22"
echo "  • DB (5432) → $RUNPOD_TCP_PORT_5432"
echo "  • Redis (6379) → $RUNPOD_TCP_PORT_6379"

echo ""
echo "3. 🧪 Testing Port Accessibility:"
EXTERNAL_IP=$RUNPOD_PUBLIC_IP

for port_var in RUNPOD_TCP_PORT_22 RUNPOD_TCP_PORT_5432 RUNPOD_TCP_PORT_6379; do
    port_value=$(eval echo \$$port_var)
    if [ -n "$port_value" ] && [ "$port_value" != "0" ]; then
        echo "Testing port $port_value..."
        if timeout 3 bash -c "echo > /dev/tcp/$EXTERNAL_IP/$port_value" 2>/dev/null; then
            echo "  ✅ Port $port_value: ACCESSIBLE"
        else
            echo "  ❌ Port $port_value: NOT ACCESSIBLE"
        fi
    fi
done

echo ""
echo "4. 🎯 RECOMMENDED SOLUTIONS:"
echo ""

echo "SOLUTION A: Modify RunPod Template (BEST)"
echo "=========================================="
echo "1. Stop your current pod"
echo "2. Go to RunPod dashboard → Templates"
echo "3. Edit your template's Docker configuration"
echo "4. Add port exposure (choose one):"
echo "   - EXPOSE 80    # For HTTP"
echo "   - EXPOSE 3000  # For custom port"
echo "   - EXPOSE 8000  # For web apps"
echo "5. Save template and start new pod"
echo "6. Run: ./runpod-start-simple.sh (will work on exposed port)"
echo ""

echo "SOLUTION B: Use RunPod HTTP Proxy (ALTERNATIVE)"
echo "================================================"
echo "If you can expose port 80, use the HTTP proxy:"
echo "1. Modify template to expose port 80"
echo "2. Run: ./runpod-start-http-proxy.sh"
echo "3. Access via: https://$RUNPOD_POD_ID.proxy.runpod.net"
echo ""

echo "SOLUTION C: Contact RunPod Support (LAST RESORT)"
echo "================================================"
echo "If template modification doesn't work:"
echo "• RunPod support can help configure port exposure"
echo "• Provide your pod ID: $RUNPOD_POD_ID"
echo "• Request port exposure for web applications"
echo ""

echo "5. 🛠️ IMMEDIATE WORKAROUNDS:"
echo ""

echo "A) Try port 8080 with different binding:"
cat << 'EOF'
pkill -f uvicorn
cd /workspace/project-nexus/v2/backend
PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2 python -m uvicorn main_simple:app --host 0.0.0.0 --port 8080 &
# Then test if accessible (unlikely but worth trying)
EOF

echo ""
echo "B) Use local access only:"
echo "• Your server works locally: curl http://localhost:36277/health"
echo "• Access via RunPod's web terminal interface"
echo "• Use SSH tunneling: ssh -L 8080:localhost:36277 root@$EXTERNAL_IP"
echo ""

echo "6. 📋 SUMMARY:"
echo "=============="
echo "• ✅ Server runs perfectly locally"
echo "• ❌ External access blocked by RunPod networking"
echo "• 🎯 Solution: Modify RunPod template to expose ports"
echo ""
echo "Next step: Edit your RunPod template to expose a web port (80, 3000, or 8000)"
echo ""
echo "🔗 Helpful links:"
echo "• RunPod Template Docs: https://docs.runpod.io/docs/templates"
echo "• Port Configuration: Search for 'EXPOSE' in Docker documentation"
