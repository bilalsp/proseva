from fastapi import APIRouter

from mscore import create_app
from mscore.settings import get_settings
from mscore.lifespan_manager import LifespanManager
from mscore.db import DatabaseLifespan, PostgresDatabaseManager

from listing.settings import AppSettings
from listing.routers.v1 import v1_router


settings: AppSettings = get_settings(AppSettings)
lifespan = LifespanManager(
    [
        DatabaseLifespan(PostgresDatabaseManager(settings.db.listing)),
    ]
)

app = create_app(settings, lifespan=lifespan)

# router
api_router = APIRouter()
api_router.include_router(v1_router, prefix="/v1")

app.include_router(router=api_router)
