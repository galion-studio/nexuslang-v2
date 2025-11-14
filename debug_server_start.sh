#!/bin/bash
echo "🐛 Debugging Server Start Issues"
echo "================================"

# Check Python version and path
echo ""
echo "1. Python version:"
python --version
which python

# Check if we can import the main module
echo ""
echo "2. Testing main_simple import:"
cd /workspace/project-nexus/v2/backend
python -c "import sys; print('Python path:'); [print(p) for p in sys.path]; print('\\nTrying import...')" 2>&1
python -c "from main_simple import app; print('✅ Import successful')" 2>&1

# Check if required packages are installed
echo ""
echo "3. Checking required packages:"
python -c "import fastapi, uvicorn; print('✅ fastapi and uvicorn available')" 2>&1

# Try to start server with verbose output
echo ""
echo "4. Starting server with debug output:"
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
timeout 10 python -m uvicorn main_simple:app --host 0.0.0.0 --port 8080 --log-level debug 2>&1 || echo "Server failed to start within 10 seconds"

# Check what happened
echo ""
echo "5. Checking if server started:"
ps aux | grep uvicorn | grep -v grep || echo "No uvicorn processes found"

echo ""
echo "6. Recent log entries:"
tail -10 /workspace/logs/galion-backend.log 2>/dev/null || echo "No log file found"
