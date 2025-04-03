from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from mscore.db import get_db_session

from listing.dto.requests import ListingCreateReqDTO
from listing.dto.responses import ListingCreateResDTO
from listing.orm import ListingModel


class ListingDAO:
    def __init__(
        self, session: Annotated[AsyncSession, Depends(get_db_session(db_name="listing"))]
    ):
        self.session = session

    async def create_listing(self, dto: ListingCreateReqDTO) -> ListingCreateResDTO:
        """Create a new listing."""
        listing = ListingModel(**dto.model_dump())
        self.session.add(listing)
        await self.session.commit()
        return ListingCreateResDTO(id=listing.id)
