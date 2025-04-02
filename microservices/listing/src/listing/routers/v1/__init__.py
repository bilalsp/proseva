from fastapi import APIRouter

from .listing import listing_router

v1_router = APIRouter()
v1_router.include_router(listing_router, prefix="/listing", tags=["Listing"])

__all__ = ["v1_router"]
