#!/bin/bash
# Quick Start Script - Launches both backend and frontend (Linux/Mac)

echo "========================================"
echo "  Starting Complete CMS System"
echo "========================================"
echo
echo "This will start:"
echo " 1. Backend API (http://localhost:8000)"
echo " 2. Frontend UI (http://localhost:3000)"
echo
echo "Press Ctrl+C to stop the system"
echo

# Make scripts executable
chmod +x start-backend.sh
chmod +x frontend/start-frontend.sh

# Function to cleanup on exit
cleanup() {
    echo
    echo "Stopping CMS services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup EXIT INT TERM

# Start backend
echo "Starting backend..."
./start-backend.sh &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
cd frontend && ./start-frontend.sh &
FRONTEND_PID=$!
cd ..

echo
echo "========================================"
echo "  CMS System Running!"
echo
echo "  Backend API: http://localhost:8000/docs"
echo "  Frontend UI: http://localhost:3000"
echo
echo "  Press Ctrl+C to stop all services"
echo "========================================"
echo

# Wait for user interrupt
wait

