from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from keycloak import KeycloakOpenID

from ..settings import KeycloakSettings
from ._schemas import KeycloakState


class KeycloakOpenIDLifespan:
    def __init__(self, settings: KeycloakSettings, /) -> None:
        self.settings = settings.model_dump(
            exclude={"authorization_url", "token_url"},
            mode="json",
        )

    @asynccontextmanager
    async def __call__(self, app: FastAPI) -> AsyncIterator[dict[str, KeycloakState]]:
        # TODO: [INFO] use logger, initializing keycloak
        openid_client = KeycloakOpenID(**self.settings)
        public_key = (
            "-----BEGIN PUBLIC KEY-----\n"
            f"{openid_client.public_key()}"
            "\n-----END PUBLIC KEY-----"
        )
        yield {
            "keycloak": KeycloakState(
                openid_client=openid_client, public_key=public_key
            )
        }
        # TODO: [INFO] keycloak released...
