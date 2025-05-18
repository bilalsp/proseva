import inspect
import logging
import sys

from loguru import logger

from mscore.contexts import get_request_id
from mscore.settings import MicroServiceSettings

LOGURU_FORMAT = (
    "<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</g>"
    " | <level>{level: <8}</level>"
    " | <c>{request_id: <36}</c>"
    " | <level>{message}</level> <fg #808080>({name}:{function}:{line})</fg #808080>"
)
LIBRARY_NAME = "mscore"
logger.disable(LIBRARY_NAME)  # Disable logging for this library by default


class InterceptHandler(logging.Handler):
    """It is used to intercept the logs from standard logging library to loguru.

    References:
        [1] https://github.com/Delgan/loguru/tree/0.7.3?tab=readme-ov-file#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def record_patcher(record: dict) -> dict:
    record["request_id"] = get_request_id()
    return record


def setup_logging(settings: MicroServiceSettings) -> None:
    """Call this once in your app/script to set up loguru."""
    logger_config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "level": settings.log_level,
                "format": LOGURU_FORMAT,
                "enqueue": True,
                "backtrace": False,
                "diagnose": False,
            },
        ],
        "patcher": record_patcher,
    }

    logger.configure(**logger_config)

    # redirect logs from standard `logging` library to `loguru`
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.enable(LIBRARY_NAME)
