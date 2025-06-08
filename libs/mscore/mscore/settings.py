from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, TypeVar, cast

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .auth import KeycloakSettings
from .db import DatabaseSettings
from .exceptions import MSCoreUserError

TSettings = TypeVar("TSettings", bound=BaseSettings)


__all__ = [
    "MicroServiceSettings",
    "DatabaseSettings",
]


class Environment(str, Enum):
    DEVELOPMENT = "development"
    RELEASE = "release"
    PRODUCTION = "production"


class MicroServiceSettings(BaseSettings):
    name: Annotated[str, Field(description="Microservice's name.")]
    port: Annotated[
        int,
        Field(
            description="The port where the microservice will listen to serve incoming requests."
        ),
    ]
    num_workers: Annotated[
        int,
        Field(
            description="The number of worker processes to handle incoming requests concurrently."
        ),
    ] = 1
    environment: Annotated[
        Environment, Field(description="Microservice's environment.")
    ]
    log_level: Annotated[
        Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"],
        Field(
            description="Defines the minimum severity of log messages to be captured. "
            "Lower levels like 'DEBUG' or 'TRACE' are useful during development, "
            "while higher levels like 'ERROR' or 'CRITICAL' are better suited for production."
        ),
    ]
    reloading: Annotated[
        bool,
        Field(
            description="To enable auto-reloading on source code changes during development."
        ),
    ] = False
    debug: Annotated[
        bool,
        Field(
            description="To enable debugging on service to get verbose logs during development."
        ),
    ] = False


#
# db
#


class BaseAppSettings(BaseSettings):
    ms: MicroServiceSettings
    keycloak: KeycloakSettings

    model_config = SettingsConfigDict(
        extra="ignore", case_sensitive=False, env_nested_delimiter="__", env_file=".env"
    )


@lru_cache
def get_settings(
    settings_type: type[TSettings] | None = None,
    is_env_file_required: bool = True,
    **kwargs: Any,
) -> TSettings:
    if settings_type is None:
        settings_type = cast(type[TSettings], BaseAppSettings)

    if issubclass(settings_type, BaseAppSettings) is False:
        raise MSCoreUserError(
            "The `settings_type` argument must be a subclass of pydanitc `BaseSettings` class."
        )

    if is_env_file_required:
        env_file_path = Path(settings_type.model_config.get("env_file"))
        try:
            env_file_path.resolve(strict=True)
        except FileNotFoundError as ex:
            raise MSCoreUserError(f"File {env_file_path} is required.") from ex

    return settings_type(**kwargs)
