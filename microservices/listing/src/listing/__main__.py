import uvicorn

from mscore.settings import get_settings
from mscore.logging import setup_logging, get_logger
from listing.settings import AppSettings

settings: AppSettings = get_settings(AppSettings)
logger = get_logger()


def runserver():
    # setup logging just before starting the server to make sure no library overwrites it
    setup_logging(settings=settings.ms)

    uvicorn.run(
        app="listing.app:app",
        host="0.0.0.0",
        port=settings.ms.port,
        reload=settings.ms.reloading,
        reload_dirs=["src", "/opt/proseva/libs/mscore/mscore"],
    )


if __name__ == "__main__":
    runserver()
