from mscore import create_app
from mscore.settings import get_settings
from mscore.lifespan_manager import LifespanManager
from mscore.monitoring.health import db_check
from mscore.db import DatabaseLifespan, PostgresDatabaseManager

from listing.settings import AppSettings
from listing.routers.v1 import v1_router


settings: AppSettings = get_settings(AppSettings)
lifespan = LifespanManager(
    [
        DatabaseLifespan(PostgresDatabaseManager(settings.db.listing)),
    ]
)

app = create_app(
    settings,
    lifespan=lifespan,
    health_checks=[db_check(db_name="listing")],
)

# routers
app.include_router(v1_router, prefix="/api/v1")
