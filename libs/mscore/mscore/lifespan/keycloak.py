from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI
from keycloak import KeycloakOpenID

from mscore.schemas import KeycloakState


class KeycloakOpenIDLifespan:
    def __init__(
        self,
        server_url: str,
        realm_name: str,
        client_id: str,
        client_secret_key: str | None = None,
        verify: bool | str = True,
        custom_headers: dict[str, Any] | None = None,
        proxies: dict[str, Any] | None = None,
        timeout: int = 60,
    ) -> None:
        self.openid_client_params = locals()
        self.openid_client_params.pop("self")

    @asynccontextmanager
    async def __call__(self, app: FastAPI) -> AsyncIterator[dict[str, KeycloakState]]:
        # TODO: [INFO] use logger, initializing keycloak
        openid_client = KeycloakOpenID(**self.openid_client_params)
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
