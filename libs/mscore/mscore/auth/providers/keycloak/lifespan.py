from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from keycloak import KeycloakOpenID
from mscore.auth.providers.keycloak.jwks import KeycloakJwksProvider
from mscore.auth.providers.keycloak.settings import KeycloakSettings
from mscore.auth.providers.keycloak.validator import KeycloakTokenValidator
from mscore.auth.providers.state import AuthProviderState


class KeycloakOpenIDLifespan:
    def __init__(self, settings: KeycloakSettings, /, audience: str) -> None:
        # parameters of Keycloak OpenID client.
        self._params = settings.model_dump(
            mode="json",
            exclude={"provider"},
            exclude_computed_fields=True,
        )
        self._issuer = settings.issuer
        self._audience = audience

    @asynccontextmanager
    async def __call__(
        self, app: FastAPI
    ) -> AsyncGenerator[dict[str, AuthProviderState], None]:
        openid_client = KeycloakOpenID(**self._params)
        jwks = KeycloakJwksProvider(
            openid_client,
            ttl=300,  # TODO: make it configurable using settings
        )
        token_validator = KeycloakTokenValidator(
            jwks,
            issuer=self._issuer,
            audience=self._audience,
        )
        yield {"auth_provider": AuthProviderState(token_validator=token_validator)}
