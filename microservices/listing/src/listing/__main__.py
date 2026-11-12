import uvicorn

from mscore.settings import get_settings
from listing.settings import AppSettings

settings: AppSettings = get_settings(AppSettings)


def runserver():
    # setup logging just before starting the server to make sure no library overwrites it
    # setup_logging(settings=settings.ms)

    uvicorn.run(
        app="listing.app:app",
        host="0.0.0.0",
        port=settings.ms.port,
        reload=settings.ms.reloading,
        reload_delay=1.0,
        reload_dirs=["src", "/opt/proseva/libs/mscore/mscore"],
        # proxy_headers=True,
        # forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    runserver()
