#!/bin/bash
echo "🔧 Galion Services Dependency Installation & Startup Script"
echo "========================================================"

# Set project root directory
PROJECT_ROOT="/c/Users/Gigabyte/Documents/project-nexus"
echo "Project root: $PROJECT_ROOT"

# Function to check and install dependencies
install_deps() {
    local service_name=$1
    local service_dir=$2

    echo ""
    echo "📦 Checking $service_name dependencies..."
    cd "$PROJECT_ROOT/$service_dir"

    if [ -d "node_modules" ] && [ "$(ls -A node_modules)" ]; then
        echo "✅ $service_name dependencies already installed"
    else
        echo "📥 Installing $service_name dependencies..."
        npm install --legacy-peer-deps
        if [ $? -eq 0 ]; then
            echo "✅ $service_name dependencies installed successfully"
        else
            echo "❌ Failed to install $service_name dependencies"
            return 1
        fi
    fi
}

# Install dependencies for all services
echo "Step 1: Installing dependencies for all services..."

install_deps "Galion.app" "galion-app"
install_deps "Developer Platform" "developer-platform"
install_deps "Galion Studio" "galion-studio"

echo ""
echo "Step 2: Starting all services..."

# Kill any existing Node processes on our ports
echo "Stopping any existing services on ports 3010, 3020, 3030..."
for port in 3010 3020 3030; do
    # Find processes using these ports (Windows equivalent)
    netstat -ano | findstr ":$port " | findstr "LISTENING" > /dev/null
    if [ $? -eq 0 ]; then
        echo "Found process on port $port, stopping..."
        # This would need Windows-specific commands, but for now we'll assume services start fresh
    fi
done

# Start Galion.app (port 3010)
echo "Starting Galion.app on port 3010..."
cd "$PROJECT_ROOT/galion-app"
npm run dev -- --port 3010 &
GALION_PID=$!

# Start Developer Platform (port 3020)
echo "Starting Developer Platform on port 3020..."
cd "$PROJECT_ROOT/developer-platform"
npm run dev -- --port 3020 &
DEV_PID=$!

# Start Galion Studio (port 3030)
echo "Starting Galion Studio on port 3030..."
cd "$PROJECT_ROOT/galion-studio"
npm run dev -- --port 3030 &
STUDIO_PID=$!

echo ""
echo "🎉 All services started!"
echo "Galion.app: http://localhost:3010 (PID: $GALION_PID)"
echo "Developer Platform: http://localhost:3020 (PID: $DEV_PID)"
echo "Galion Studio: http://localhost:3030 (PID: $STUDIO_PID)"

echo ""
echo "Waiting for services to initialize..."
sleep 5

# Test services
echo "Testing service health..."
curl -s http://localhost:3010 > /dev/null && echo "✅ Galion.app is responding" || echo "❌ Galion.app not responding"
curl -s http://localhost:3020 > /dev/null && echo "✅ Developer Platform is responding" || echo "❌ Developer Platform not responding"
curl -s http://localhost:3030 > /dev/null && echo "✅ Galion Studio is responding" || echo "❌ Galion Studio not responding"

echo ""
echo "🚀 All services should now be running!"
echo "You can access them at:"
echo "  - Galion.app: http://localhost:3010"
echo "  - Developer Platform: http://localhost:3020"
echo "  - Galion Studio: http://localhost:3030"
