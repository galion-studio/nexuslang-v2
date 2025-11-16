#!/bin/bash
# ============================================
# GALION CLEANUP SCRIPT
# ============================================
# Clean up Docker containers, images, and volumes

set -e

echo "🧹 Cleaning up Galion development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Stop and remove containers
print_status "Stopping and removing containers..."
if command -v docker-compose &> /dev/null; then
    docker-compose down --volumes --remove-orphans
else
    docker compose down --volumes --remove-orphans
fi

# Remove unused images
print_status "Removing unused Docker images..."
docker image prune -f

# Remove unused volumes
print_status "Removing unused Docker volumes..."
docker volume prune -f

# Remove unused networks
print_status "Removing unused Docker networks..."
docker network prune -f

# Clean up generated files
print_status "Cleaning up generated files..."
rm -rf logs/
rm -rf nginx/sites-enabled/
rm -rf ssl/
rm -rf monitoring/

# Keep .env file but warn about it
if [[ -f ".env" ]]; then
    print_warning ".env file preserved (contains your API keys)"
fi

print_success "Cleanup complete!"
echo ""
echo "🧹 Removed:"
echo "   - All Docker containers"
echo "   - All Docker volumes"
echo "   - Generated configuration files"
echo "   - Log files"
echo ""
echo "💾 Preserved:"
echo "   - .env file (your API keys)"
echo "   - Source code"
echo "   - Configuration templates"
echo ""
echo "🚀 To start fresh:"
echo "   ./scripts/setup-dev.sh"

