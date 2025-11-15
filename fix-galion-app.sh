#!/bin/bash
# ============================================
# Fix Galion App - Diagnostic and Repair Script
# ============================================

echo "🔧 GALION APP FIX SCRIPT"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd /nexuslang-v2/galion-app || exit 1

# Step 1: Check current status
echo -e "${BLUE}Step 1: Checking current status...${NC}"
pm2 describe galion-app > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Service exists${NC}"
    pm2 stop galion-app
else
    echo -e "${YELLOW}⚠ Service not in PM2${NC}"
fi
echo ""

# Step 2: Check directory structure
echo -e "${BLUE}Step 2: Checking directory structure...${NC}"
if [ -d "app" ]; then
    echo -e "${GREEN}✓ app/ directory exists${NC}"
    ls -la app/ | head -10
else
    echo -e "${RED}✗ app/ directory missing!${NC}"
fi
echo ""

# Step 3: Check package.json
echo -e "${BLUE}Step 3: Checking package.json...${NC}"
if [ -f "package.json" ]; then
    echo -e "${GREEN}✓ package.json exists${NC}"
    cat package.json | grep -A 5 "dependencies"
else
    echo -e "${RED}✗ package.json missing!${NC}"
fi
echo ""

# Step 4: Install ALL missing dependencies
echo -e "${BLUE}Step 4: Installing all dependencies...${NC}"
npm install --silent

# Install commonly needed packages
echo -e "${BLUE}  Installing additional packages...${NC}"
npm install lucide-react @radix-ui/react-slot class-variance-authority clsx tailwind-merge next react react-dom --silent

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 5: Check for lib directory and create if missing
echo -e "${BLUE}Step 5: Checking lib utilities...${NC}"
if [ ! -d "lib" ]; then
    echo -e "${YELLOW}⚠ Creating lib directory...${NC}"
    mkdir -p lib
fi

# Create utils.ts if missing
if [ ! -f "lib/utils.ts" ]; then
    echo -e "${YELLOW}⚠ Creating lib/utils.ts...${NC}"
    cat > lib/utils.ts << 'UTILS_EOF'
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
UTILS_EOF
    echo -e "${GREEN}✓ Created lib/utils.ts${NC}"
fi
echo ""

# Step 6: Clear Next.js cache
echo -e "${BLUE}Step 6: Clearing Next.js cache...${NC}"
rm -rf .next
echo -e "${GREEN}✓ Cache cleared${NC}"
echo ""

# Step 7: Restart service
echo -e "${BLUE}Step 7: Restarting service...${NC}"
pm2 delete galion-app 2>/dev/null || true
pm2 start npm --name galion-app -- run dev -- -p 3000
pm2 save
echo ""

# Step 8: Wait and check
echo -e "${BLUE}Step 8: Waiting for service to start...${NC}"
sleep 5
echo ""

# Step 9: Test
echo -e "${BLUE}Step 9: Testing service...${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ SUCCESS! Galion App is working!${NC}"
    echo -e "${GREEN}   HTTP Status: $HTTP_CODE${NC}"
elif [ "$HTTP_CODE" = "500" ]; then
    echo -e "${YELLOW}⚠ Still getting 500 error${NC}"
    echo -e "${YELLOW}   Showing last 30 lines of error log:${NC}"
    echo ""
    pm2 logs galion-app --lines 30 --nostream --err
else
    echo -e "${RED}✗ Service not responding (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo "============================================"
echo -e "${BLUE}Final Status:${NC}"
pm2 status
echo "============================================"
echo ""
echo -e "${BLUE}To view live logs:${NC} pm2 logs galion-app"
echo -e "${BLUE}To restart:${NC} pm2 restart galion-app"
echo ""

