# Infrastructure

## MVP Infrastructure

For the MVP, simplicity and speed of deployment are prioritized. We use managed services wherever possible to minimize operational overhead for a two-person team.

### Hosting: Railway

**Why Railway:**
- One-click deployment from GitHub
- Managed PostgreSQL and Redis included
- Simple scaling (vertical and horizontal)
- Reasonable pricing for early stage
- Built-in CI/CD from git pushes
- Environment variable management
- Custom domain support

**Services on Railway:**
```
┌─────────────────────────────────────────┐
│           Railway Project                │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ Web Service (Next.js frontend)   │   │
│  │ Dockerfile / nixpack             │   │
│  │ Port: 3000                       │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ API Service (FastAPI backend)    │   │
│  │ Dockerfile                       │   │
│  │ Port: 8000                       │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ Worker Service (Celery)          │   │
│  │ Same image, different command    │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ Beat Service (Celery Beat)       │   │
│  │ Scheduler for periodic tasks     │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ PostgreSQL   │  │    Redis     │    │
│  │ (managed)    │  │  (managed)   │    │
│  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
```

### Docker Configuration

**Backend Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Celery Worker command:**
```bash
celery -A app.tasks worker --loglevel=info --concurrency=4
```

**Celery Beat command:**
```bash
celery -A app.tasks beat --loglevel=info
```

### Domain & SSL

- Custom domain: `journeybuddi.com` (to be acquired)
- SSL: Automatic via Railway (Let's Encrypt)
- API subdomain: `api.journeybuddi.com`
- Web: `www.journeybuddi.com` / `journeybuddi.com`

## Environment Configuration

### Environment Variables

```bash
# Application
APP_ENV=production
APP_SECRET_KEY=<random-secret>
APP_URL=https://journeybuddi.com
API_URL=https://api.journeybuddi.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/journey_buddi

# Redis
REDIS_URL=redis://host:6379/0

# AI / LLM
GEMINI_API_KEY=<key>
OPENAI_API_KEY=<key>  # Fallback

# External APIs
OPENWEATHERMAP_API_KEY=<key>
WORLDTIDES_API_KEY=<key>
MAPBOX_ACCESS_TOKEN=<key>

# Push Notifications
VAPID_PUBLIC_KEY=<key>
VAPID_PRIVATE_KEY=<key>

# Email (Magic Links)
SMTP_HOST=<host>
SMTP_PORT=587
SMTP_USER=<user>
SMTP_PASSWORD=<password>
FROM_EMAIL=hello@journeybuddi.com
```

### Secret Management

- **MVP**: Railway's built-in environment variable management
- **Production**: Migrate to AWS Secrets Manager or HashiCorp Vault

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run tests
        run: pytest backend/tests/
      
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci && npm test

  deploy:
    needs: [test, test-frontend]
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Railway
        # Railway auto-deploys on push to main
        # This step can trigger via Railway API if needed
        run: echo "Auto-deployed via Railway GitHub integration"
```

### Deployment Strategy

- **Main branch**: Auto-deploys to production
- **Feature branches**: Can deploy to Railway preview environments
- **Database migrations**: Run automatically on deploy (Alembic)
- **Zero-downtime**: Railway handles rolling deployments

## Monitoring & Observability

### Application Monitoring

**Structured Logging:**
```python
import structlog

logger = structlog.get_logger()

logger.info("briefing_generated", 
    trip_id=trip_id, 
    day_number=day_number, 
    generation_time_ms=elapsed,
    activities_count=len(activities)
)
```

### Key Metrics to Track

| Metric | Source | Alert Threshold |
|--------|--------|----------------|
| API response time (p95) | Application logs | > 500ms |
| AI response time | LLM SDK | > 10s first token |
| Error rate | Application logs | > 1% |
| Active WebSocket connections | Application | > 1000 |
| Background task queue depth | Celery/Redis | > 100 |
| Database connection pool | SQLAlchemy | > 80% utilized |
| External API failures | HTTP client | > 5% failure rate |
| LLM cost per day | Token tracking | > $50/day |

### Error Tracking

**Sentry** for error tracking:
- Captures unhandled exceptions with full context
- Tracks performance transactions
- Alerts on new/recurring errors
- Source maps for frontend errors

### Uptime Monitoring

Simple uptime check (e.g., UptimeRobot or Better Uptime):
- Health check endpoint: `GET /api/v1/health`
- Check every 5 minutes
- Alert via email/Slack on downtime

### Health Check Endpoint

```python
@app.get("/api/v1/health")
async def health_check():
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "celery": await check_celery_workers(),
    }
    
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "version": APP_VERSION
    }
```

## Backup Strategy

### Database Backups

- **Railway managed PostgreSQL**: Automatic daily backups with 7-day retention
- **Additional**: Weekly pg_dump to object storage (S3/GCS) for long-term retention
- **Recovery**: Test restoration monthly

### Application Data

- All code in GitHub (version controlled)
- Environment variables documented (not in code)
- Knowledge base data in version control or exportable from vector store

## Cost Estimation (MVP)

| Service | Estimated Monthly Cost |
|---------|----------------------|
| Railway (hosting) | $20-50 |
| Railway PostgreSQL | $5-20 |
| Railway Redis | $5-10 |
| Gemini API (LLM) | $50-200 (usage-based) |
| OpenWeatherMap API | $0-40 (free tier covers initial usage) |
| WorldTides API | $10-30 |
| Mapbox | $0 (free tier: 50K loads/month) |
| Email service (SMTP) | $0-15 |
| Domain | $15/year |
| Sentry | $0 (free tier) |
| **Total** | **~$100-400/month** |

Costs scale with user count and LLM usage. The LLM cost is the primary variable expense.

## Future Scale-Up Path

When the MVP grows beyond Railway's capabilities:

1. **AWS/GCP Migration:**
   - ECS/Cloud Run for containerized services
   - RDS/Cloud SQL for managed PostgreSQL
   - ElastiCache/Memorystore for managed Redis
   - S3/GCS for object storage
   - CloudFront/Cloud CDN for static assets

2. **Kubernetes (if needed):**
   - Auto-scaling based on active trip count
   - Separate node pools for API and workers
   - Managed Kubernetes (EKS/GKE) to reduce ops burden

3. **Multi-Region (eventual):**
   - Deploy in regions closest to active travelers
   - Edge caching for condition data
   - Database replication for read performance
