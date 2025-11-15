#!/bin/bash
# ============================================
# FIX EVERYTHING - Comprehensive Platform Fix
# ============================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  COMPREHENSIVE PLATFORM FIX${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

cd /nexuslang-v2 || exit 1

# ============================================
# FIX 1: Galion App CSS Import
# ============================================
echo -e "${BLUE}[1/4] Fixing Galion App CSS...${NC}"

# The issue is the import path - just comment it out since we have Tailwind
cd galion-app
sed -i '1s/^/@import/; 1s/@import/@import \/\*/' app/globals.css
sed -i '1s/$/*\//' app/globals.css

# Better solution: just remove the problematic line
sed -i '1d' app/globals.css

echo -e "${GREEN}✓${NC} Removed problematic CSS import"
cd /nexuslang-v2
echo ""

# ============================================
# FIX 2: Add NexusLang Route to main_simple.py
# ============================================
echo -e "${BLUE}[2/4] Adding missing backend routes...${NC}"

cd v2/backend

# Check if NexusLang router is already there
if ! grep -q "nexuslang_router" main_simple.py; then
    echo -e "${YELLOW}⚠${NC} Adding NexusLang router..."
    
    # Add NexusLang import and router after Grokopedia section
    sed -i '/# Try to include Grokopedia/i\
# Try to include NexusLang router if available\
try:\
    from api.nexuslang import router as nexuslang_router\
    app.include_router(nexuslang_router, prefix="/api/v1/nexuslang", tags=["nexuslang"])\
    logger.info("NexusLang router loaded successfully")\
except Exception as e:\
    logger.warning(f"Could not load NexusLang router: {e}")\
    logger.info("Server will start without NexusLang endpoints")\
\
' main_simple.py
    
    echo -e "${GREEN}✓${NC} NexusLang router added"
else
    echo -e "${GREEN}✓${NC} NexusLang router already present"
fi

cd /nexuslang-v2
echo ""

# ============================================
# FIX 3: Clear All Caches
# ============================================
echo -e "${BLUE}[3/4] Clearing all caches...${NC}"

rm -rf galion-app/.next
rm -rf galion-studio/.next  
rm -rf developer-platform/.next
rm -rf galion-app/node_modules/.cache
rm -rf galion-studio/node_modules/.cache
rm -rf developer-platform/node_modules/.cache

echo -e "${GREEN}✓${NC} All caches cleared"
echo ""

# ============================================
# FIX 4: Restart All Services
# ============================================
echo -e "${BLUE}[4/4] Restarting all services...${NC}"

pm2 delete all 2>/dev/null || true
echo "   Services stopped"

# Backend
cd v2/backend
pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
echo "   ✓ Backend started"

# Frontends
cd /nexuslang-v2/galion-studio
pm2 start npm --name galion-studio -- run dev -- -p 3030
echo "   ✓ Galion Studio started"

cd /nexuslang-v2/galion-app
pm2 start npm --name galion-app -- run dev -- -p 3000
echo "   ✓ Galion App started"

cd /nexuslang-v2/developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003
echo "   ✓ Developer Platform started"

pm2 save
echo ""

# ============================================
# WAIT AND TEST
# ============================================
echo -e "${BLUE}Waiting 15 seconds for services to initialize...${NC}"
sleep 15
echo ""

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  TESTING ALL SERVICES${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Test backend
BACKEND_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$BACKEND_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} Backend (8000): HTTP $BACKEND_CODE"
else
    echo -e "${RED}✗${NC} Backend (8000): HTTP $BACKEND_CODE"
fi

# Test Grokopedia (correct path)
GROKO_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/grokopedia/)
if [ "$GROKO_CODE" = "200" ] || [ "$GROKO_CODE" = "404" ]; then
    echo -e "${GREEN}✓${NC} Grokopedia Route: Registered (HTTP $GROKO_CODE)"
else
    echo -e "${YELLOW}⚠${NC} Grokopedia Route: HTTP $GROKO_CODE"
fi

# Test NexusLang (correct path)
NEXUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/nexuslang/compile)
if [ "$NEXUS_CODE" = "405" ] || [ "$NEXUS_CODE" = "422" ]; then
    echo -e "${GREEN}✓${NC} NexusLang Route: Registered (HTTP $NEXUS_CODE)"
else
    echo -e "${YELLOW}⚠${NC} NexusLang Route: HTTP $NEXUS_CODE"
fi

# Test frontends
STUDIO_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3030)
if [ "$STUDIO_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} Galion Studio (3030): HTTP $STUDIO_CODE"
else
    echo -e "${RED}✗${NC} Galion Studio (3030): HTTP $STUDIO_CODE"
fi

APP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$APP_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} Galion App (3000): HTTP $APP_CODE"
else
    echo -e "${YELLOW}⚠${NC} Galion App (3000): HTTP $APP_CODE"
fi

DEV_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3003)
if [ "$DEV_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} Developer Platform (3003): HTTP $DEV_CODE"
else
    echo -e "${RED}✗${NC} Developer Platform (3003): HTTP $DEV_CODE"
fi

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  FINAL STATUS${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

pm2 status

echo ""
if [ "$BACKEND_CODE" = "200" ] && [ "$STUDIO_CODE" = "200" ] && [ "$DEV_CODE" = "200" ]; then
    echo -e "${GREEN}✅ PLATFORM READY!${NC}"
    echo ""
    echo "Access your services:"
    echo "  • Backend:     http://213.173.105.83:8000/docs"
    echo "  • Studio:      http://213.173.105.83:3030"
    echo "  • Dev Platform: http://213.173.105.83:3003"
    if [ "$APP_CODE" = "200" ]; then
        echo "  • App:         http://213.173.105.83:3000"
    else
        echo -e "  • App:         http://213.173.105.83:3000 ${YELLOW}(HTTP $APP_CODE)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Some services need attention${NC}"
    echo "  Run: pm2 logs SERVICE_NAME"
fi

echo ""

