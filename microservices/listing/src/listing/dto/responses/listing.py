from pydantic import BaseModel, Field


class ListingCreateResDTO(BaseModel):
    id: int = Field(..., description="Listing's id.")
