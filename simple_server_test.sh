#!/bin/bash
echo "🧪 Simple Server Test"
echo "===================="

cd /workspace/project-nexus/v2/backend
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2

echo "Testing imports..."
python -c "from main_simple import app; print('✅ Import works')"

echo ""
echo "Testing server start for 3 seconds..."
timeout 3 python -m uvicorn main_simple:app --host 0.0.0.0 --port 8080 --log-level info 2>&1

echo ""
echo "Done."
