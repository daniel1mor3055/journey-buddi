#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

step() { echo -e "\n${CYAN}▸ $1${NC}"; }
ok()   { echo -e "  ${GREEN}✓ $1${NC}"; }

echo -e "${YELLOW}━━━ Journey Buddi — Stop ━━━${NC}"

# ── Kill backend (port 8000) ─────────────────────────────────
step "Stopping backend"

BACKEND_PIDS=$(lsof -ti :8000 2>/dev/null || true)
if [ -n "$BACKEND_PIDS" ]; then
    echo "$BACKEND_PIDS" | xargs kill 2>/dev/null || true
    sleep 1
    ok "Backend stopped"
else
    ok "Backend was not running"
fi

# ── Kill frontend (port 3000) ────────────────────────────────
step "Stopping frontend"

FRONTEND_PIDS=$(lsof -ti :3000 2>/dev/null || true)
if [ -n "$FRONTEND_PIDS" ]; then
    echo "$FRONTEND_PIDS" | xargs kill 2>/dev/null || true
    sleep 1
    ok "Frontend stopped"
else
    ok "Frontend was not running"
fi

# ── Stop Docker services ────────────────────────────────────
step "Stopping Docker services"

docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true
ok "Docker containers stopped"

echo ""
echo -e "${GREEN}━━━ All services stopped ━━━${NC}"
echo ""
