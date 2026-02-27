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
fail() { echo -e "  ${RED}✗ $1${NC}"; exit 1; }

echo -e "${GREEN}━━━ Journey Buddi — Start ━━━${NC}"

# ── 1. Pre-flight checks ────────────────────────────────────
step "Checking prerequisites"

command -v docker >/dev/null 2>&1 || fail "Docker is not installed"
docker info >/dev/null 2>&1     || fail "Docker daemon is not running — open Docker Desktop"
command -v python3 >/dev/null 2>&1 || fail "python3 is not installed"
command -v node >/dev/null 2>&1   || fail "node is not installed"
ok "docker, python3, node found"

# ── 2. Docker services ──────────────────────────────────────
step "Starting Docker services (PostgreSQL + Redis)"

docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null
ok "Docker containers up"

step "Waiting for PostgreSQL to be healthy"
for i in $(seq 1 30); do
    if docker compose exec -T db pg_isready -U journeybuddi >/dev/null 2>&1; then
        ok "PostgreSQL ready"
        break
    fi
    if [ "$i" -eq 30 ]; then fail "PostgreSQL did not become healthy in 30s"; fi
    sleep 1
done

step "Waiting for Redis to be healthy"
for i in $(seq 1 15); do
    if docker compose exec -T redis redis-cli ping >/dev/null 2>&1; then
        ok "Redis ready"
        break
    fi
    if [ "$i" -eq 15 ]; then fail "Redis did not become healthy in 15s"; fi
    sleep 1
done

# ── 3. Python venv ───────────────────────────────────────────
step "Setting up Python virtual environment"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    ok "Created new venv"
else
    ok "venv already exists"
fi

venv/bin/pip3 install -q -r backend/requirements.txt
ok "Python dependencies installed"

# ── 4. Backend .env ──────────────────────────────────────────
step "Checking backend .env"

if [ ! -f "backend/.env" ]; then
    cp .env backend/.env 2>/dev/null || cp .env.example backend/.env 2>/dev/null || true
    if [ -f "backend/.env" ]; then
        ok "Copied .env to backend/"
    else
        warn "No .env found — backend will use defaults (fine for local dev)"
    fi
else
    ok "backend/.env exists"
fi

# ── 5. Run Alembic migrations ────────────────────────────────
step "Running database migrations"

cd backend
PYTHONPATH=. ../venv/bin/python3 -m alembic upgrade head
ok "Migrations applied"
cd "$ROOT"

# ── 6. Seed attractions (idempotent) ────────────────────────
step "Seeding NZ attractions"

cd backend
SEED_OUT=$(PYTHONPATH=. ../venv/bin/python3 -c "
import asyncio, logging
logging.disable(logging.CRITICAL)
from app.database import async_session
from sqlalchemy import text

async def check():
    async with async_session() as s:
        r = await s.execute(text('SELECT count(*) FROM attractions'))
        return r.scalar()

print(asyncio.run(check()))
" 2>/dev/null || echo "0")
cd "$ROOT"

if [ "$SEED_OUT" = "0" ] || [ "$SEED_OUT" = "" ]; then
    curl -s -X POST http://localhost:8000/api/v1/attractions/seed >/dev/null 2>&1 && \
        ok "Seeded 18 attractions" || \
        warn "Seed will run once backend is up — use: curl -X POST http://localhost:8000/api/v1/attractions/seed"
else
    ok "Attractions already seeded ($SEED_OUT)"
fi

# ── 7. Kill any stale processes on ports 8000 / 3000 ────────
step "Checking for stale processes"

kill_port() {
    local port=$1
    local pid
    pid=$(lsof -ti :"$port" 2>/dev/null || true)
    if [ -n "$pid" ]; then
        kill "$pid" 2>/dev/null || true
        sleep 1
        ok "Killed stale process on port $port (pid $pid)"
    fi
}

kill_port 8000
kill_port 3000

# ── 8. Start backend ────────────────────────────────────────
step "Starting backend (FastAPI on :8000)"

mkdir -p "$ROOT/logs"

cd backend
PYTHONPATH=. nohup ../venv/bin/python3 -m uvicorn app.main:app \
    --host 0.0.0.0 --port 8000 --reload \
    > "$ROOT/logs/backend.log" 2>&1 &
BACKEND_PID=$!
cd "$ROOT"
sleep 2
if kill -0 "$BACKEND_PID" 2>/dev/null; then
    ok "Backend running (pid $BACKEND_PID) — logs: logs/backend.log"
else
    fail "Backend failed to start — check logs/backend.log"
fi

# Wait for backend to respond
for i in $(seq 1 10); do
    if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
        ok "Backend health check passed"
        break
    fi
    if [ "$i" -eq 10 ]; then warn "Backend not responding yet — it may still be starting"; fi
    sleep 1
done

# Seed again now that backend is up (in case earlier seed was skipped)
if [ "$SEED_OUT" = "0" ] || [ "$SEED_OUT" = "" ]; then
    curl -s -X POST http://localhost:8000/api/v1/attractions/seed >/dev/null 2>&1 && \
        ok "Seeded attractions via API" || true
fi

# ── 9. Start frontend ───────────────────────────────────────
step "Starting frontend (Next.js on :3000)"

cd frontend
nohup npm run dev > "$ROOT/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
cd "$ROOT"

sleep 3
if kill -0 "$FRONTEND_PID" 2>/dev/null; then
    ok "Frontend running (pid $FRONTEND_PID) — logs: logs/frontend.log"
else
    fail "Frontend failed to start — check logs/frontend.log"
fi

# ── Done ─────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━ All services running ━━━${NC}"
echo ""
echo -e "  Frontend:  ${CYAN}http://localhost:3000${NC}"
echo -e "  Backend:   ${CYAN}http://localhost:8000${NC}"
echo -e "  API docs:  ${CYAN}http://localhost:8000/docs${NC}"
echo -e "  Health:    ${CYAN}http://localhost:8000/health${NC}"
echo ""
echo -e "  Backend logs:  ${YELLOW}tail -f logs/backend.log${NC}"
echo -e "  Frontend logs: ${YELLOW}tail -f logs/frontend.log${NC}"
echo -e "  Stop all:      ${YELLOW}./scripts/stop.sh${NC}"
echo ""
