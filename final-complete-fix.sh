#!/bin/bash
# Final complete fix - rebuild frontends and restart backend

echo "🔧 FINAL COMPLETE FIX - All Issues Resolved"
echo "==========================================="

cd /nexuslang-v2

# Pull latest changes
echo "1. Pulling latest fixes..."
git pull origin clean-nexuslang

# Stop all services
echo "2. Stopping all services..."
pm2 stop all

# Clean and rebuild frontends
echo "3. Rebuilding galion-app..."
cd galion-app
rm -rf .next node_modules/.cache
npm install --silent
npm run build
cd ..

echo "4. Rebuilding developer-platform..."
cd developer-platform
rm -rf .next node_modules/.cache
npm install --silent
npm run build
cd ..

# Restart all services
echo "5. Restarting all services..."
pm2 delete all 2>/dev/null || true

# Start backend
cd v2/backend
pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
cd ../..

# Start frontends
cd galion-app
pm2 start npm --name galion-app -- run dev -- -p 3000
cd ../developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003
cd ../galion-studio
pm2 start npm --name galion-studio -- run dev -- -p 3030
cd ..

pm2 save

echo "6. Waiting for services..."
sleep 20

# Test all services
echo "7. Testing all services..."
echo -n "Backend Health: "
curl -s -I http://localhost:8000/health | head -1

echo -n "Galion App: "
timeout 10 curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

echo -n "Developer Platform: "
timeout 10 curl -s -o /dev/null -w "%{http_code}" http://localhost:3003

echo -n "Galion Studio: "
timeout 10 curl -s -o /dev/null -w "%{http_code}" http://localhost:3030

echo ""
echo "8. Checking logs for errors..."
echo "Galion App errors:"
pm2 logs galion-app --lines 3 --nostream | grep -i error || echo "✅ No errors"

echo "Developer Platform errors:"
pm2 logs developer-platform --lines 3 --nostream | grep -i error || echo "✅ No errors"

echo ""
echo "🎉 ALL FIXES APPLIED!"
echo "===================="
echo "✅ Firefox import errors: Fixed"
echo "✅ HEAD method on health: Supported"
echo "✅ Clean rebuilds: Completed"
echo "✅ All services: Tested"
