# Technology Stack

## Stack Overview

| Layer | Technology | Reasoning |
|-------|-----------|-----------|
| **Frontend** | Next.js (React) + TypeScript | SSR for landing page SEO, React ecosystem, TypeScript for safety |
| **Styling** | Tailwind CSS | Rapid development, consistent design tokens, mobile-first utilities |
| **Maps** | Mapbox GL JS | Beautiful maps, custom styling, route visualization, free tier for MVP |
| **Backend** | Python + FastAPI | Async support, excellent AI/ML ecosystem, rapid development |
| **AI/LLM** | Google Gemini (primary) | Strong reasoning, long context, competitive pricing, multimodal |
| **AI Framework** | LangChain | Agent orchestration, tool calling, conversation memory |
| **Database** | PostgreSQL + PostGIS | Robust, geospatial queries, JSON support, mature ecosystem |
| **Cache** | Redis | Session management, condition data caching, Celery broker |
| **Vector Store** | Chroma (MVP) → Pinecone (prod) | RAG retrieval for destination knowledge |
| **Task Queue** | Celery + Redis | Background jobs (briefings, monitoring, notifications) |
| **Auth** | Custom magic link (JWT) | Simple, no passwords, minimal friction |
| **Push Notifications** | Web Push API | PWA-compatible, no native app required |
| **Hosting** | Railway (MVP) | Simple deployment, managed services, affordable |
| **Version Control** | Git + GitHub | Standard, CI/CD integration |

## Frontend Stack Deep Dive

### Next.js 14+ (App Router)

**Why Next.js:**
- Server-side rendering for the landing page (SEO for organic discovery)
- App Router for modern React patterns (Server Components, Streaming)
- API routes as a lightweight BFF (Backend for Frontend) layer if needed
- Built-in image optimization for destination photography
- Excellent TypeScript support

**Key packages:**
```json
{
  "next": "latest",
  "react": "latest",
  "typescript": "latest",
  "tailwindcss": "latest",
  "mapbox-gl": "latest",
  "@tanstack/react-query": "latest",
  "zustand": "latest",
  "framer-motion": "latest",
  "lucide-react": "latest",
  "date-fns": "latest"
}
```

### State Management: Zustand

**Why Zustand over Redux:**
- Simpler API, less boilerplate
- Sufficient for our needs (trip state, UI state, auth state)
- Easy integration with React Query for server state

**State stores:**
- `authStore`: User session, profile
- `tripStore`: Active trip data, itinerary
- `chatStore`: Conversation messages, planning state
- `uiStore`: Navigation state, modals, preferences

### Data Fetching: React Query (TanStack Query)

**Why React Query:**
- Automatic caching and background refetching
- Optimistic updates for itinerary changes
- Infinite scroll support for chat history
- WebSocket integration for real-time data

### Animations: Framer Motion

**Usage:**
- Chat message entry animations (Buddi typing effect)
- Card expand/collapse transitions
- Page transitions
- Choice card selection feedback
- Swap suggestion before/after transition

## Backend Stack Deep Dive

### FastAPI

**Why FastAPI:**
- Native async support (critical for AI API calls and concurrent users)
- Automatic API documentation (OpenAPI/Swagger)
- Pydantic models for request/response validation
- WebSocket support for streaming chat
- Excellent Python ecosystem access (AI libraries, data processing)

**Key packages:**
```
fastapi
uvicorn
pydantic
sqlalchemy
alembic
celery
redis
python-jose[cryptography]  # JWT handling
httpx                      # Async HTTP client
langchain
google-generativeai        # Gemini SDK
chromadb                   # Vector store
psycopg2-binary           # PostgreSQL
geoalchemy2               # PostGIS integration
```

### Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Settings and environment
│   ├── api/
│   │   ├── auth.py             # Auth endpoints
│   │   ├── trips.py            # Trip CRUD endpoints
│   │   ├── itinerary.py        # Itinerary endpoints
│   │   ├── chat.py             # WebSocket chat endpoint
│   │   ├── conditions.py       # Condition data endpoints
│   │   └── deps.py             # Dependency injection
│   ├── services/
│   │   ├── ai_agent/
│   │   │   ├── planning_agent.py
│   │   │   ├── companion_agent.py
│   │   │   ├── chat_agent.py
│   │   │   └── tools.py        # Agent tools/functions
│   │   ├── condition_service.py
│   │   ├── itinerary_service.py
│   │   ├── knowledge_service.py
│   │   ├── notification_service.py
│   │   └── external_data/
│   │       ├── weather.py
│   │       ├── tides.py
│   │       ├── solar.py
│   │       └── maps.py
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── trip.py
│   │   ├── itinerary.py
│   │   ├── activity.py
│   │   └── conversation.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── trip.py
│   │   ├── itinerary.py
│   │   └── chat.py
│   ├── prompts/                # AI prompt templates
│   │   ├── planning_system.txt
│   │   ├── companion_system.txt
│   │   ├── briefing_task.txt
│   │   ├── swap_evaluation.txt
│   │   └── activity_guidance.txt
│   ├── knowledge/              # Knowledge base data
│   │   ├── nz/
│   │   │   ├── attractions.json
│   │   │   ├── tips.json
│   │   │   ├── stories.json
│   │   │   └── areas.json
│   │   └── loader.py
│   └── tasks/                  # Celery tasks
│       ├── briefing.py
│       ├── monitoring.py
│       └── notifications.py
├── migrations/                 # Alembic migrations
├── tests/
├── requirements.txt
└── Dockerfile
```

## Database

### PostgreSQL with PostGIS

**Why PostgreSQL:**
- Rock-solid reliability for user data
- PostGIS for geospatial queries (distance calculations, area lookups)
- JSON/JSONB columns for flexible data (itinerary details, AI responses)
- Full-text search for knowledge base backup
- Excellent ecosystem and hosting options

### Redis

**Usage:**
- **Condition data cache**: Weather forecasts, tide data (TTL-based expiry)
- **Session management**: User sessions and auth tokens
- **Celery broker**: Task queue message broker
- **Rate limiting**: API rate limit counters
- **Real-time data**: WebSocket session state

### Vector Store

**Chroma (MVP):**
- Embedded mode (runs in-process, no separate server)
- Perfect for development and small scale
- Persistent storage to disk
- Easy to set up and use with LangChain

**Pinecone (Production):**
- Managed service, zero ops
- Scales automatically
- Fast retrieval at any scale
- Metadata filtering for destination/category scoping

## External Services

### LLM Providers
- **Google Gemini**: Primary (via `google-generativeai` SDK)
- **OpenAI**: Fallback/comparison (via `openai` SDK)
- **Anthropic**: Optional fallback (via `anthropic` SDK)

### Hosting
- **Railway**: MVP deployment (simple, managed Postgres + Redis included)
- **Vercel**: Frontend hosting option (if decoupling frontend)
- **AWS/GCP**: Future scale-up

### External APIs
See [../06-data/DATA-INTEGRATIONS-OVERVIEW.md](../06-data/DATA-INTEGRATIONS-OVERVIEW.md) for complete list.

## Development Tools

| Tool | Purpose |
|------|---------|
| GitHub | Version control, issues, project management |
| GitHub Actions | CI/CD pipeline |
| Pytest | Python testing |
| Vitest | JavaScript/TypeScript testing |
| Ruff | Python linting and formatting |
| ESLint + Prettier | JavaScript/TypeScript linting and formatting |
| Docker | Local development and deployment containerization |
| Alembic | Database migrations |

## Performance Considerations

### API Response Times
- REST endpoints: < 200ms (p95)
- AI chat streaming: First token < 2 seconds
- Daily briefing generation: < 30 seconds (background)
- Condition assessment: < 5 seconds

### Scaling Strategy
1. **Vertical first**: Bigger instances handle more load simply
2. **Read replicas**: PostgreSQL read replicas for condition queries
3. **Worker scaling**: Add Celery workers for background job throughput
4. **CDN**: Static assets and images through CDN
5. **Horizontal**: Multiple API server instances behind a load balancer (FastAPI is stateless)
