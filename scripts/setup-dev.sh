#!/bin/bash
# ============================================
# GALION DEVELOPMENT SETUP SCRIPT
# ============================================
# Quick setup for local development environment

set -e

echo "🚀 Setting up Galion Voice API for Development..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
    print_warning "Please edit .env file with your actual API keys!"
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p logs
mkdir -p nginx/sites-enabled
mkdir -p ssl
mkdir -p monitoring

# Copy nginx configuration
print_status "Setting up nginx configuration..."
if [[ -f "nginx.conf" ]]; then
    cp nginx.conf nginx/nginx.conf
fi

# Enable nginx sites
if [[ -d "nginx/sites-available" ]]; then
    for site in nginx/sites-available/*.conf; do
        if [[ -f "$site" ]]; then
            ln -sf "../../../$site" "nginx/sites-enabled/$(basename "$site")"
        fi
    done
fi

# Start services
print_status "Starting services with Docker Compose..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

# Wait for services to start
print_status "Waiting for services to start..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check Redis
if docker ps | grep -q galion-redis; then
    print_success "Redis is running"
else
    print_warning "Redis may not be running"
fi

# Check Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend is healthy"
else
    print_warning "Backend may not be ready yet"
fi

# Check Frontend
if curl -f http://localhost:3003 > /dev/null 2>&1; then
    print_success "Frontend is running"
else
    print_warning "Frontend may not be ready yet"
fi

echo ""
echo -e "${GREEN}🎉 Development environment setup complete!${NC}"
echo ""
echo "📡 Services:"
echo "   - Frontend: http://localhost:3003"
echo "   - Backend: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health: http://localhost:8000/health"
echo ""
echo "🔧 Development commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart backend: docker-compose restart backend"
echo "   - Restart frontend: docker-compose restart frontend"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env file with your API keys"
echo "   2. Test the voice interface at http://localhost:3003"
echo "   3. Check API documentation at http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}⚠️  Remember to add your API keys to the .env file!${NC}"
echo ""
echo -e "${GREEN}🚀 Happy coding!${NC}"

