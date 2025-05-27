from typing import Self
from pydantic import model_validator
from pydantic_settings import BaseSettings
from mscore.settings import BaseAppSettings, DatabaseSettings


class ListingDatabaseSettings(BaseSettings):
    listing: DatabaseSettings


class AppSettings(BaseAppSettings):
    db: ListingDatabaseSettings

    @model_validator(mode="after")
    def auto_set_values(self) -> Self:
        """preset some values."""
        #
        self.db.listing.echo = self.db.listing.echo  # or self.ms.debug

        # set app name for database connection
        if self.db.listing.application_name == "":
            self.db.listing.application_name = self.ms.name
        return self
