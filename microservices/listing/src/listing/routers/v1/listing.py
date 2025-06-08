from typing import Annotated

from fastapi import APIRouter, Query, Depends, Body, Request, status
from pydantic import BaseModel, Field

from mscore.utils import get_openapi_examples
from mscore.auth import get_token

from listing.dto.requests import ListingCreateReqDTO
from listing.dto.responses import ListingCreateResDTO
from listing.services import ListingService

listing_router = APIRouter()


@listing_router.post("", status_code=status.HTTP_201_CREATED)
async def create_listing(
    dto: Annotated[
        ListingCreateReqDTO,
        Body(
            ...,
            openapi_examples=get_openapi_examples("v1_listing_post"),
            description="Request body to create a lisiting.",
        ),
    ],
    service: Annotated[ListingService, Depends()],
    token: str = Depends(get_token),
) -> ListingCreateResDTO:
    """Create a new listing."""
    return await service.create_listing(dto=dto)


class Message(BaseModel):
    message: str = Field(..., examples=["KeyError"])


@listing_router.get(
    "",
    responses={
        400: {
            "description": "400 error description",
            "model": Message,
            "content": {
                "application/json": {
                    "example": {"message": "error_message_@"},
                },
                "application/problem+json": {
                    "schema": Message.model_json_schema(),
                    "example": {"message": "error_message__problem"},
                },
            },
        },
    },
)
async def get_listing(
    req: Request, id: Annotated[int, Query(description="Listing's Id.")]
):
    """Get listing details."""


@listing_router.patch("")
async def update_listing(id: Annotated[int, Query(description="Listing's Id.")]):
    """Update listing."""


@listing_router.delete("")
async def delete_listing(id: Annotated[int, Query(description="Listing's Id.")]):
    """Delete listing."""
