from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.logging import setup_logging

settings = get_settings()
setup_logging(settings.environment)
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("starting_up", environment=settings.environment)
    yield
    log.info("shutting_down")


app = FastAPI(
    title="Journey Buddi API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.exception("unhandled_error", path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}


from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.trips import router as trips_router
from app.api.conversations import router as conversations_router
from app.api.attractions import router as attractions_router
from app.api.itinerary import router as itinerary_router
from app.api.conditions import router as conditions_router
from app.api.briefings import router as briefings_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(trips_router, prefix="/api/v1")
app.include_router(conversations_router, prefix="/api/v1")
app.include_router(attractions_router, prefix="/api/v1")
app.include_router(itinerary_router, prefix="/api/v1")
app.include_router(conditions_router, prefix="/api/v1")
app.include_router(briefings_router, prefix="/api/v1")
