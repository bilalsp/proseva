from fastapi import APIRouter, Depends
from mscore.security.dependencies import get_token

test_router = APIRouter()


@test_router.get("/unprotected-endpoint")
async def unprotected_endpoint():
    ...


@test_router.get("/protected-endpoint", dependencies=[Depends(get_token)])
async def protected_endpoint():
    ...
