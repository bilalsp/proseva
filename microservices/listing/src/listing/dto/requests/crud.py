from pydantic import BaseModel, Field


class ListingCreateReqDTO(BaseModel):
    title: str = Field(..., min_length=10, max_length=120)
    # description: str = Field(..., max_length=2000)
    # category_id: int
    # base_price: float = Field(..., gt=0)
    # pricing_model: str
    # service_area_pincodes: list[str]


# class Listing(Base):
#     __tablename__ = "listings"

#     id = Column(UUID(as_uuid=True), primary_key=True, index=True)
#     title = Column(String(120), nullable=False)
#     description = Column(String(2000), nullable=False)


#     professional_id = Column(UUID(as_uuid=True), nullable=False)

#     category_id = Column(Integer, nullable=False)
#     base_price = Column(Float, nullable=False)
#     pricing_model = Column(String(50), nullable=False)
#     service_area_pincodes = Column(ARRAY(String(10)), nullable=False)
#     status = Column(Enum(ListingStatus), default=ListingStatus.DRAFT)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
