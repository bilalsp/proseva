from gunicorn.arbiter import Arbiter

from mscore.logging import setup_logging
from mscore.settings import get_settings

from listing.settings import AppSettings


settings: AppSettings = get_settings(AppSettings)

# listing application will listen for incoming HTTP requests on a network IP/port
bind = f"0.0.0.0:{settings.ms.port}"

# Worker settings
workers = (
    settings.ms.num_workers
)  # Recommended formula: multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"  # For FastAPI + ASGI

# Timeouts
timeout = 30  # Kill workers if they hang for more than 30s
graceful_timeout = 30  # Graceful restart timeout

# Daemonize (usually False if using systemd or Docker to run the application in foreground)
daemon = False

# Logging
accesslog = "-"  # log to stdout
errorlog = "-"  # log to stderr


def on_starting(server: Arbiter) -> None:
    """It is a lifecycle event hook that is called just before the Gunicorn master process is initialized.

    NOTE: It is used to perform early setup tasks that must be done before workers are created/forked
    — such as logging, metrics setup, environment validation etc..
    """
    # setup logging at the end to make sure no library overwrites it
    setup_logging(settings=settings.ms)
    server.log.info("Loguru logging has been configured by gunicorn_config.")
