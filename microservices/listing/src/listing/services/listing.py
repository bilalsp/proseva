from fastapi import Depends

from listing.dao import ListingDAO
from listing.dto.requests import ListingCreateReqDTO
from listing.dto.responses import ListingCreateResDTO


class ListingService:
    def __init__(self, dao: ListingDAO = Depends()) -> None:
        self.dao = dao

    async def create_listing(self, dto: ListingCreateReqDTO) -> ListingCreateResDTO:
        """Create a new listing."""
        return await self.dao.create_listing(dto=dto)
