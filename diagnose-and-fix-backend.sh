#!/bin/bash
# Diagnose and fix backend startup issue

echo "🔍 DIAGNOSING BACKEND ISSUE"
echo "==========================="
echo ""

# 1. Check current directory
echo "1. Current directory:"
pwd
echo ""

# 2. Check if backend file exists
echo "2. Checking for main_simple.py..."
if [ -f "v2/backend/main_simple.py" ]; then
    echo "✅ File exists at v2/backend/main_simple.py"
    ls -lh v2/backend/main_simple.py
else
    echo "❌ File NOT found at v2/backend/main_simple.py"
    echo ""
    echo "Searching for main_simple.py..."
    find . -name "main_simple.py" 2>/dev/null
fi

echo ""

# 3. Check directory structure
echo "3. Directory structure:"
ls -la v2/ 2>/dev/null || echo "❌ v2/ directory not found"
ls -la v2/backend/ 2>/dev/null || echo "❌ v2/backend/ directory not found"

echo ""

# 4. Stop backend
echo "4. Stopping backend..."
pm2 delete backend 2>/dev/null || true

echo ""

# 5. Start backend with absolute path
echo "5. Starting backend with absolute path..."

# Get absolute path
BACKEND_DIR="/nexuslang-v2/v2/backend"

if [ -f "$BACKEND_DIR/main_simple.py" ]; then
    echo "✅ Found backend at: $BACKEND_DIR/main_simple.py"
    
    # Create a wrapper script with absolute path
    cat > /tmp/start-backend.sh << EOF
#!/bin/bash
cd $BACKEND_DIR
exec python3 main_simple.py --host 0.0.0.0 --port 8000
EOF
    
    chmod +x /tmp/start-backend.sh
    
    echo "Starting backend with wrapper script..."
    pm2 start /tmp/start-backend.sh --name backend
    
else
    echo "❌ Backend file not found"
    echo "Checking alternative locations..."
    
    # Check if we're in the wrong directory
    if [ -f "/workspace/v2/backend/main_simple.py" ]; then
        echo "✅ Found at /workspace/v2/backend/main_simple.py"
        cat > /tmp/start-backend.sh << EOF
#!/bin/bash
cd /workspace/v2/backend
exec python3 main_simple.py --host 0.0.0.0 --port 8000
EOF
        chmod +x /tmp/start-backend.sh
        pm2 start /tmp/start-backend.sh --name backend
        
    elif [ -f "backend/main_simple.py" ]; then
        echo "✅ Found at backend/main_simple.py (current dir)"
        cat > /tmp/start-backend.sh << EOF
#!/bin/bash
cd $(pwd)/backend
exec python3 main_simple.py --host 0.0.0.0 --port 8000
EOF
        chmod +x /tmp/start-backend.sh
        pm2 start /tmp/start-backend.sh --name backend
    else
        echo "❌ Cannot find main_simple.py anywhere"
        exit 1
    fi
fi

sleep 5

echo ""

# 6. Check status
echo "6. Backend status:"
pm2 list | grep backend

echo ""

# 7. Test backend
echo "7. Testing backend..."
sleep 3

if curl -s --max-time 5 http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is responding!"
    curl http://localhost:8000/health
else
    echo "❌ Backend not responding"
    echo ""
    echo "Checking logs..."
    pm2 logs backend --lines 20 --nostream
fi

echo ""
echo "🎉 DIAGNOSIS COMPLETE!"

