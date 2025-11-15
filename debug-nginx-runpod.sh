#!/bin/bash
# Debug nginx configuration on RunPod

echo "🔍 Nginx Debug for RunPod"
echo "========================="

# Check main nginx.conf
echo "1. Main nginx.conf:"
echo "------------------"
cat /etc/nginx/nginx.conf | grep -A 10 -B 5 "include\|listen\|server"

echo ""
echo "2. Sites-enabled directory:"
echo "---------------------------"
ls -la /etc/nginx/sites-enabled/

echo ""
echo "3. Our configuration file:"
echo "--------------------------"
head -30 /etc/nginx/sites-enabled/galion-platform

echo ""
echo "4. Check if nginx is using systemd:"
echo "------------------------------------"
ps aux | head -5

echo ""
echo "5. Check nginx process details:"
echo "--------------------------------"
ps aux | grep nginx | head -3

echo ""
echo "6. Check what config file nginx is using:"
echo "------------------------------------------"
cat /proc/$(pgrep nginx | head -1)/cmdline | tr '\0' '\n'

echo ""
echo "7. Try to reload nginx manually:"
echo "---------------------------------"
nginx -s reload 2>&1 || echo "Reload failed - nginx might need restart"

echo ""
echo "========================="
echo "Debug complete"
echo "========================="
