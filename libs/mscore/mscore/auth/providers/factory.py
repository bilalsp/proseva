from fastapi import FastAPI
from starlette.types import Lifespan

from mscore.auth.providers.keycloak.lifespan import KeycloakOpenIDLifespan
from mscore.auth.providers.keycloak.settings import KeycloakSettings


def get_auth_provider_lifespan(
    settings: KeycloakSettings, /, audience: str
) -> Lifespan[FastAPI]:
    match settings.provider:
        case "keycloak":
            return KeycloakOpenIDLifespan(settings, audience=audience)
        case _:
            raise RuntimeError(
                f"Unsupported authentication provider: " f"{settings.provider!r}"
            )
