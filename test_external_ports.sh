#!/bin/bash
echo "🌐 Testing External Port Access"
echo "=============================="

# Test port 3000
echo ""
echo "Testing port 3000:"
curl -s --max-time 5 http://213.173.105.83:3000/health && echo " ✅ Port 3000 works externally!" || echo " ❌ Port 3000 blocked"

# Test port 5000
echo ""
echo "Testing port 5000:"
curl -s --max-time 5 http://213.173.105.83:5000/health && echo " ✅ Port 5000 works externally!" || echo " ❌ Port 5000 blocked"

# Test port 8080 (original)
echo ""
echo "Testing port 8080:"
curl -s --max-time 5 http://213.173.105.83:8080/health && echo " ✅ Port 8080 works externally!" || echo " ❌ Port 8080 blocked"

echo ""
echo "🎯 Next steps:"
echo "1. Test the working port URLs in your browser"
echo "2. If none work, configure RunPod port exposure"
echo "3. Update your application to use the working port"
