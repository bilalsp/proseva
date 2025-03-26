from fastapi import APIRouter

from mscore import create_app
from mscore.settings import AppSettings, get_settings
from iam.routers.v1 import v1_router


settings: AppSettings = get_settings(AppSettings)
app = create_app(settings)

# router
api_router = APIRouter()
api_router.include_router(v1_router, prefix="/v1")

app.include_router(router=api_router)
