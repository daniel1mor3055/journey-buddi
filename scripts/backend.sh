#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}━━━ Starting Backend ━━━${NC}"
echo ""
echo -e "${CYAN}FastAPI server starting on:${NC} http://localhost:8000"
echo -e "${CYAN}API docs:${NC} http://localhost:8000/docs"
echo -e "${CYAN}Health check:${NC} http://localhost:8000/health"
echo ""
echo -e "${YELLOW}Logs will stream below...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Check if uv is available
if command -v uv >/dev/null 2>&1 && [ -d "$ROOT/.venv" ]; then
    cd "$ROOT"
    PYTHONPATH=backend uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
elif [ -d "$ROOT/venv" ]; then
    PYTHONPATH=. ../venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "Error: No Python environment found. Run ./scripts/setup.sh first"
    exit 1
fi
