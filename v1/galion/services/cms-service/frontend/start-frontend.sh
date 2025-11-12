#!/bin/bash
# Startup script for CMS Frontend (Linux/Mac)

echo "========================================"
echo "  Starting CMS Frontend"
echo "========================================"
echo

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the React development server
echo
echo "========================================"
echo "  CMS Frontend is starting..."
echo "  URL: http://localhost:3000"
echo "========================================"
echo

npm start

