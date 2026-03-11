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
    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
]

_FOREIGN_PRE_CHAIN: list = [
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
]


class _ConsoleFilter(logging.Filter):
    """Only allow app.* loggers through at any level.

    Third-party loggers (uvicorn, sqlalchemy, etc.) are blocked below
    WARNING so their INFO/DEBUG noise stays out of stdout while the
    file handler captures everything.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if record.name.startswith("app"):
            return True
        return record.levelno >= logging.WARNING


def _make_console_formatter() -> structlog.stdlib.ProcessorFormatter:
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

    # ── console handler — INFO+, coloured, app.* only below WARNING ─────
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(_make_console_formatter())
    console_handler.addFilter(_ConsoleFilter())

    handlers: list[logging.Handler] = [console_handler]

    # ── file handler — DEBUG+, plain JSON, everything ───────────────────
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(_make_file_formatter())
        handlers.append(file_handler)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    for h in root.handlers[:]:
        root.removeHandler(h)
    for h in handlers:
        root.addHandler(h)

    logging.getLogger("app").setLevel(logging.DEBUG)

    # Uvicorn access logs: INFO so per-request lines reach the file.
    # The _ConsoleFilter keeps them off stdout.
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    # Truly noisy third-party loggers that produce nothing useful even
    # for the file at INFO.
    for name in (
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "sqlalchemy.dialects",
        "httpx",
        "openai",
        "httpcore",
        "watchfiles",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)
