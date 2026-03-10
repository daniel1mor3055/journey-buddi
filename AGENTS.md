# Journey Buddi — AGENTS.md

Project context for AI assistants. Keep this file up to date as the codebase evolves.

---

## What This Project Is

**Journey Buddi** is an AI-powered adaptive travel companion for extended adventure trips. It has two modes:

1. **Planning mode** — conversational AI (Buddi) collects trip preferences through a multi-agent pipeline and generates a day-by-day itinerary.
2. **Companion mode** — live companion during the trip that monitors weather/conditions, delivers daily briefings, and suggests itinerary swaps when conditions change.

**Pilot destination:** New Zealand.

**Target user:** The "Intentional Explorer" — 28–55, middle–upper class traveler who wants expert-level knowledge without the research burden. Anti-personas: weekend city trippers, package tourists.

**Core product principles:** Intelligence over information, adaptive not rigid, expert-level knowledge baked in, conversation over configuration.

---

## Architecture

| Layer | Tech |
|-------|------|
| Frontend | Next.js 16 (App Router) + React 19 + TypeScript + Tailwind CSS v4 |
| Backend | Python + FastAPI (fully async) |
| Database | PostgreSQL 16 + PostGIS 3.4 |
| Cache | Redis 7 |
| AI/Agents | OpenAI (`gpt-4.1-mini`) + `openai-agents` SDK |
| Task Queue | Celery + Redis (queues: monitoring, briefings, notifications) |
| Maps | Mapbox GL JS |
| Auth | Magic link (JWT, no passwords) |
| Notifications | Web Push (VAPID / pywebpush) |
| Email | Resend |
| Deployment | Railway (MVP) |
| CI | GitHub Actions (pytest + frontend lint/build on push/PR to main) |

---

## Monorepo Structure

```
journey-buddi/
├── backend/                    # FastAPI app
│   ├── app/
│   │   ├── agents/             # AI planning pipeline (core)
│   │   │   ├── context.py          # PlanningContext dataclass (shared mutable state)
│   │   │   ├── pipeline.py         # Agent definitions + PIPELINE list + FIELD_TOOLS
│   │   │   ├── orchestrator.py     # PlanningOrchestrator — drives agent transitions
│   │   │   ├── tools.py            # @function_tool functions (update context, return status)
│   │   │   ├── master.py           # MasterAgent — synthesises context → itinerary prompt
│   │   │   ├── models.py           # PlanningResponse pydantic model (choices, provider cards)
│   │   │   └── prompts.py          # BUDDI_PERSONA, QUESTION_PHILOSOPHY, RESPONSE_RULES
│   │   ├── api/                # Route handlers (one file per domain)
│   │   │   ├── auth.py             # Magic link + verify + refresh + logout
│   │   │   ├── users.py            # GET/PATCH /me
│   │   │   ├── trips.py            # CRUD + activate + complete
│   │   │   ├── conversations.py    # CRUD + messages + init + back + companion
│   │   │   ├── itinerary.py        # Overview, generate, days, swap
│   │   │   ├── briefings.py        # Daily briefings + generate + regenerate
│   │   │   ├── conditions.py       # Current + forecast + activity assessment
│   │   │   ├── swaps.py            # List + accept + decline
│   │   │   ├── attractions.py      # List + get + tips + seed
│   │   │   ├── notifications.py    # Push subscribe + unsubscribe + VAPID key
│   │   │   ├── ws.py               # WebSocket chat endpoint
│   │   │   └── deps.py             # FastAPI dependency injection (get_db, get_current_user)
│   │   ├── models/             # SQLAlchemy ORM models (11 models)
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic
│   │   │   ├── weather.py          # OpenWeatherMap + Open-Meteo
│   │   │   ├── solar.py            # Sunrise/sunset, golden hours, aurora Kp (astral + NOAA)
│   │   │   ├── tides.py            # Approximate tides from lunar calculations
│   │   │   ├── condition_scorer.py # Activity-aware condition scoring
│   │   │   ├── briefing_generator.py   # Daily briefing assembly + AI narrative
│   │   │   ├── swap_engine.py      # Weather-based day swap detection
│   │   │   ├── itinerary_generator.py  # Context → day-by-day itinerary
│   │   │   ├── companion_chat.py   # Live companion chat with context injection
│   │   │   ├── notifications.py    # Push notification sending
│   │   │   ├── openai_client.py    # OpenAI wrapper (generate, stream, JSON mode)
│   │   │   ├── gemini.py           # Gemini wrapper (same interface)
│   │   │   └── tell_me_more_options.py # "Tell me more" greeting copy
│   │   ├── data/               # Static NZ data
│   │   │   ├── activity_taxonomy.py    # 9 categories, 100+ activities, validation helpers
│   │   │   ├── nz_attractions.py       # Combined 75+ NZ attractions
│   │   │   ├── nz_attractions_adventure.py
│   │   │   ├── nz_attractions_nature.py
│   │   │   ├── nz_attractions_thermal.py
│   │   │   └── nz_attractions_cultural.py
│   │   ├── tasks/              # Celery background tasks
│   │   │   ├── briefings.py        # check_and_generate (every 5 min)
│   │   │   └── monitoring.py       # refresh_conditions (hourly), check_alerts (30 min)
│   │   ├── config.py           # Settings via pydantic-settings (.env)
│   │   ├── main.py             # FastAPI app entry + CORS + WebSocket mount
│   │   ├── database.py         # Async SQLAlchemy engine + session factory
│   │   ├── auth.py             # JWT + magic link token helpers
│   │   ├── celery_app.py       # Celery instance + beat schedule
│   │   └── redis.py            # Redis client
│   ├── migrations/             # Alembic migrations (5 revisions)
│   ├── tests/                  # pytest-asyncio tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router pages
│   │   │   ├── layout.tsx          # Root layout (Inter + JetBrains Mono fonts)
│   │   │   ├── page.tsx            # Landing page (hero, value props, how it works)
│   │   │   ├── auth/               # Magic link sign-in + verify
│   │   │   ├── plan/               # Planning conversation UI
│   │   │   ├── dashboard/          # Post-auth dashboard
│   │   │   └── trip/[tripId]/      # Live companion views
│   │   │       ├── page.tsx            # Trip itinerary overview
│   │   │       ├── today/page.tsx      # Daily briefing
│   │   │       ├── day/[dayNum]/page.tsx  # Day detail
│   │   │       ├── chat/page.tsx       # Companion chat
│   │   │       ├── map/page.tsx        # Mapbox route map
│   │   │       └── settings/page.tsx   # Trip settings
│   │   ├── components/
│   │   │   ├── layout/             # BottomTabBar
│   │   │   └── ui/                 # ConditionBadge
│   │   ├── stores/             # Zustand state management
│   │   │   ├── auth-store.ts       # User, magic link, JWT
│   │   │   ├── conversation-store.ts # Chat messages, planning state, progress
│   │   │   ├── trip-store.ts       # Trips, itinerary, days
│   │   │   └── companion-store.ts  # Briefings, conditions, swaps
│   │   └── lib/
│   │       ├── api.ts              # ApiClient (Bearer auth, 401 handling)
│   │       ├── utils.ts            # cn() class merge helper
│   │       └── push.ts             # Service worker + push subscription
│   └── package.json
├── docs/                       # 40+ spec documents (see Docs section)
├── scripts/                    # backend.sh, frontend.sh, setup.sh, reset.sh, stop.sh
├── postman/                    # Postman collection + environments (DEV/STG/PROD)
├── docker-compose.yml          # PostgreSQL 16 + PostGIS + Redis 7
└── logs/                       # Dev server logs
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

| # | Agent | Fields collected | Tools |
|---|-------|-----------------|-------|
| 1 | `greeting` | started | `get_tell_me_more_info` |
| 2 | `travel_dna` | group_type, group_details (count + ages), accessibility_needs, fitness_profile, budget | `set_group_type`, `set_group_count`, `set_group_ages`, `set_accessibility`, `set_fitness_profile`, `set_budget` |
| 3 | `logistics` | travel_dates, trip_duration, max_driving_hours | `set_travel_dates`, `set_trip_duration`, `set_max_driving_hours` |
| 4 | `interest_categories` | interest_categories | `set_interest_categories` |
| 5 | `island_preference` | island_preference | `get_island_analysis`, `set_island_preference` |
| 6 | `transport_route` | transport_plan, route_direction | `set_transport_mode`, `set_route_direction` |

### The 9 categories (strict — no additions):

Attractions, Tours, Day Trips, Outdoor Activities, Concerts & Shows, Events, Classes & Workshops, Transportation, Traveler Resources

### PlanningContext (`context.py`)

Dataclass serialized to `Conversation.planning_state` (JSONB) between turns:

```
Travel DNA:      group_type, group_details, accessibility_needs, fitness_profile, budget
Logistics:       destination, travel_dates, trip_duration, max_driving_hours
Interests:       interest_categories, interest_details, selected_providers
Island:          island_preference
Activity mapping: activity_locations, location_summary, days_per_location
Transport:       transport_plan, route_direction
Pipeline:        current_agent, completed_agents, started
```

Methods: `to_dict()`, `from_dict()` for JSON round-tripping.

### PlanningOrchestrator (`orchestrator.py`)

- `process_message(user_input, conversation)` — runs current agent, updates context, advances pipeline
- `init_conversation(conversation)` — sends greeting
- `progress_percent` — completion percentage
- `_advance_pipeline` — moves to next agent when current completes
- `_field_fallback` / `_try_direct_fill` — handles edge cases

### PlanningResponse (`models.py`)

The structured response format agents return:

```python
class PlanningResponse:
    text: str                           # Buddi's message
    choices: list[Choice] | None        # Emoji + label + desc
    multi_select: bool                  # Single vs multi-select
    free_text: bool                     # Show text input
    provider_cards: list[ProviderCard]  # Provider selection cards
```

### Buddi Persona (`prompts.py`)

- **Personality:** Warm, knowledgeable, opinionated, practical, calm, honest
- **Question philosophy:** Mostly closed questions with structured choices
- **Response rules:** Always use the choice/card format, never open-ended unless needed

---

## Companion Mode

Activates when a trip is set to "active" status. Provides daily awareness and adaptation.

### Daily Briefing Structure

Generated by `briefing_generator.py`, includes:

| Component | Source |
|-----------|--------|
| Weather summary | WeatherService (Open-Meteo + OpenWeatherMap) |
| Solar data | SolarService (sunrise/sunset, golden hours, moon phase via astral) |
| Activity condition reports | ConditionScorer (per-activity scoring with profiles) |
| Packing list | Weather-derived suggestions |
| Timeline | Scheduled activities with timing |
| AI narrative | OpenAI-generated natural language briefing |
| Hidden gem | Local recommendation |
| Lookahead | Next 2–3 days preview |
| Swap suggestion | SwapEngine (weather-based day swap recommendation) |

### Condition Scoring

Five-tier assessment: **EXCELLENT** (80–100) → **GOOD** (60–79) → **FAIR** (40–59) → **POOR** (20–39) → **UNSAFE** (0–19)

Activity profiles in `condition_scorer.py`: hiking, water sports, scenic, thermal, cultural — each with different weather sensitivity weights.

### Swap Engine (`swap_engine.py`)

Detects swap opportunities by comparing forecast quality across itinerary days. Produces `SwapSuggestion` records with `improvement_score`, `disruption_score`, and `recommendation`. Users accept or decline via the API.

### Celery Background Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| `check_and_generate` | Every 5 min | Generate daily briefings for active trips |
| `refresh_conditions` | Hourly | Refresh weather cache for active trip locations |
| `check_alerts` | Every 30 min | Compare current conditions to briefing, log severity changes |

---

## API Endpoints

All routes under `/api/v1`. Auth via Bearer JWT unless noted.

### Auth (`/auth`)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/magic-link` | Send magic link email |
| POST | `/verify` | Verify token → returns JWT + user |
| POST | `/refresh` | Refresh access token |
| POST | `/logout` | Logout (no-op server-side) |

### Users (`/users`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/me` | Get current user profile |
| PATCH | `/me` | Update name, preferences, profile |

### Trips (`/trips`)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/` | Create trip |
| GET | `/` | List user's trips |
| GET | `/{trip_id}` | Get trip |
| PATCH | `/{trip_id}` | Update trip |
| DELETE | `/{trip_id}` | Delete trip |
| POST | `/{trip_id}/activate` | planning/confirmed → active |
| POST | `/{trip_id}/complete` | active → completed |

### Conversations (`/conversations`)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/` | Create conversation for a trip |
| GET | `/` | List conversations (query: `trip_id`) |
| GET | `/{id}` | Get conversation with messages |
| POST | `/{id}/init` | Initialize with AI greeting |
| POST | `/{id}/messages` | Send planning message → returns `PlanningStepResponse` |
| POST | `/{id}/back` | Go back to previous agent |
| POST | `/{id}/companion` | Send companion-mode message |

### Itinerary (`/trips/{trip_id}/itinerary`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Itinerary overview (days, activity counts) |
| POST | `/generate` | AI-generate itinerary from planning state |
| GET | `/days` | List all days |
| GET | `/days/{day_number}` | Get single day with activities |
| PATCH | `/days/{day_number}` | Update day (title, notes, locked, etc.) |
| POST | `/swap` | Swap two days (day_a ↔ day_b) |

### Briefings (`/trips/{trip_id}/briefings`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | List all briefings |
| GET | `/today` | Today's briefing |
| GET | `/{day_number}` | Briefing for specific day |
| POST | `/generate` | Generate briefings (all or specific day) |
| POST | `/{day_number}/regenerate` | Force-regenerate a day's briefing |

### Conditions (`/conditions`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/current` | Current weather + solar at lat/lon |
| GET | `/forecast/{trip_id}` | Multi-day condition forecast |
| GET | `/assess` | Activity-specific condition assessment |

### Swaps (`/trips/{trip_id}/swaps`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | List swap suggestions (query: `status`) |
| GET | `/{swap_id}` | Get swap details |
| POST | `/{swap_id}/accept` | Accept swap |
| POST | `/{swap_id}/decline` | Decline swap |

### Attractions (`/attractions`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | List attractions (query: destination, region, types) |
| GET | `/{slug}` | Get attraction by slug |
| GET | `/{slug}/tips` | Get pro tips |
| POST | `/seed` | Seed NZ attractions from static data |

### Notifications (`/notifications`)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/subscribe` | Subscribe to web push |
| POST | `/unsubscribe` | Unsubscribe |
| GET | `/vapid-key` | Get VAPID public key |

### WebSocket

| Path | Purpose |
|------|---------|
| `/ws/chat/{conversation_id}?token=` | Real-time chat (planning or companion) |

### Health

| Path | Purpose |
|------|---------|
| `GET /health` | Health check |

---

## Database Models

PostgreSQL 16 + PostGIS. Async via `asyncpg` + SQLAlchemy 2.0. Migrations via Alembic (5 revisions).

### User (`users`)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| email | String(255) | unique, indexed |
| name | String(255) | nullable |
| preferences | JSONB | default `{}` |
| profile | JSONB | default `{}` |
| last_login_at | DateTime(TZ) | nullable |
| created_at, updated_at | DateTime(TZ) | auto |

### Trip (`trips`)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user_id | UUID | FK → users |
| destination | String(100) | e.g. "New Zealand" |
| destination_region | String(100) | nullable |
| status | String(20) | planning → confirmed → active → completed |
| start_date, end_date | Date | nullable |
| entry_point, exit_point | String(100) | nullable |
| transport_plan | JSONB | mode, details |
| flight_details | JSONB | |
| planning_state | JSONB | snapshot of PlanningContext |
| created_at, updated_at | DateTime(TZ) | auto |

### Conversation (`conversations`)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| trip_id | UUID | FK → trips |
| user_id | UUID | FK → users |
| conversation_type | String(20) | "planning" or "companion" |
| planning_step | String(50) | current pipeline step, default "GREETING" |
| planning_state | JSONB | serialized PlanningContext |
| is_active | Boolean | default True |

### Message (`messages`)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| conversation_id | UUID | FK → conversations |
| role | String(20) | user / assistant / system |
| content | Text | message body |
| message_type | String(30) | default "text" |
| metadata_ | JSONB | choices, cards, etc. |
| sort_order | Integer | ordering within conversation |

### ItineraryDay (`itinerary_days`)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| trip_id | UUID | FK → trips |
| day_number | Integer | 1-indexed |
| date | Date | nullable |
| location | String(255) | e.g. "Queenstown" |
| title, summary | String/Text | |
| day_type | String(20) | |
| is_flex_day | Boolean | weather-flexible day |
| is_arrival, is_departure | Boolean | |
| is_locked | Boolean | user-locked, skip swaps |
| accommodation, transport, weather | JSONB | structured data |
| condition_forecast | JSONB | latest forecast snapshot |

### ItineraryActivity (`itinerary_activities`)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| itinerary_day_id | UUID | FK → itinerary_days |
| attraction_id | UUID | FK → attractions, nullable |
| name | String(255) | activity name |
| emoji | String(10) | default "📍" |
| provider | String(255) | nullable |
| time_start, time_end | String(10) | "09:00" format |
| price | Float | default 0 |
| currency | String(10) | default "NZD" |
| booking_status | String(20) | not-booked / booked / confirmed |
| condition_score | Integer | nullable |
| sort_order | Integer | ordering within day |

### Attraction (`attractions`)

75+ NZ attractions with rich metadata:

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| destination | String(100) | indexed, e.g. "new-zealand" |
| region | String(100) | e.g. "otago" |
| name, slug | String(255) | slug is unique + indexed |
| category | String | TripAdvisor category, indexed |
| activity | String | specific activity type, indexed |
| types | ARRAY(String) | tags |
| location_name | String(255) | human-readable location |
| latitude, longitude | Float | geo coordinates |
| difficulty | String(20) | easy / moderate / hard / extreme |
| cost_level | String(20) | free / budget / moderate / premium / luxury |
| duration_min, duration_max | Float | hours |
| seasonal_availability | String | default "year-round" |
| booking_required | Boolean | |
| weather_sensitivity | String(20) | low / moderate / high / critical |
| ideal_conditions, acceptable_conditions, dealbreaker_conditions | JSONB | for condition scoring |
| logistics | JSONB | access, parking, facilities |
| pro_tips | JSONB | array of expert tips |
| uniqueness_score | Integer | 0–100 |

### DailyBriefing (`daily_briefings`)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| trip_id | UUID | FK → trips |
| day_id | UUID | FK → itinerary_days, nullable |
| day_number | Integer | |
| briefing_date | Date | |
| location | String(255) | |
| overall_score | Integer | 0–100 |
| overall_assessment | String(20) | EXCELLENT/GOOD/FAIR/POOR/UNSAFE |
| confidence | String(20) | high/medium/low |
| weather_summary, solar_data | JSONB | |
| activity_reports | JSONB | per-activity condition analysis |
| packing_list, timeline | JSONB | |
| hidden_gem | Text | |
| lookahead | JSONB | next 2–3 days preview |
| ai_narrative | Text | LLM-generated briefing text |
| swap_suggestion, conditions_snapshot | JSONB | |

### SwapSuggestion (`swap_suggestions`)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| trip_id | UUID | FK → trips |
| original_day, suggested_day | Integer | day numbers to swap |
| reason | Text | human-readable explanation |
| improvement_score | Integer | expected improvement |
| disruption_score | Integer | travel disruption cost |
| recommendation | String(30) | suggest_swap / keep_original |
| original_conditions, suggested_conditions, details | JSONB | |
| status | String(20) | pending / accepted / declined |

### ConditionRecord (`condition_records`)

Cached weather/condition data for locations:

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| location_lat, location_lon | Float | |
| recorded_at | DateTime(TZ) | |
| forecast_for | DateTime(TZ) | nullable |
| source | String(50) | provider name |
| data | JSONB | raw condition data |

### Other models: `TripAttraction` (join table), `PushSubscription` (web push endpoints)

---

## Frontend Pages & Routes

All pages are client components (`"use client"`). Auth-protected pages redirect to `/auth`.

| Route | Page | Purpose |
|-------|------|---------|
| `/` | Landing | Hero, value props, how it works, CTA → `/auth` |
| `/auth` | Sign In | Email input → magic link |
| `/auth/verify` | Verify | `?token=` → JWT → redirect to `/dashboard` |
| `/plan` | Planning Chat | Full-screen chat with Buddi: progress bar, choice cards, provider cards, free-text input |
| `/dashboard` | Dashboard | Post-auth home, list trips, "Plan a New Trip" |
| `/trip/[tripId]` | Trip Overview | Day list with condition dots, summary card, generate itinerary |
| `/trip/[tripId]/today` | Daily Briefing | Weather header, condition banner, activity cards, packing list, swap banner, hidden gem, lookahead |
| `/trip/[tripId]/day/[dayNum]` | Day Detail | Timeline, activities (expandable), accommodation, transport, prev/next navigation |
| `/trip/[tripId]/chat` | Companion Chat | Live chat with Buddi during trip |
| `/trip/[tripId]/map` | Map | Mapbox route map with day pins, condition colors, route line, popups |
| `/trip/[tripId]/settings` | Settings | Notification prefs, briefing schedule, emergency info |

### Bottom Tab Bar

Fixed bottom navigation on all `/trip/[tripId]/*` pages: **Today** · **Trip** · **Chat** · **Map** · **More**

---

## Frontend Stores (Zustand)

### `auth-store.ts`

| State | Type |
|-------|------|
| user | `{ id, email, name }` or null |
| isAuthenticated | boolean |
| isLoading | boolean |

Actions: `sendMagicLink(email)`, `verifyToken(token)`, `refreshSession()`, `logout()`, `initialize()`

### `conversation-store.ts`

| State | Type |
|-------|------|
| conversationId | string or null |
| messages | `ChatMessage[]` |
| planningStep | string |
| planningState | object |
| progressPercent | number |
| isLoading | boolean |

Types: `ChatMessage` (id, role, content, message_type, metadata_, sort_order, created_at), `ChoiceOption` (emoji, label, desc?), `ProviderCard` (emoji, name, location, rating, reviews, price, whatsSpecial, buddiPick?)

Actions: `createConversation(tripId)`, `initConversation(id)`, `sendMessage(id, content)`, `goBack(id)`, `reset()`

### `trip-store.ts`

| State | Type |
|-------|------|
| trips | `Trip[]` |
| currentTrip | `Trip` or null |
| itinerary | `ItineraryOverview` or null |
| isLoading | boolean |

Actions: `fetchTrips()`, `createTrip(data)`, `setCurrentTrip(trip)`, `fetchItinerary(tripId)`, `generateItinerary(tripId)`

### `companion-store.ts`

| State | Type |
|-------|------|
| briefings | `DailyBriefing[]` |
| currentBriefing | `DailyBriefing` or null |
| conditions | `DayConditionReport[]` |
| swaps | `SwapSuggestion[]` |
| isLoading | boolean |

Actions: `fetchBriefings(tripId)`, `generateBriefings(tripId, opts?)`, `fetchBriefing(tripId, day)`, `fetchConditions(tripId)`, `fetchSwaps(tripId)`, `handleSwap(tripId, swapId, action)`, `activateTrip(tripId)`, `reset()`

---

## Frontend Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| next | 16.1.6 | Framework |
| react / react-dom | 19.2.3 | UI |
| tailwindcss | ^4 | Styling (v4 CSS-based config, no tailwind.config.js) |
| zustand | ^5.0.11 | State management |
| framer-motion | ^12.34.3 | Animations |
| mapbox-gl | ^3.19.0 | Maps |
| lucide-react | ^0.575.0 | Icons |
| date-fns | ^4.1.0 | Date formatting |
| clsx | ^2.1.1 | Class merging |

### API Client (`lib/api.ts`)

`ApiClient` class with Bearer auth. Base URL from `NEXT_PUBLIC_API_URL` (default `http://localhost:8000/api/v1`). Token stored in memory + `localStorage`. Auto-clears token on 401. Methods: `get<T>`, `post<T>`, `patch<T>`, `delete`.

### Design System (`globals.css`)

Nature-inspired palette via CSS variables mapped to Tailwind:

| Token | Purpose |
|-------|---------|
| forest | Primary green |
| teal | Secondary accent |
| amber | Warm accent |
| leaf, bark, stone, driftwood, sand, mist, cloud | Neutral tones |
| gold, purple | Highlights |
| excellent, good, fair, poor, unsafe | Condition assessment colors |

Fonts: Inter (sans), JetBrains Mono (mono).

---

## External Services & Data Sources

| Service | Purpose | Cache TTL |
|---------|---------|-----------|
| OpenWeatherMap (One Call 3.0) | Primary weather | Redis |
| Open-Meteo | Fallback weather | Redis |
| astral (Python lib) | Sunrise/sunset, golden hours, moon phase | — |
| NOAA Space Weather | Aurora Kp index | Redis |
| Lunar calculations | Approximate tides for NZ | Redis |
| Mapbox GL JS | Maps + route display | — |
| Resend | Magic link emails | — |
| OpenAI (gpt-4.1-mini) | Agent pipeline, briefing narratives, companion chat | — |

---

## Static NZ Data

### Activity Taxonomy (`data/activity_taxonomy.py`)

9 TripAdvisor-aligned categories with 100+ activities. Helpers: `get_category()`, `get_activity()`, `get_activities_for_category()`, `get_category_slug_for_label()`, `validate_attraction_tags()`.

### NZ Attractions (`data/nz_attractions*.py`)

75+ attractions split across 5 files (core, adventure, nature, thermal, cultural). Each attraction includes: name, slug, description, types, location (name + lat/lon), difficulty, cost, duration, seasonal availability, weather sensitivity, ideal/acceptable/dealbreaker conditions, logistics (access, parking, facilities), pro tips, uniqueness score.

Seeded to the database via `POST /attractions/seed`.

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
# → http://localhost:8000 (API docs at /docs)
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

### Full setup from scratch
```bash
./scripts/setup.sh    # Docker + deps + migrations + optional .env
```

### Full reset
```bash
./scripts/reset.sh    # Destroys everything and rebuilds
```

### Stop all services
```bash
./scripts/stop.sh     # Kills backend, frontend, Docker containers
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
VAPID_CLAIMS_EMAIL=...
ENVIRONMENT=development
```

Frontend: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_MAPBOX_TOKEN`

---

## Key Conventions

### Python
- **Always use `venv/bin/python3`**, never global `python`. Never `source activate`.
- Async throughout (FastAPI + asyncpg + SQLAlchemy async).
- Structured logging via `structlog`.
- Settings via `pydantic-settings` (`app/config.py`), loaded once with `@lru_cache`.
- Tests: `pytest-asyncio` (`asyncio_mode = auto`), fixtures in `conftest.py`. Use `AsyncClient` with `ASGITransport` for API tests.

### TypeScript / Next.js
- App Router (not Pages Router). All pages are client components.
- State management: Zustand stores in `src/stores/`.
- No passwords — auth is magic link only.
- Path alias: `@/*` → `./src/*`.
- Tailwind v4 — config lives in CSS (`globals.css`), not `tailwind.config.js`.

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

## Alembic Migrations

5 revisions in `backend/migrations/`:

| Revision | Name | Changes |
|----------|------|---------|
| `0bdfca592133` | initial_users_and_trips | `users`, `trips` tables |
| `ea982cd4a3f5` | add_phase_2_models | `attractions`, `conversations`, `itinerary_days`, `itinerary_activities`, `messages` |
| `d3e967e5838a` | add_phase_3_models | `daily_briefings`, `swap_suggestions` |
| `b66adfb67d27` | phase_3_alignment | `condition_records`, `push_subscriptions` + column additions |
| `7ca4d3aefe6a` | add_category_and_activity_columns | `category`, `activity` on `attractions` with indexes |

Config: `backend/alembic.ini` → `script_location = migrations`. `env.py` uses `settings.sync_database_url`, imports all models, excludes PostGIS system tables.

---

## Tests

`pytest-asyncio` with `asyncio_mode = auto`. Fixtures in `conftest.py`: `event_loop`, `client` (AsyncClient + ASGITransport), `test_email`, `magic_link_token`, `auth_headers`.

| File | Coverage |
|------|----------|
| `test_health.py` | Health check endpoint |
| `test_auth.py` | Magic link request, token create/verify/decode, invalid tokens |
| `test_trips.py` | Auth-required guards for list/create |
| `test_agents.py` | PlanningContext (4), PlanningResponse (3), status helpers (10), constants (2), pipeline (6), orchestrator (7), MasterAgent (3) |
| `test_activity_taxonomy.py` | Registry (7), attraction tags (5), canonical categories (2), location normalization (2) |

---

## Docs

40+ documents organized by domain:

| Folder | Contents |
|--------|----------|
| `docs/01-vision/` | Product vision, target audience, competitive analysis |
| `docs/02-product/` | Feature specs: planning phase, conversation flow, itinerary generation, live companion, daily briefing, condition monitoring, itinerary adaptation, notifications, activity guidance, transport logic |
| `docs/03-ai/` | AI agent overview, Buddi persona, conversation design, prompt architecture, knowledge system, decision engine |
| `docs/04-ux/` | UX overview, design principles, design system, screen flows, user journey map, mobile considerations |
| `docs/05-architecture/` | System architecture, API design, tech stack, data model, infrastructure, real-time system |
| `docs/06-data/` | Data integrations: weather, tides, solar, maps/routing, destination knowledge base, wildlife data |
| `docs/07-pilot/` | NZ overview, North Island, South Island, weather patterns, transport guide, attractions database |
| `docs/08-roadmap/` | 5-phase roadmap: foundation → planning AI → live companion → polish & launch → expansion |
| `docs/plans/` | Implementation plans |
| `docs/svgs/` | ER diagrams, architecture diagrams, user journey diagrams |
| `docs/GLOSSARY.md` | Product and technical glossary |

---

## Postman Collection

Collection: "Journey Buddi API" with folder structure mirroring API domains.

**Folders:** Health, Auth, Users, Trips, Conversations, Attractions, Itinerary, Conditions, Briefings

**Environments:** DEV (localhost:8000), STG, PROD

**Variables:** `base_url`, `access_token` (auto-set by Verify Magic Link test script), `trip_id`, `conversation_id`, `swap_id`, `attraction_slug`, `day_number`, `user_email`
