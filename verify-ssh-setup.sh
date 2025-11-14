#!/bin/bash
# Verify SSH key setup on RunPod server

echo "🔍 Verifying SSH Key Setup"
echo "=========================="

echo "1. Checking .ssh directory..."
ls -la ~/.ssh/

echo ""
echo "2. Checking authorized_keys..."
if [ -f ~/.ssh/authorized_keys ]; then
    echo "✅ authorized_keys exists"
    echo "Contents:"
    cat ~/.ssh/authorized_keys
else
    echo "❌ authorized_keys not found"
fi

echo ""
echo "3. Checking permissions..."
ls -la ~/.ssh/authorized_keys 2>/dev/null || echo "File not found"

echo ""
echo "4. Testing SSH service..."
systemctl status ssh 2>/dev/null || service ssh status 2>/dev/null || echo "SSH service status unknown"

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 NEXT: Run these commands from your LOCAL machine:"
echo ""
echo "   # Test SSH connection:"
echo "   ssh root@213.173.105.83"
echo ""
echo "   # Create tunnel:"
echo "   ssh -L 8080:localhost:36277 root@213.173.105.83 -N"
echo ""
echo "   # Then access API at:"
echo "   http://localhost:8080"
