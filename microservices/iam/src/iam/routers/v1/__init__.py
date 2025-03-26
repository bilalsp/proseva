from fastapi import APIRouter

from .user import test_router

v1_router = APIRouter()
v1_router.include_router(test_router, prefix="/user", tags=["User"])
