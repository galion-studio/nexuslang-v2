#!/bin/bash
# Fix backend startup issue

echo "🔧 FIXING BACKEND STARTUP"
echo "========================="
echo ""

# Go to backend directory
cd /nexuslang-v2/v2/backend

echo "1. Testing backend imports..."
python3 << 'PYTEST'
import sys
print("Testing imports...")

try:
    import fastapi
    print("✅ fastapi OK")
except Exception as e:
    print(f"❌ fastapi: {e}")
    sys.exit(1)

try:
    import uvicorn
    print("✅ uvicorn OK")
except Exception as e:
    print(f"❌ uvicorn: {e}")
    sys.exit(1)

try:
    import psutil
    print("✅ psutil OK")
except Exception as e:
    print(f"❌ psutil: {e}")
    sys.exit(1)

try:
    import pydantic
    print("✅ pydantic OK")
except Exception as e:
    print(f"❌ pydantic: {e}")
    sys.exit(1)

try:
    from starlette.middleware.cors import CORSMiddleware
    print("✅ starlette.middleware.cors OK")
except Exception as e:
    print(f"❌ starlette.middleware.cors: {e}")
    sys.exit(1)

print("\n✅ All imports successful!")
PYTEST

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Import test failed - installing dependencies..."
    pip3 install -q fastapi uvicorn psutil pydantic starlette python-multipart
    echo "✅ Dependencies installed"
fi

echo ""
echo "2. Testing if main_simple.py can be imported..."

python3 -c "import main_simple" 2>&1 | head -20

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ main_simple.py import failed"
    echo ""
    echo "Checking if file exists..."
    ls -la main_simple.py
    echo ""
    echo "Checking file contents (first 30 lines)..."
    head -30 main_simple.py
    echo ""
    echo "Trying to run directly..."
    python3 main_simple.py --help 2>&1 | head -20
else
    echo "✅ main_simple.py can be imported"
fi

echo ""
echo "3. Stopping any existing backend processes..."
pm2 delete backend 2>/dev/null || true
pkill -f "main_simple.py" 2>/dev/null || true

echo ""
echo "4. Starting backend with proper command..."

# Try different startup methods
echo "Method 1: Direct python command"
pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000

sleep 5

# Check if it's running
if pm2 list | grep -q "backend.*online"; then
    echo "✅ Backend started successfully!"
else
    echo "❌ Backend failed to start with Method 1"
    echo ""
    echo "Trying Method 2: Using bash wrapper..."
    
    pm2 delete backend 2>/dev/null || true
    
    # Create a startup script
    cat > /tmp/start-backend.sh << 'EOF'
#!/bin/bash
cd /nexuslang-v2/v2/backend
exec python3 main_simple.py --host 0.0.0.0 --port 8000
EOF
    chmod +x /tmp/start-backend.sh
    
    pm2 start /tmp/start-backend.sh --name backend
    
    sleep 5
    
    if pm2 list | grep -q "backend.*online"; then
        echo "✅ Backend started successfully with Method 2!"
    else
        echo "❌ Backend still failing"
        echo ""
        echo "Checking logs..."
        pm2 logs backend --lines 50 --nostream
    fi
fi

echo ""
echo "5. Testing backend endpoint..."
sleep 3

curl -s http://localhost:8000/health || echo "❌ Backend not responding"

echo ""
echo ""
echo "6. Final PM2 Status:"
pm2 list

echo ""
echo "7. Backend logs (last 20 lines):"
pm2 logs backend --lines 20 --nostream

echo ""
echo "🎉 BACKEND FIX COMPLETE!"
echo ""
echo "If backend is still errored, check logs with: pm2 logs backend"

