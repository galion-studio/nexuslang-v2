#!/bin/bash
# Start GALION.STUDIO Alpha

echo "🚀 Starting GALION.STUDIO Alpha..."
echo ""

# Start backend
echo "📊 Starting backend..."
python app.py &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 3

# Seed data
echo "🌱 Seeding test data..."
curl -X POST http://localhost:5000/api/seed
echo ""

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm start

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT

