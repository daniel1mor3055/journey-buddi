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
warn() { echo -e "  ${YELLOW}⚠ $1${NC}"; }

echo -e "${RED}━━━ Journey Buddi — Full Reset ━━━${NC}"
echo ""
echo -e "${YELLOW}This will:${NC}"
echo "  1. Stop all running services"
echo "  2. Destroy the database and all data"
echo "  3. Remove the Python virtual environment"
echo "  4. Remove node_modules"
echo "  5. Rebuild everything from scratch"
echo ""
read -p "Are you sure? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# ── 1. Stop everything ──────────────────────────────────────
step "Stopping all services"

BACKEND_PIDS=$(lsof -ti :8000 2>/dev/null || true)
[ -n "$BACKEND_PIDS" ] && echo "$BACKEND_PIDS" | xargs kill 2>/dev/null || true

FRONTEND_PIDS=$(lsof -ti :3000 2>/dev/null || true)
[ -n "$FRONTEND_PIDS" ] && echo "$FRONTEND_PIDS" | xargs kill 2>/dev/null || true

sleep 1
ok "Application processes killed"

# ── 2. Destroy Docker volumes (database data) ───────────────
step "Destroying Docker containers and volumes"

docker compose down -v 2>/dev/null || docker-compose down -v 2>/dev/null || true
ok "Docker containers and volumes removed"

# ── 3. Remove Python venv ───────────────────────────────────
step "Removing Python virtual environment"

if [ -d "venv" ]; then
    rm -rf venv
    ok "venv removed"
else
    ok "No venv to remove"
fi

# ── 4. Remove node_modules ──────────────────────────────────
step "Removing node_modules"

if [ -d "frontend/node_modules" ]; then
    rm -rf frontend/node_modules
    ok "frontend/node_modules removed"
else
    ok "No node_modules to remove"
fi

# ── 5. Remove logs ──────────────────────────────────────────
step "Removing logs"

rm -rf logs
ok "Logs removed"

# ── 6. Remove Next.js cache ─────────────────────────────────
step "Removing Next.js build cache"

rm -rf frontend/.next
ok ".next cache removed"

# ── 7. Remove Python caches ─────────────────────────────────
step "Removing Python caches"

find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find backend -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
ok "Python caches removed"

# ── 8. Rebuild everything ───────────────────────────────────
step "Recreating Python virtual environment"

python3 -m venv venv
venv/bin/pip3 install -q --upgrade pip
venv/bin/pip3 install -q -r backend/requirements.txt
ok "venv recreated and dependencies installed"

step "Reinstalling frontend dependencies"

cd frontend
npm install
cd "$ROOT"
ok "node_modules reinstalled"

# ── 9. Start Docker fresh ───────────────────────────────────
step "Starting Docker services (fresh database)"

docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null
ok "Docker containers started"

step "Waiting for PostgreSQL"
for i in $(seq 1 30); do
    if docker compose exec -T db pg_isready -U journeybuddi >/dev/null 2>&1; then
        ok "PostgreSQL ready"
        break
    fi
    if [ "$i" -eq 30 ]; then warn "PostgreSQL slow to start"; fi
    sleep 1
done

step "Waiting for Redis"
for i in $(seq 1 15); do
    if docker compose exec -T redis redis-cli ping >/dev/null 2>&1; then
        ok "Redis ready"
        break
    fi
    if [ "$i" -eq 15 ]; then warn "Redis slow to start"; fi
    sleep 1
done

# ── 10. Run migrations ──────────────────────────────────────
step "Running database migrations"

cd backend
PYTHONPATH=. ../venv/bin/python3 -m alembic upgrade head
cd "$ROOT"
ok "Migrations applied to fresh database"

# ── 11. Copy .env to backend if needed ───────────────────────
step "Setting up backend .env"

if [ ! -f "backend/.env" ]; then
    if [ -f ".env" ]; then
        cp .env backend/.env
        ok "Copied root .env to backend/"
    elif [ -f ".env.example" ]; then
        cp .env.example backend/.env
        warn "Copied .env.example to backend/.env — edit it with your real keys"
    fi
else
    ok "backend/.env already exists"
fi

# ── Done ─────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━ Reset complete ━━━${NC}"
echo ""
echo -e "  Everything is clean and rebuilt."
echo -e "  Database is empty (migrations applied, no seed data yet)."
echo ""
echo -e "  Next steps:"
echo -e "    ${CYAN}./scripts/start.sh${NC}   — Start all services"
echo -e "    The start script will seed attraction data automatically."
echo ""
echo -e "  Or start manually:"
echo -e "    ${YELLOW}cd backend && PYTHONPATH=. ../venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload${NC}"
echo -e "    ${YELLOW}cd frontend && npm run dev${NC}"
echo -e "    ${YELLOW}curl -X POST http://localhost:8000/api/v1/attractions/seed${NC}"
echo ""
