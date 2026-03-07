import structlog
import logging


def setup_logging(environment: str = "development") -> None:
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if environment == "development":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Add a StreamHandler to the root logger (format "%(message)s" so structlog
    # controls all formatting).  In uvicorn's worker process, the root logger
    # starts with no handlers so basicConfig is NOT a no-op here.
    # Root at WARNING silences third-party libraries (SQLAlchemy, httpx, etc.)
    # by default without us having to enumerate every one of them.
    logging.basicConfig(format="%(message)s", level=logging.WARNING)

    # Re-enable app code at DEBUG so all structlog app events pass through.
    # structlog's filter_by_level processor respects per-logger effective levels.
    logging.getLogger("app").setLevel(logging.DEBUG)

    # Belt-and-suspenders: explicitly silence the noisiest third-party loggers
    # in case they ever configure themselves with their own handlers/levels.
    # Note: SQLAlchemy is also silenced via echo=False in database.py so it
    # cannot re-raise its engine logger to INFO regardless of this setting.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    # uvicorn.access: per-request "POST /api/v1/... 200 OK" lines — noise
    # uvicorn.error: server startup/restart INFO — app.main logs starting_up
    #   and shutting_down which covers what matters
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
