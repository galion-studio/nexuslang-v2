#!/bin/bash
# Force deploy fixes with clean rebuild

echo "🔧 FORCE DEPLOY FIXES - Clean Rebuild"
echo "====================================="

cd /nexuslang-v2

# Pull latest changes
echo "1. Pulling latest changes..."
git pull origin clean-nexuslang

# Clean Next.js caches and rebuild
echo "2. Cleaning and rebuilding galion-app..."
cd galion-app
rm -rf .next
npm install
npm run build

echo "3. Cleaning and rebuilding developer-platform..."
cd ../developer-platform
rm -rf .next
npm install
npm run build
cd ..

# Force restart services
echo "4. Force restarting services..."
pm2 delete galion-app developer-platform 2>/dev/null || true

# Start fresh
echo "5. Starting services fresh..."
cd galion-app
pm2 start npm --name galion-app -- run dev -- -p 3000
cd ../developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003
cd ..

pm2 save

echo "6. Waiting for services to start..."
sleep 10

# Test services
echo "7. Testing services..."
echo -n "Galion App: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

echo -n "Developer Platform: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3003

echo ""
echo "8. Checking logs..."
pm2 logs galion-app --lines 3 --nostream | grep -i error || echo "No errors in galion-app logs"
pm2 logs developer-platform --lines 3 --nostream | grep -i error || echo "No errors in developer-platform logs"

echo ""
echo "✅ Force deployment complete!"
echo "Check the logs above for any remaining issues."
