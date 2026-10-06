from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from keycloak import KeycloakOpenID

from ._schemas import KeycloakState
from ._settings import KeycloakSettings


class KeycloakOpenIDLifespan:
    def __init__(self, settings: KeycloakSettings, /) -> None:
        # parameters of Keycloak OpenID client.
        self.params = settings.model_dump(
            exclude={"authorization_url", "token_url"},
            mode="json",
        )

    @asynccontextmanager
    async def __call__(self, app: FastAPI) -> AsyncIterator[dict[str, KeycloakState]]:
        # TODO: [INFO] use logger, initializing keycloak
        openid_client = KeycloakOpenID(**self.params)
        public_key = (
            "-----BEGIN PUBLIC KEY-----\n"
            f"{openid_client.public_key()}"
            "\n-----END PUBLIC KEY-----"
        )
        state = KeycloakState(openid_client=openid_client, public_key=public_key)
        yield {"keycloak": state}
        # TODO: [INFO] keycloak released...
