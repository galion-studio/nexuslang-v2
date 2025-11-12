#!/bin/bash
# ===============================================
# NexusLang v2 Instant Deployment for RunPod
# ===============================================
# One-command deployment that completes in under 2 minutes
# Uses Docker with pre-built dependencies

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║       NexusLang v2 - Instant RunPod Deployment           ║"
echo "║              Deploy in Under 2 Minutes!                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/v2/backend"

# Run Python recovery script (handles everything)
echo -e "${CYAN}🚀 Starting recovery process...${NC}"
echo ""

if [ -f "recovery.py" ]; then
    python3 recovery.py "$@"
else
    echo -e "${RED}❌ recovery.py not found!${NC}"
    echo "Please ensure you're in the correct directory"
    exit 1
fi

