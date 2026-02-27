#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/frontend"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}━━━ Starting Frontend ━━━${NC}"
echo ""
echo -e "${CYAN}Next.js dev server starting on:${NC} http://localhost:3000"
echo ""
echo -e "${YELLOW}Logs will stream below...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

if [ ! -d "node_modules" ]; then
    echo "Error: node_modules not found. Run ./scripts/setup.sh first"
    exit 1
fi

npm run dev
