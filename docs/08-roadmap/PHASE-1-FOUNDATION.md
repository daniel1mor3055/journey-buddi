# Phase 1: Foundation — Weeks 1-3

## Goal

Set up the complete development environment, project structure, database, authentication, and basic frontend shell. At the end of Phase 1, we have a deployed application skeleton that a user can sign up for and access.

## Week 1: Project Setup & Backend Foundation

### Tasks

**Day 1-2: Repository & Project Structure**
- Initialize the monorepo structure:
  ```
  journey-buddi/
  ├── backend/          # Python FastAPI
  ├── frontend/         # Next.js
  ├── docs/             # Documentation (already done!)
  ├── docker-compose.yml
  └── .github/workflows/
  ```
- Set up Python virtual environment and install core dependencies
- Set up FastAPI application skeleton with health check endpoint
- Set up Next.js application with TypeScript and Tailwind CSS
- Configure Docker Compose for local development (PostgreSQL, Redis)
- Configure linting (Ruff for Python, ESLint/Prettier for TypeScript)

**Day 3-4: Database Setup**
- Install and configure SQLAlchemy + Alembic
- Create initial database models: User, Trip
- Write and run first Alembic migration
- Set up PostGIS extension
- Create seed data script
- Set up database connection pooling

**Day 5: Redis & Configuration**
- Set up Redis connection
- Configure environment variable management (python-dotenv for dev, env vars for prod)
- Create configuration module with validation (Pydantic Settings)
- Set up structured logging with structlog

### Deliverables
- Running FastAPI server with health check endpoint
- Running Next.js dev server
- PostgreSQL with initial schema
- Redis connected
- Docker Compose for one-command local development

## Week 2: Authentication & User API

### Tasks

**Day 1-2: Magic Link Authentication**
- Implement magic link generation endpoint
  - Generate secure token (JWT with 15-min expiry)
  - Store token in Redis with TTL
  - Send email with magic link (use a simple SMTP service, e.g., Resend or Mailgun)
- Implement token verification endpoint
  - Validate token
  - Create or get user
  - Return session JWT (30-day expiry)
- Implement JWT middleware for protected routes
- Implement session refresh endpoint

**Day 3-4: User & Trip APIs**
- User profile endpoint (GET/PATCH /users/me)
- Trip CRUD endpoints (POST, GET, PATCH, DELETE /trips)
- Input validation with Pydantic schemas
- Error handling middleware (consistent error format)
- Basic rate limiting (per-user, using Redis)

**Day 5: API Testing**
- Set up Pytest with async support
- Write tests for auth flow (magic link → verify → JWT)
- Write tests for user and trip CRUD
- Set up test database (separate from dev)

### Deliverables
- Working magic link auth flow
- User and Trip REST APIs
- API documentation auto-generated (FastAPI Swagger UI)
- Test suite passing

## Week 3: Frontend Shell & Deployment

### Tasks

**Day 1-2: Frontend Foundation**
- Set up Next.js app structure:
  ```
  frontend/
  ├── src/
  │   ├── app/
  │   │   ├── page.tsx          # Landing page
  │   │   ├── auth/
  │   │   │   └── page.tsx      # Magic link auth
  │   │   ├── dashboard/
  │   │   │   └── page.tsx      # User dashboard
  │   │   └── layout.tsx        # Root layout
  │   ├── components/
  │   │   ├── ui/               # Base UI components
  │   │   └── layout/           # Layout components
  │   ├── lib/
  │   │   ├── api.ts            # API client
  │   │   └── auth.ts           # Auth utilities
  │   └── stores/
  │       └── auth-store.ts     # Zustand auth store
  ```
- Implement design system basics (colors, typography, spacing from design-system.md)
- Build basic UI components: Button, Card, Input, Badge
- Set up API client with auth token management
- Set up Zustand stores for auth state

**Day 3: Auth UI & Flow**
- Build magic link auth page (email input → "check your email" → logged in)
- Implement auth token storage and refresh
- Build protected route wrapper (redirect to auth if not logged in)
- Build basic dashboard page (placeholder content)

**Day 4: Landing Page**
- Build responsive landing page with:
  - Hero section with destination imagery
  - Value proposition highlights
  - "Start Planning" CTA
  - Basic footer
- Mobile-responsive design

**Day 5: Deployment**
- Set up Railway project with all services
  - Web service (Next.js)
  - API service (FastAPI)
  - PostgreSQL (managed)
  - Redis (managed)
- Configure environment variables in Railway
- Set up custom domain (or use Railway-provided URL)
- Set up GitHub Actions for basic CI (run tests on PR)
- Verify deployment end-to-end (sign up → dashboard)

### Deliverables
- Landing page accessible at the public URL
- Working magic link auth flow (sign up → email → verify → dashboard)
- Dashboard page (authenticated, empty for now)
- CI pipeline running tests on push
- Production deployment on Railway

## Phase 1 Definition of Done

- [ ] A user can visit the public URL and see the landing page
- [ ] A user can enter their email and receive a magic link
- [ ] Clicking the magic link logs the user in and shows the dashboard
- [ ] The backend serves user and trip data from PostgreSQL
- [ ] Redis is connected and used for session/auth tokens
- [ ] The project is deployed on Railway
- [ ] CI runs tests on every push to main
- [ ] Code is clean, linted, and structured per the project layout

## Technical Decisions for Phase 1

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Package manager (Python) | pip + requirements.txt | Simple, no need for Poetry complexity yet |
| Package manager (JS) | npm | Standard, well-supported |
| ORM | SQLAlchemy 2.0 (async) | Mature, flexible, async support |
| Migration tool | Alembic | Standard with SQLAlchemy |
| Email service | Resend | Simple API, generous free tier, great DX |
| CSS framework | Tailwind CSS | Rapid development, consistent design tokens |
| State management | Zustand | Lightweight, simple, sufficient |
| HTTP client (frontend) | fetch + custom wrapper | No need for Axios overhead |
