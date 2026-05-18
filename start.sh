#!/bin/bash
set -e

# ERP Backend Startup Script (with Virtual Environment)

PROJECT_DIR="/home/ubuntu/erp"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$PROJECT_DIR/venv"

cd "$BACKEND_DIR"

# Create virtual environment if not exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python -c "from database import engine; from models.base import Base; Base.metadata.create_all(bind=engine)" 2>/dev/null || true

# Start backend server
echo "Starting ERP Backend on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4