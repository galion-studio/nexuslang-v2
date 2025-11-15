#!/bin/bash
# Simple one-command deployment for RunPod
# Usage: wget https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/runpod-deploy-simple.sh && bash runpod-deploy-simple.sh

cd /nexuslang-v2 || exit 1
git fetch origin
git reset --hard origin/clean-nexuslang
pip3 install -q fastapi uvicorn psutil pydantic python-multipart
cd galion-studio && npm install --silent && cd ..
cd galion-app && npm install --silent && cd ..
cd developer-platform && npm install --silent && cd ..
pm2 delete all 2>/dev/null || true
cd v2/backend && pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000 && cd ../..
cd galion-studio && pm2 start npm --name galion-studio -- run dev -- -p 3030 && cd ..
cd galion-app && npm install lucide-react --silent && pm2 start npm --name galion-app -- run dev -- -p 3000 && cd ..
cd developer-platform && pm2 start npm --name developer-platform -- run dev -- -p 3003 && cd ..
pm2 save
pm2 status
echo "✅ Done!"

