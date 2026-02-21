# System Architecture

## Architecture Overview

Journey Buddi follows a modular monolith architecture for the MVP, designed to be decomposed into microservices as the system scales. The initial architecture prioritizes development speed and simplicity while maintaining clean boundaries between domains.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │   Web App (PWA)   │  │  Mobile App      │                    │
│  │   Next.js / React │  │  (Future)        │                    │
│  └────────┬─────────┘  └────────┬─────────┘                    │
│           │                     │                                │
└───────────┼─────────────────────┼────────────────────────────────┘
            │                     │
            ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                               │
│                     (FastAPI Application)                         │
│                                                                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │
│  │  Auth  │ │  Trip  │ │  Chat  │ │Itiner- │ │Condit- │       │
│  │  API   │ │  API   │ │  API   │ │ary API │ │ion API │       │
│  └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘       │
│       │          │          │          │          │              │
└───────┼──────────┼──────────┼──────────┼──────────┼──────────────┘
        │          │          │          │          │
        ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                               │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ AI Agent    │  │ Condition   │  │ Itinerary   │            │
│  │ Service     │  │ Service     │  │ Service     │            │
│  │             │  │             │  │             │            │
│  │ - Planning  │  │ - Weather   │  │ - Generate  │            │
│  │ - Companion │  │ - Tides     │  │ - Optimize  │            │
│  │ - Chat      │  │ - Solar     │  │ - Adapt     │            │
│  │ - Guidance  │  │ - Scoring   │  │ - CRUD      │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                     │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐            │
│  │ Knowledge   │  │ External   │  │ Notification │            │
│  │ Service     │  │ Data       │  │ Service      │            │
│  │             │  │ Service    │  │              │            │
│  │ - RAG       │  │            │  │ - Push       │            │
│  │ - Embeddings│  │ - API calls│  │ - Email      │            │
│  │ - Search    │  │ - Caching  │  │ - Scheduling │            │
│  └─────────────┘  └────────────┘  └──────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
        │                │                │
        ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │PostgreSQL│  │  Redis   │  │  Vector  │  │  Object  │       │
│  │+ PostGIS │  │          │  │  Store   │  │  Store   │       │
│  │          │  │          │  │ (Chroma/ │  │  (S3)    │       │
│  │Users     │  │Cache     │  │ Pinecone)│  │          │       │
│  │Trips     │  │Sessions  │  │          │  │Images    │       │
│  │Itinerary │  │Conditions│  │Knowledge │  │Exports   │       │
│  │Profiles  │  │Rate Limit│  │Embeddings│  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Client Layer

**Web Application (Next.js)**
- Server-side rendering for landing page (SEO)
- Client-side React for the app experience
- PWA capabilities (service worker, offline, install)
- WebSocket connection for real-time chat streaming

### API Gateway (FastAPI)

Single FastAPI application serving all endpoints:

- **Auth API**: Magic link generation, token validation, session management
- **Trip API**: Trip CRUD, trip state management
- **Chat API**: WebSocket endpoint for AI conversations, REST for message history
- **Itinerary API**: Itinerary CRUD, day/activity management
- **Condition API**: Current conditions, forecasts, condition assessments

### Service Layer

**AI Agent Service**
- Manages LLM interactions (prompt construction, API calls, response parsing)
- Maintains conversation state and context
- Implements tool/function calling for data access
- Handles streaming responses to the client
- Rate limiting and cost tracking per user

**Condition Service**
- Fetches and normalizes data from external weather/tide/solar APIs
- Caches condition data with appropriate TTLs
- Scores conditions against activity requirements
- Generates condition reports for daily briefings
- Triggers alerts when conditions cross thresholds

**Itinerary Service**
- Generates itineraries from user selections (planning phase)
- Manages day-by-day itinerary state
- Evaluates swap opportunities
- Handles itinerary modifications and re-optimization

**Knowledge Service**
- Manages the destination knowledge base
- Handles vector embedding and storage
- Performs RAG retrieval for AI context augmentation
- Provides structured attraction data

**External Data Service**
- Wrapper around all external API calls
- Handles API key management, rate limiting, error handling
- Normalizes data from different providers into internal format
- Implements retry logic and fallbacks

**Notification Service**
- Schedules notifications based on user timezone and preferences
- Generates notification content (using AI Agent Service)
- Delivers via web push (PWA) or native push (future)
- Manages notification history and user preferences

## Data Flow Examples

### Planning Conversation

```
User selects interest → Frontend sends to Chat API (WebSocket)
  → AI Agent Service constructs prompt with profile + destination context
  → Knowledge Service retrieves relevant attraction data (RAG)
  → LLM generates response with options
  → Response streamed back through WebSocket
  → Frontend renders Buddi's message + choice cards
  → User selects → Frontend sends selection
  → Conversation state updated in database
  → Loop continues...
```

### Morning Briefing Generation

```
Scheduled job triggers at user's configured time
  → Itinerary Service retrieves today's plan
  → Condition Service fetches latest conditions for today's locations
  → Condition Service scores each activity
  → If any activity scores FAIR or below:
      → Itinerary Service evaluates swap opportunities
  → AI Agent Service generates briefing content
      → Knowledge Service provides activity-specific tips (RAG)
      → Prompt includes: plan + conditions + profile + knowledge
  → Notification Service delivers push notification
  → Full briefing stored for in-app access
```

### Swap Evaluation

```
Condition monitoring detects degradation for Day N activity
  → Condition Service generates condition report for Days N through N+5
  → Itinerary Service identifies swap candidates
  → For each candidate swap:
      → Score condition improvement
      → Evaluate logistics impact
      → Calculate disruption score
  → If best swap exceeds threshold:
      → AI Agent Service generates swap suggestion narrative
      → Notification Service delivers swap suggestion
  → User accepts/declines
  → If accepted: Itinerary Service updates plan, regenerates affected briefings
```

## Communication Patterns

### Synchronous (REST)
- All CRUD operations
- Auth operations
- Condition data retrieval
- Itinerary management

### Streaming (WebSocket)
- AI chat responses (token-by-token streaming for natural feel)
- Real-time condition updates (when app is active)

### Async (Background Jobs)
- Morning briefing generation
- Condition monitoring and alerting
- Knowledge base updates
- Notification scheduling and delivery

### Background Task Queue

Using Celery with Redis as broker:

| Task | Frequency | Priority |
|------|-----------|----------|
| Generate morning briefing | Daily per active trip | High |
| Condition monitoring check | Every 3 hours per active trip | Medium |
| Swap evaluation | When conditions change significantly | High |
| Knowledge base enrichment | On-demand / weekly | Low |
| Notification delivery | Scheduled per user | High |
| Condition data refresh | Every 1-6 hours by data type | Medium |

## Security Considerations

### Authentication
- Magic link tokens: JWT with 15-minute expiry
- Session tokens: JWT with 30-day expiry, stored in httpOnly cookies
- No passwords stored — magic link only

### Authorization
- Users can only access their own trips and data
- No admin interface for MVP (database-direct for admin tasks)

### Data Protection
- All external API keys stored in environment variables / secret manager
- User data encrypted at rest (PostgreSQL encryption)
- HTTPS for all communications
- No sensitive data in logs

### API Rate Limiting
- Per-user rate limits on all endpoints
- LLM call rate limits to prevent abuse and cost overrun
- External API call rate limits to stay within provider quotas

## Deployment Architecture

### MVP Deployment
```
┌──────────────────────────────────┐
│  Hosting Platform                │
│  (Railway / Render / Fly.io)     │
│                                  │
│  ┌────────────────────────────┐ │
│  │ Web Server (Next.js)       │ │
│  │ + FastAPI Backend           │ │
│  └────────────────────────────┘ │
│  ┌────────────────────────────┐ │
│  │ PostgreSQL                  │ │
│  └────────────────────────────┘ │
│  ┌────────────────────────────┐ │
│  │ Redis                       │ │
│  └────────────────────────────┘ │
│  ┌────────────────────────────┐ │
│  │ Celery Worker               │ │
│  └────────────────────────────┘ │
└──────────────────────────────────┘
```

### Scale-Up Architecture (Future)
- Container orchestration (Kubernetes or equivalent)
- Separate frontend and backend deployments
- Managed database (AWS RDS / GCP Cloud SQL)
- Managed Redis (ElastiCache / Memorystore)
- CDN for static assets
- Managed vector database (Pinecone)
