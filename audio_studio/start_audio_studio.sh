#!/bin/bash

# Wan2GP Audio Studio - Quick Start Script

set -e

echo "=================================="
echo "Wan2GP Audio Studio Quick Start"
echo "=================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "Error: Virtual environment not found at $PROJECT_DIR/.venv"
    echo "Please create a virtual environment first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$PROJECT_DIR/.venv/bin/activate"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed."
    echo "Please install Node.js 18.x or 20.x from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed."
    echo "Please install npm (comes with Node.js)."
    exit 1
fi

# Install backend dependencies if needed
if [ ! -f "$PROJECT_DIR/audio_backend/.deps_installed" ]; then
    echo ""
    echo "Installing backend dependencies..."
    pip install -r "$PROJECT_DIR/audio_backend/requirements.txt"
    touch "$PROJECT_DIR/audio_backend/.deps_installed"
fi

# Install frontend dependencies if needed
if [ ! -d "$PROJECT_DIR/audio_frontend/node_modules" ]; then
    echo ""
    echo "Installing frontend dependencies..."
    cd "$PROJECT_DIR/audio_frontend"
    npm install
    cd "$PROJECT_DIR"
fi

# Parse arguments
START_BACKEND=true
START_FRONTEND=true
DEV_MODE=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            START_FRONTEND=false
            shift
            ;;
        --frontend-only)
            START_BACKEND=false
            shift
            ;;
        --production)
            DEV_MODE=false
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-only    Start only the backend server"
            echo "  --frontend-only   Start only the frontend server"
            echo "  --production      Start in production mode (build frontend)"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                Start both backend and frontend in development mode"
            echo "  $0 --backend-only  Start only the backend"
            echo "  $0 --production    Build frontend and start backend serving it"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Start servers
if [ "$DEV_MODE" = true ]; then
    echo ""
    echo "Starting in DEVELOPMENT mode..."
    echo ""
    
    if [ "$START_BACKEND" = true ]; then
        echo "Starting FastAPI backend on http://127.0.0.1:8001..."
        cd "$PROJECT_DIR"
        python audio_backend/main.py &
        BACKEND_PID=$!
        echo "Backend PID: $BACKEND_PID"
        echo ""
    fi
    
    if [ "$START_FRONTEND" = true ]; then
        echo "Starting Vite frontend on http://localhost:3000..."
        cd "$PROJECT_DIR/audio_frontend"
        npm run dev &
        FRONTEND_PID=$!
        echo "Frontend PID: $FRONTEND_PID"
        echo ""
    fi
    
    echo "=================================="
    echo "Servers started successfully!"
    echo "=================================="
    echo ""
    echo "Frontend: http://localhost:3000"
    echo "Backend:  http://127.0.0.1:8001"
    echo "API Docs: http://127.0.0.1:8001/docs"
    echo ""
    echo "Press Ctrl+C to stop all servers"
    echo ""
    
    # Wait for interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopping servers...'; exit" INT TERM
    
    if [ "$START_BACKEND" = true ] && [ "$START_FRONTEND" = true ]; then
        wait $BACKEND_PID $FRONTEND_PID
    elif [ "$START_BACKEND" = true ]; then
        wait $BACKEND_PID
    elif [ "$START_FRONTEND" = true ]; then
        wait $FRONTEND_PID
    fi
else
    echo ""
    echo "Starting in PRODUCTION mode..."
    echo ""
    
    # Build frontend
    echo "Building frontend..."
    cd "$PROJECT_DIR/audio_frontend"
    npm run build
    cd "$PROJECT_DIR"
    
    if [ "$START_BACKEND" = true ]; then
        echo ""
        echo "Starting FastAPI backend serving built frontend..."
        echo "Access at: http://127.0.0.1:8001"
        echo ""
        cd "$PROJECT_DIR"
        python audio_backend/main.py
    fi
fi
