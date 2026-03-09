# Journey Buddi — CLAUDE.md

Project context for AI assistants. Keep this file up to date as the codebase evolves.

---

## What This Project Is

**Journey Buddi** is an AI-powered adaptive travel companion for extended adventure trips. It has two modes:

1. **Planning mode** — conversational AI (Buddi) collects trip preferences through a multi-agent pipeline and generates a day-by-day itinerary.
2. **Companion mode** — live companion during the trip that monitors weather/conditions, delivers daily briefings, and suggests itinerary swaps when conditions change.

**Pilot destination:** New Zealand.

---

## Architecture

| Layer | Tech |
|-------|------|
| Frontend | Next.js 16 (App Router) + TypeScript + Tailwind CSS v4 |
| Backend | Python + FastAPI (async) |
| Database | PostgreSQL 16 + PostGIS |
| Cache | Redis 7 |
| AI/Agents | OpenAI (`gpt-4.1-mini`) + `openai-agents` SDK |
| Task Queue | Celery + Redis |
| Maps | Mapbox GL JS |
| Auth | Magic link (JWT, no passwords) |
| Deployment | Railway (MVP) |

---

## Monorepo Structure

```
journey-buddi/
├── backend/               # FastAPI app
│   ├── app/
│   │   ├── agents/        # AI planning pipeline (core)
│   │   │   ├── context.py     # PlanningContext dataclass (shared mutable state)
│   │   │   ├── pipeline.py    # Agent definitions + PIPELINE list
│   │   │   ├── orchestrator.py # Drives agent transitions turn-by-turn
│   │   │   ├── tools.py       # Function tools (update context, return status)
│   │   │   ├── master.py      # MasterAgent — synthesises context into itinerary prompt
│   │   │   ├── models.py      # PlanningResponse pydantic model
│   │   │   └── prompts.py     # BUDDI_PERSONA, QUESTION_PHILOSOPHY, RESPONSE_RULES
│   │   ├── api/           # Route handlers (one file per domain)
│   │   │   ├── auth.py, trips.py, conversations.py, itinerary.py
│   │   │   ├── briefings.py, conditions.py, swaps.py, attractions.py
│   │   │   └── deps.py        # FastAPI dependency injection (get_db, get_current_user)
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic schemas (request/response)
│   │   ├── services/      # Business logic (weather, briefings, swaps, OpenAI calls)
│   │   ├── data/          # Static NZ data (attractions, activity taxonomy)
│   │   ├── tasks/         # Celery tasks (briefings, monitoring)
│   │   ├── config.py      # Settings via pydantic-settings (.env)
│   │   ├── main.py        # FastAPI app entry point + CORS
│   │   ├── database.py    # Async SQLAlchemy engine + session factory
│   │   ├── auth.py        # JWT + magic link token helpers
│   │   ├── celery_app.py  # Celery app instance
│   │   └── redis.py       # Redis client
│   ├── tests/             # pytest-asyncio tests
│   │   ├── conftest.py    # Fixtures: client, auth_headers, test_email
│   │   └── test_agents.py, test_trips.py, test_auth.py, test_health.py, ...
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   │   ├── auth/      # Magic link auth flow
│   │   │   ├── plan/      # Planning conversation UI
│   │   │   ├── dashboard/ # Post-plan dashboard
│   │   │   └── trip/[tripId]/ # Live companion view
│   │   ├── components/
│   │   │   ├── layout/    # Layout components
│   │   │   └── ui/        # Reusable UI components
│   │   ├── stores/        # Zustand stores
│   │   │   ├── auth-store.ts
│   │   │   ├── conversation-store.ts
│   │   │   ├── trip-store.ts
│   │   │   └── companion-store.ts
│   │   └── lib/           # Utilities, API client
│   └── package.json
├── docs/                  # Architecture docs, specs, ER diagrams
├── scripts/               # Dev scripts (backend.sh, frontend.sh, setup.sh, reset.sh)
├── docker-compose.yml     # PostgreSQL + Redis for local dev
├── postman/               # Postman collection + environment
└── logs/                  # Dev server logs (backend.log, frontend.log)
```

---

## Planning Agent Pipeline

The heart of the product. Each agent is a self-contained question-asking unit. The orchestrator drives transitions — no handoffs between agents.

### 3-Level Activity Design

Activity decision-making is split across three stages to reduce conversation fatigue:

1. **Level 1 — Category Preferences (in conversation):** User picks from 9 TripAdvisor-aligned categories. This is the only activity-related step in the chat.
2. **Level 2 — Specific Activities (post-chat, dashboard):** User browses and selects specific activities within their categories (e.g., "bungy jumping", "whale watching").
3. **Level 3 — Providers (inside itinerary):** Providers are selected as part of a progressive itinerary-building experience, location by location.

### Pipeline order (PIPELINE list in `pipeline.py`):

1. `greeting` — welcome, offer "Let's do it!" / "Tell me more"
2. `travel_dna` — group type, ages, accessibility, fitness, budget
3. `logistics` — dates, duration, max driving hours
4. `interest_categories` — 9 strict TripAdvisor-aligned categories (multi-select)
5. `island_preference` — North Island / South Island / both
6. `transport_route` — transport mode + route direction

### The 9 categories (strict — no additions):

Attractions, Tours, Day Trips, Outdoor Activities, Concerts & Shows, Events, Classes & Workshops, Transportation, Traveler Resources

**Key files:**
- `context.py` — `PlanningContext` dataclass, serialized to `Conversation.planning_state` (JSONB) between turns
- `orchestrator.py` — `PlanningOrchestrator` class, picks current agent, restricts tools to one field at a time
- `tools.py` — all `@function_tool` functions; update context in-place and return a missing-fields status string so the agent knows what to ask next
- `pipeline.py` — agent definitions, dynamic instruction builders, `PIPELINE` list, `FIELD_TOOLS` map
- `master.py` — `MasterAgent.generate_itinerary_prompt()` runs once after pipeline completes; generates a skeleton prompt (activities & providers are empty at this stage)

---

## Running Locally

### Prerequisites
- Docker Desktop running (for PostgreSQL + Redis)
- Node.js (for frontend)
- Python venv already set up

### Start infrastructure
```bash
docker-compose up -d
```

### Start backend
```bash
./scripts/backend.sh
# → http://localhost:8000  (API docs: http://localhost:8000/docs)
```

### Start frontend
```bash
./scripts/frontend.sh
# → http://localhost:3000
```

### Run tests
```bash
venv/bin/python3 -m pytest backend/tests/ -v
```

---

## Environment Variables (`backend/.env`)

```
DATABASE_URL=postgresql+asyncpg://journeybuddi:localdev@localhost:5432/journeybuddi
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=...
MAGIC_LINK_SECRET=...
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
RESEND_API_KEY=...
FROM_EMAIL=noreply@journeybuddi.com
FRONTEND_URL=http://localhost:3000
OPENWEATHERMAP_API_KEY=...
VAPID_PRIVATE_KEY=...
VAPID_PUBLIC_KEY=...
```

---

## Key Conventions

### Python
- **Always use `venv/bin/python3`**, never global `python`. Never `source activate`.
- Async throughout (FastAPI + asyncpg + SQLAlchemy async).
- Structured logging via `structlog`.
- Settings via `pydantic-settings` (`app/config.py`), loaded once with `@lru_cache`.
- Tests: `pytest-asyncio`, fixtures in `conftest.py`. Use `AsyncClient` with `ASGITransport` for API tests.

### TypeScript / Next.js
- App Router (not Pages Router).
- State management: Zustand stores in `src/stores/`.
- No passwords — auth is magic link only.

### Agent Tool Pattern
Tools in `tools.py` follow this pattern:
```python
@function_tool
async def set_group_type(ctx: RunContextWrapper[PlanningContext], group_type: str) -> str:
    ctx.context.group_type = group_type
    missing = travel_dna_missing(ctx.context)
    return f"OK. Still missing: {missing}" if missing else "travel_dna complete"
```

### Commit style
Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `chore:`.

### Development methodology
- TDD: RED → GREEN → REFACTOR
- Plan before coding (see `docs/plans/`)
- DRY and YAGNI

---

## Database

- PostgreSQL 16 + PostGIS (via Docker)
- Local: `postgresql+asyncpg://journeybuddi:localdev@localhost:5432/journeybuddi`
- Migrations: Alembic
- Key models: `User`, `Trip`, `Conversation`, `Itinerary`, `Briefing`, `ConditionRecord`, `TripAttraction`, `Attraction`, `PushSubscription`

---

## Docs

| Folder | Contents |
|--------|----------|
| `docs/01-vision/` | Product vision |
| `docs/02-product/` | Feature specs |
| `docs/03-ai/` | AI system design |
| `docs/04-ux/` | UX / design |
| `docs/05-architecture/` | Architecture decisions |
| `docs/06-data/` | Data integrations |
| `docs/07-pilot/` | NZ pilot data |
| `docs/08-roadmap/` | Roadmap |
| `docs/plans/` | Implementation plans |
| `docs/svgs/` | ER diagrams, architecture diagrams |
