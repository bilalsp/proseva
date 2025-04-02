from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from mscore.db import get_db_session
from listing.dto.requests import ListingCreateReqDTO


class ListingDAO:
    def __init__(
        self, session: AsyncSession = Depends(get_db_session(db_name="listing"))
    ):
        self.session = session

    async def create_listing(self, dto: ListingCreateReqDTO):
        """Create a new listing."""
        result = await self.session.execute(text("SELECT 10*23;"))
        return result.scalar()
