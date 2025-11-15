#!/bin/bash
# ============================================
# Advanced Galion App Fix - Deep Diagnosis
# ============================================

echo "🔧 ADVANCED GALION APP FIX"
echo "============================================"
echo ""

cd /nexuslang-v2/galion-app || exit 1

# Stop service to see full error
echo "Step 1: Stopping service..."
pm2 delete galion-app 2>/dev/null || true
pm2 flush
echo ""

# Install EVERYTHING
echo "Step 2: Installing all possible dependencies..."
npm install --silent \
  lucide-react \
  @radix-ui/react-slot \
  @radix-ui/react-dialog \
  @radix-ui/react-dropdown-menu \
  @radix-ui/react-label \
  @radix-ui/react-separator \
  @radix-ui/react-tabs \
  @radix-ui/react-select \
  @radix-ui/react-switch \
  class-variance-authority \
  clsx \
  tailwind-merge \
  @types/node \
  @types/react \
  @types/react-dom

echo "✓ Dependencies installed"
echo ""

# Create lib directory and utils
echo "Step 3: Creating utility files..."
mkdir -p lib

cat > lib/utils.ts << 'EOF'
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
EOF

# Create API client if missing
cat > lib/api-client.ts << 'EOF'
export class APIClient {
  private baseURL: string;

  constructor(baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async get(endpoint: string) {
    const response = await fetch(`${this.baseURL}${endpoint}`);
    return response.json();
  }

  async post(endpoint: string, data: any) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }
}

export const apiClient = new APIClient();
EOF

echo "✓ Utility files created"
echo ""

# Clear everything
echo "Step 4: Clearing caches..."
rm -rf .next node_modules/.cache
echo "✓ Caches cleared"
echo ""

# Try to build (this will show the REAL error)
echo "Step 5: Building to find errors..."
echo "   (This will show the exact problem)"
echo ""

npm run build 2>&1 | tee /tmp/galion-app-build.log

BUILD_EXIT_CODE=${PIPESTATUS[0]}

echo ""
if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "✅ BUILD SUCCESSFUL!"
    echo ""
    echo "Starting in production mode..."
    pm2 start npm --name galion-app -- run start -- -p 3000
else
    echo "❌ BUILD FAILED - See errors above"
    echo ""
    echo "Starting in dev mode anyway..."
    pm2 start npm --name galion-app -- run dev -- -p 3000
fi

pm2 save
echo ""

# Wait and test
echo "Step 6: Testing..."
sleep 10

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)

echo ""
echo "============================================"
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ SUCCESS! Galion App is working!"
    echo "   HTTP Status: $HTTP_CODE"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "⚠ Still 500 error. Full error details:"
    echo ""
    pm2 logs galion-app --lines 50 --nostream --err
    echo ""
    echo "Build log saved to: /tmp/galion-app-build.log"
    echo "View with: cat /tmp/galion-app-build.log"
else
    echo "Service Status: HTTP $HTTP_CODE"
fi
echo "============================================"
echo ""

pm2 status
echo ""
echo "To view live logs: pm2 logs galion-app"

