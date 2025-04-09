from typing import Annotated

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings

from mscore.security._errors import MSCoreUserError


class DatabaseSettings(BaseSettings):
    url: PostgresDsn
    pool_size: Annotated[
        int,
        Field(
            description="The number of connections to keep open inside the connection pool."
        ),
    ] = 5
    pool_recycle: Annotated[
        int,
        Field(
            description="When a connection is idle for `pool_recycle` seconds, it is closed and removed from the pool."
        ),
    ] = 300
    pool_pre_ping: Annotated[
        bool, Field(description="Check if a connection is still alive before using it.")
    ] = True
    max_overflow: Annotated[
        int,
        Field(
            description="Extra temporary connections beyond `pool_size` when demand spikes."
        ),
    ] = 0
    echo: Annotated[
        bool,
        Field(
            description="When echo=True, SQLAlchemy will print out all the SQL statements it executes."
        ),
    ] = False
    application_name: Annotated[
        str,
        Field(
            description="""Sets the application name to be reported in statistics and logs.
            The name will be displayed in the pg_stat_activity view.
            """
        ),
    ] = ""

    @field_validator("url")
    def check_db_name(cls, url: PostgresDsn) -> PostgresDsn:
        if not (url.path and len(url.path) > 1):
            raise MSCoreUserError("Database name must be provided.")
        return url
