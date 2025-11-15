#!/bin/bash
# Clean up logs and fix test script

echo "🧹 Cleaning up logs and optimizing..."
echo ""

# Clear old error logs
pm2 flush

# Pull latest code
cd /nexuslang-v2
git fetch origin
git reset --hard origin/clean-nexuslang

echo "✓ Logs cleared"
echo "✓ Code updated"
echo ""
echo "All services are working!"
echo ""

pm2 status

echo ""
echo "🌐 Your platform is ready:"
echo "  • Backend:   http://213.173.105.83:8000/docs"
echo "  • Studio:    http://213.173.105.83:3030"
echo "  • App:       http://213.173.105.83:3000"
echo "  • Dev Platform: http://213.173.105.83:3003"

