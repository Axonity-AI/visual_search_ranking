#!/bin/bash
# run_local.sh - Start Visual Search Ranking in development mode
#
# Usage:
#   ./scripts/run_local.sh                    # Start MVP demo
#   ./scripts/run_local.sh --enterprise       # Start Enterprise demo
#   ./scripts/run_local.sh --production       # Production mode

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"

BACKEND_PORT=${BACKEND_PORT:-8000}
STATIC_PORT=${STATIC_PORT:-8001}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Visual Search Ranking - Local Runner             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"

# Parse arguments
DEMO_TYPE="mvp"
PRODUCTION_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --enterprise)
            DEMO_TYPE="enterprise"
            shift
            ;;
        --production)
            PRODUCTION_MODE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${YELLOW}Demo type: $DEMO_TYPE${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r "$PROJECT_ROOT/requirements.txt"

# Add src to Python path
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${YELLOW}Loading environment variables from .env${NC}"
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
elif [ -f "$PROJECT_ROOT/.env.example" ]; then
    echo -e "${YELLOW}Loading environment variables from .env.example${NC}"
    export $(grep -v '^#' "$PROJECT_ROOT/.env.example" | xargs)
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    pkill -P $$ || true
    exit 0
}
trap cleanup INT TERM

# Start backend
echo -e "${GREEN}Starting backend on port $BACKEND_PORT...${NC}"
if [ "$DEMO_TYPE" == "enterprise" ]; then
    python -m visual_search_ranking.enterprise.main &
else
    cd "$PROJECT_ROOT/src/visual_search_ranking/mvp"
    python main.py &
    cd "$PROJECT_ROOT"
fi
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start static file server
echo -e "${GREEN}Starting static server on port $STATIC_PORT...${NC}"
cd "$PROJECT_ROOT"
python -m http.server $STATIC_PORT &
STATIC_PID=$!

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Servers are running!${NC}"
echo ""
echo -e "  Backend API:  ${YELLOW}http://localhost:$BACKEND_PORT${NC}"
echo -e "  API Docs:     ${YELLOW}http://localhost:$BACKEND_PORT/docs${NC}"

if [ "$DEMO_TYPE" == "enterprise" ]; then
    echo -e "  Frontend:     ${YELLOW}http://localhost:$STATIC_PORT/frontend/enterprise/index.html${NC}"
else
    echo -e "  Frontend:     ${YELLOW}http://localhost:$STATIC_PORT/frontend/mvp/index.html${NC}"
fi

echo ""
echo -e "${GREEN}Press Ctrl+C to stop all servers${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"

# Wait for background processes
wait
