#!/bin/bash
# Force clean rebuild of all Next.js applications

echo "🔧 FORCE CLEAN REBUILD - Complete Cache Clear"
echo "=============================================="

cd /nexuslang-v2

# Pull latest changes
echo "1. Pulling latest changes..."
git pull origin clean-nexuslang

# Stop services
echo "2. Stopping services..."
pm2 stop galion-app developer-platform 2>/dev/null || true

# Clean and rebuild galion-app
echo "3. Rebuilding galion-app..."
cd galion-app
rm -rf .next node_modules/.cache
npm install --silent
npm run build
cd ..

# Clean and rebuild developer-platform
echo "4. Rebuilding developer-platform..."
cd developer-platform
rm -rf .next node_modules/.cache
npm install --silent
npm run build
cd ..

# Force restart services
echo "5. Force restarting services..."
pm2 delete galion-app developer-platform 2>/dev/null || true

# Start fresh
echo "6. Starting fresh services..."
cd galion-app
pm2 start npm --name galion-app -- run dev -- -p 3000
cd ../developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003
cd ..

pm2 save

echo "7. Waiting for services..."
sleep 15

# Test services
echo "8. Testing services..."
echo -n "Galion App: "
timeout 10 curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

echo -n "Developer Platform: "
timeout 10 curl -s -o /dev/null -w "%{http_code}" http://localhost:3003

echo ""
echo "9. Checking logs..."
pm2 logs galion-app --lines 5 --nostream | grep -i error || echo "Galion App: No errors"
pm2 logs developer-platform --lines 5 --nostream | grep -i error || echo "Developer Platform: No errors"

echo ""
echo "✅ Force clean rebuild complete!"
echo "All caches cleared and services rebuilt from scratch."
