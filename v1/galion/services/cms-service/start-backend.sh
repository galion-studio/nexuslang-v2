#!/bin/bash
# Startup script for CMS Backend (Linux/Mac)

echo "========================================"
echo "  Starting CMS Backend API"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the FastAPI server
echo
echo "========================================"
echo "  CMS API is starting..."
echo "  API URL: http://localhost:8000"
echo "  Documentation: http://localhost:8000/docs"
echo "========================================"
echo

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

