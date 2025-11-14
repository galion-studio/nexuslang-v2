#!/bin/bash
echo "🔍 Complete Server Troubleshooting"
echo "=================================="

# Check logs
echo ""
echo "1. Recent server logs:"
tail -20 /workspace/logs/galion-backend.log 2>/dev/null || echo "No log file found"

# Check if port is in use
echo ""
echo "2. Port 8080 status:"
ss -tlnp | grep 8080 || echo "Port 8080 not in use"

# Check running processes
echo ""
echo "3. Python processes:"
ps aux | grep python | grep -v grep

# Check if we can start server in foreground for 5 seconds
echo ""
echo "4. Testing server startup (5 seconds):"
cd /workspace/project-nexus/v2/backend
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
timeout 5 python -m uvicorn main_simple:app --host 0.0.0.0 --port 8080 --log-level info 2>&1 || echo "Server test completed"

# Check available memory
echo ""
echo "5. System resources:"
free -h 2>/dev/null || echo "Memory info not available"

# Check if required modules can be imported individually
echo ""
echo "6. Testing individual imports:"
python -c "import fastapi; print('✅ fastapi')" 2>&1
python -c "import uvicorn; print('✅ uvicorn')" 2>&1
python -c "import pydantic; print('✅ pydantic')" 2>&1

echo ""
echo "7. Testing main module imports:"
python -c "from fastapi import FastAPI; print('✅ FastAPI import')" 2>&1
python -c "from fastapi.middleware.cors import CORSMiddleware; print('✅ CORS import')" 2>&1

echo ""
echo "8. Testing main_simple app creation:"
python -c "from main_simple import app; print('✅ App created successfully')" 2>&1
