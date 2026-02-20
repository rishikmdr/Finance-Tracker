#!/usr/bin/env bash
# ============================================================================
# Finance Tracker — One-command startup for laptop use
# No Docker, no PostgreSQL, no Redis needed. Just Python 3.11+ and Node 18+.
#
# Usage:
#   chmod +x start.sh
#   ./start.sh
#
# First run installs dependencies automatically.
# Backend: http://localhost:8000 (API + Swagger docs at /api/docs)
# Frontend: http://localhost:5173 (auto-opens in browser)
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║       Finance Tracker v0.1.0          ║"
echo "  ║   AI-Powered Personal Finance Tool    ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is required. Install from https://python.org${NC}"
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "  Python: ${GREEN}${PY_VERSION}${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is required. Install from https://nodejs.org${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "  Node.js: ${GREEN}${NODE_VERSION}${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is required. Comes with Node.js.${NC}"
    exit 1
fi

# Setup backend
echo ""
echo -e "${YELLOW}Setting up backend...${NC}"
cd backend

if [ ! -d ".venv" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "  Installing Python dependencies..."
pip install -q -e . 2>&1 | tail -1

cd ..

# Setup frontend
echo -e "${YELLOW}Setting up frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "  Installing Node dependencies..."
    npm install --silent 2>&1 | tail -1
fi

cd ..

# Start services
echo ""
echo -e "${GREEN}Starting services...${NC}"
echo -e "  Backend  → ${BLUE}http://localhost:8000${NC}  (API docs: /api/docs)"
echo -e "  Frontend → ${BLUE}http://localhost:5173${NC}"
echo ""
echo -e "${YELLOW}Database: SQLite (zero config, file: backend/finance_tracker.db)${NC}"
echo -e "${YELLOW}AI features: Add your Anthropic API key in Settings page${NC}"
echo ""
echo -e "Press ${RED}Ctrl+C${NC} to stop both services."
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup INT TERM

# Start backend
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend ready!${NC}"
        break
    fi
    sleep 1
done

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}Both services running. Open http://localhost:5173 in your browser.${NC}"
echo ""

# Wait for either to exit
wait $BACKEND_PID $FRONTEND_PID
