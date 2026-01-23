#!/bin/bash
# Visual Search Demo - One-Click Startup (Mac/Linux)

set -e

BACKEND_PORT=8000
STATIC_PORT=8001
DEMO_URL="http://localhost:${STATIC_PORT}/enterprise_demo/frontend_product/index.html"

# Cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    [ ! -z "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
    [ ! -z "$STATIC_PID" ] && kill $STATIC_PID 2>/dev/null || true
    echo "Servers stopped."
    exit 0
}

trap cleanup EXIT INT TERM

echo ""
echo "=========================================="
echo "  Visual Search Demo - Starting..."
echo "=========================================="
echo ""

# Check directory
if [ ! -d "enterprise_demo" ]; then
    echo "ERROR: Run this from Workbench/ directory"
    exit 1
fi

# Activate conda environment
echo "Activating vis_similarity environment..."
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)"
    conda activate vis_similarity || {
        echo "ERROR: Failed to activate vis_similarity environment"
        echo "Create it first: conda create -n vis_similarity python=3.9"
        exit 1
    }
else
    echo "ERROR: conda not found"
    exit 1
fi

# Check ports
if lsof -Pi :${BACKEND_PORT} -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "ERROR: Port ${BACKEND_PORT} in use. Run ./stop_demo.sh first."
    exit 1
fi

# Start backend
echo "Starting backend server..."
cd enterprise_demo/backend/app
python main.py > ../../../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ../../..
echo "Backend started (PID: $BACKEND_PID)"

# Wait for backend
echo "Waiting for backend (8 seconds)..."
sleep 8

# Start static server
echo "Starting static server..."
python -m http.server ${STATIC_PORT} > logs/static.log 2>&1 &
STATIC_PID=$!
echo "Static server started (PID: $STATIC_PID)"

sleep 2

# Open browser
echo "Opening browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open "${DEMO_URL}" 2>/dev/null || true
elif command -v open &> /dev/null; then
    open "${DEMO_URL}" 2>/dev/null || true
fi

echo ""
echo "=========================================="
echo "  Demo Started!"
echo "=========================================="
echo ""
echo "Backend:  http://localhost:${BACKEND_PORT}"
echo "Demo:     ${DEMO_URL}"
echo ""
echo "Press Ctrl+C to stop servers"
echo ""

# Tail logs
tail -f logs/backend.log logs/static.log 2>/dev/null
