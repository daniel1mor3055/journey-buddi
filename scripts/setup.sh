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

echo -e "${GREEN}━━━ Journey Buddi — Setup ━━━${NC}"

# ── 1. Pre-flight checks ────────────────────────────────────
step "Checking prerequisites"

command -v docker >/dev/null 2>&1 || fail "Docker is not installed"
docker info >/dev/null 2>&1     || fail "Docker daemon is not running — open Docker Desktop"
command -v python3 >/dev/null 2>&1 || fail "python3 is not installed"
command -v node >/dev/null 2>&1   || fail "node is not installed"

if command -v uv >/dev/null 2>&1; then
    ok "docker, python3, node, uv found"
    USE_UV=true
else
    ok "docker, python3, node found (uv not found, will use pip)"
    USE_UV=false
fi

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

# ── 3. Python dependencies ───────────────────────────────────
step "Setting up Python dependencies"

if [ "$USE_UV" = true ]; then
    if [ ! -d ".venv" ]; then
        uv venv
        ok "Created .venv with uv"
    fi
    uv pip install -q -r backend/requirements.txt
    ok "Python dependencies installed (uv)"
else
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        ok "Created venv"
    fi
    venv/bin/pip3 install -q -r backend/requirements.txt
    ok "Python dependencies installed (pip)"
fi

# ── 4. Backend .env ──────────────────────────────────────────
step "Checking backend .env"

if [ ! -f "backend/.env" ]; then
    cp .env backend/.env 2>/dev/null || cp .env.example backend/.env 2>/dev/null || true
    if [ -f "backend/.env" ]; then
        ok "Copied .env to backend/"
    else
        warn "No .env found — backend will use defaults"
    fi
else
    ok "backend/.env exists"
fi

# ── 5. Frontend dependencies ─────────────────────────────────
step "Installing frontend dependencies"

if [ ! -d "frontend/node_modules" ]; then
    cd frontend
    npm install
    cd "$ROOT"
    ok "node_modules installed"
else
    ok "node_modules already exists"
fi

# ── 6. Run Alembic migrations ────────────────────────────────
step "Running database migrations"

cd backend
if [ "$USE_UV" = true ]; then
    PYTHONPATH=. uv run alembic upgrade head
else
    PYTHONPATH=. ../venv/bin/python3 -m alembic upgrade head
fi
cd "$ROOT"
ok "Migrations applied"

# ── 7. Seed attractions ──────────────────────────────────────
step "Checking if attractions need seeding"

cd backend
SEED_OUT=$(
if [ "$USE_UV" = true ]; then
    uv run python -c "
import asyncio, logging
logging.disable(logging.CRITICAL)
from app.database import async_session
from sqlalchemy import text

async def check():
    async with async_session() as s:
        r = await s.execute(text('SELECT count(*) FROM attractions'))
        return r.scalar()

print(asyncio.run(check()))
" 2>/dev/null || echo "0"
else
    PYTHONPATH=. ../venv/bin/python3 -c "
import asyncio, logging
logging.disable(logging.CRITICAL)
from app.database import async_session
from sqlalchemy import text

async def check():
    async with async_session() as s:
        r = await s.execute(text('SELECT count(*) FROM attractions'))
        return r.scalar()

print(asyncio.run(check()))
" 2>/dev/null || echo "0"
fi
)
cd "$ROOT"

if [ "$SEED_OUT" = "0" ] || [ "$SEED_OUT" = "" ]; then
    warn "Attractions table is empty — seed after starting backend with:"
    echo -e "     ${YELLOW}curl -X POST http://localhost:8000/api/v1/attractions/seed${NC}"
else
    ok "Attractions already seeded ($SEED_OUT attractions)"
fi

# ── Done ─────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━ Setup complete ━━━${NC}"
echo ""
echo -e "  Next steps:"
echo ""
echo -e "  ${CYAN}1. Backend terminal:${NC}"
echo -e "     ${YELLOW}cd backend && ../scripts/backend.sh${NC}"
echo ""
echo -e "  ${CYAN}2. Frontend terminal:${NC}"
echo -e "     ${YELLOW}cd frontend && ../scripts/frontend.sh${NC}"
echo ""
echo -e "  ${CYAN}3. Seed attractions (if needed):${NC}"
echo -e "     ${YELLOW}curl -X POST http://localhost:8000/api/v1/attractions/seed${NC}"
echo ""
