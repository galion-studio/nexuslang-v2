#!/bin/bash
# Final fix deployment - just pull and restart

echo "🔧 Final Fix Deployment"
echo "======================"

cd /nexuslang-v2

# Pull latest changes
echo "Pulling latest fixes..."
git pull origin clean-nexuslang

# Restart services (they should pick up the new code)
echo "Restarting services..."
pm2 restart galion-app
pm2 restart developer-platform

echo "Waiting for services..."
sleep 5

# Test
echo "Testing services..."
echo -n "Galion App: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

echo -n "Developer Platform: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3003

echo ""
echo "Checking logs..."
pm2 logs galion-app --lines 3 --nostream | grep -i error || echo "Galion App: No errors"
pm2 logs developer-platform --lines 3 --nostream | grep -i error || echo "Developer Platform: No errors"

echo ""
echo "✅ Final fixes deployed!"
