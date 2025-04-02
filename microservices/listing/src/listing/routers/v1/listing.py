from typing import Annotated

from fastapi import APIRouter, Query, Depends, status

from listing.dto.requests import ListingCreateReqDTO
from listing.services import ListingService

listing_router = APIRouter()


@listing_router.post("", status_code=status.HTTP_201_CREATED)
async def create_listing(dto: ListingCreateReqDTO, service: ListingService = Depends()):
    """Create a new listing."""
    return await service.create_listing(dto=dto)


@listing_router.get("")
async def get_listing(id: Annotated[int, Query(description="Listing's Id.")]):
    """Get listing details."""


@listing_router.patch("")
async def update_listing(id: Annotated[int, Query(description="Listing's Id.")]):
    """Update listing."""


@listing_router.delete("")
async def delete_listing(id: Annotated[int, Query(description="Listing's Id.")]):
    """Delete listing."""
