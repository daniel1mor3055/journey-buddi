import logging
import sys

import structlog


# Processors that run on every event before it reaches a handler.
# The final renderer is deliberately omitted here — each handler's
# ProcessorFormatter applies its own renderer so stdout and the log
# file can have different formats and log levels.
_SHARED_PROCESSORS: list = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.filter_by_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.UnicodeDecoder(),
    # Required bridge: wraps the event dict so ProcessorFormatter can
    # pick it up in each handler's formatter chain.
    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
]

# Processors that run only when an event arrives via stdlib (e.g., uvicorn,
# SQLAlchemy) rather than through structlog — they normalise the record so
# the final renderer sees a consistent event dict.
_FOREIGN_PRE_CHAIN: list = [
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
]


def _make_stdout_formatter() -> structlog.stdlib.ProcessorFormatter:
    return structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=_FOREIGN_PRE_CHAIN,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(),
        ],
    )


def _make_file_formatter() -> structlog.stdlib.ProcessorFormatter:
    return structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=_FOREIGN_PRE_CHAIN,
        processors=[
            structlog.processors.ExceptionRenderer(),
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )


def setup_logging(environment: str = "development", log_file: str = "") -> None:
    structlog.configure(
        processors=_SHARED_PROCESSORS,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # ── console handler — INFO+, coloured ConsoleRenderer ─────────────────
    # Use sys.stderr to match the original basicConfig behaviour (basicConfig
    # defaults to stderr, and uvicorn also writes there — keeps interleaving
    # identical to before).
    stdout_handler = logging.StreamHandler(sys.stderr)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(_make_stdout_formatter())

    handlers: list[logging.Handler] = [stdout_handler]

    # ── file handler — DEBUG+, plain JSON (no ANSI) ────────────────────────
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(_make_file_formatter())
        handlers.append(file_handler)

    # Root logger at WARNING: silences third-party libraries that have no
    # explicit level set (their effective level walks up to root = WARNING,
    # so INFO/DEBUG from e.g. httpcore, watchfiles, etc. never becomes a
    # LogRecord).  Propagated records from app.* loggers skip this check
    # (propagation calls callHandlers directly, not isEnabledFor), so
    # app.* DEBUG records DO reach the file handler via propagation.
    root = logging.getLogger()
    root.setLevel(logging.WARNING)
    for h in root.handlers[:]:
        root.removeHandler(h)
    for h in handlers:
        root.addHandler(h)

    # App loggers: DEBUG so all structlog app events pass through.
    logging.getLogger("app").setLevel(logging.DEBUG)

    # Silence noisy third-party loggers on both handlers.
    for name in (
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "sqlalchemy.dialects",
        "httpx",
        "openai",
        "uvicorn.access",
        "uvicorn.error",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)
