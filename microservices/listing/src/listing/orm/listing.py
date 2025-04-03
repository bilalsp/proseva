from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa

from .base import BaseModel


class ListingModel(BaseModel):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(sa.String(250), nullable=False)
