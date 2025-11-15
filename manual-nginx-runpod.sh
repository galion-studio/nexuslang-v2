#!/bin/bash
# Manual nginx management for RunPod

echo "🔧 Manual Nginx Management for RunPod"
echo "====================================="

# Check if nginx is running
echo "Checking nginx status..."
ps aux | grep nginx

# Try to find nginx binary
echo ""
echo "Finding nginx binary..."
which nginx
ls -la /usr/sbin/nginx 2>/dev/null || echo "Not in /usr/sbin"
ls -la /usr/bin/nginx 2>/dev/null || echo "Not in /usr/bin"

# Check nginx configuration
echo ""
echo "Testing nginx configuration..."
nginx -t 2>/dev/null || echo "nginx command not found in PATH"

# Try different nginx paths
echo ""
echo "Trying alternative nginx paths..."
/usr/sbin/nginx -t 2>/dev/null || echo "Not in /usr/sbin"
/usr/bin/nginx -t 2>/dev/null || echo "Not in /usr/bin"

# Check if nginx is managed by supervisor or runit
echo ""
echo "Checking for alternative init systems..."
ls -la /etc/init.d/nginx 2>/dev/null || echo "No init.d script"
ls -la /etc/service/nginx 2>/dev/null || echo "No runit service"

# Try to restart nginx manually
echo ""
echo "Attempting manual nginx restart..."
pkill -f nginx 2>/dev/null || echo "No nginx processes to kill"

# Start nginx manually
echo "Starting nginx manually..."
nginx 2>/dev/null || /usr/sbin/nginx 2>/dev/null || /usr/bin/nginx 2>/dev/null || echo "Cannot start nginx - binary not found"

# Check if it started
echo ""
echo "Checking if nginx started..."
ps aux | grep nginx

echo ""
echo "====================================="
echo "Manual nginx management complete"
echo "====================================="
