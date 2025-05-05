from typing import Annotated

from fastapi import APIRouter, Query, Depends, Body, Request, status
from pydantic import BaseModel, Field

from mscore.utils import get_openapi_examples

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
) -> ListingCreateResDTO:
    """Create a new listing."""
    print("creating...")
    # 34/0
    res = await service.create_listing(dto=dto)
    print("created..")
    return res





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
    from mscore.errors import NotFoundError

    raise NotFoundError(detail=f"Listing not found #{id}")

    import http
    from fastapi import status, HTTPException
    # return str(req.url.scheme)

    detail = http.HTTPStatus(status.HTTP_404_NOT_FOUND).phrase.title()
    return detail
    # from pydantic import Field, create_model
    # fields = {
    #         "test": Annotated[
    #             str,
    #             Field(23),
    #         ]
    #     }
    # m = create_model('TEST', **fields)
    # print(m)

    return {"a": 333}
    raise HTTPException(status_code=404, detail="delte.")


@listing_router.patch("")
async def update_listing(id: Annotated[int, Query(description="Listing's Id.")]):
    """Update listing."""


@listing_router.delete("")
async def delete_listing(id: Annotated[int, Query(description="Listing's Id.")]):
    """Delete listing."""
