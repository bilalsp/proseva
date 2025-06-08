from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer

from ..settings import BaseAppSettings, get_settings
from ..utils import get_openid_config


@lru_cache
def get_oauth2_scheme() -> OAuth2AuthorizationCodeBearer:
    """It returns a cached instance of OAuth2AuthorizationCodeBearer.

    NOTE: Caching ensures it is created only once during the app lifecycle.
    """
    settings: BaseAppSettings = get_settings()
    openid_config = get_openid_config(
        keycloak_server_url=settings.keycloak.server_url,
        realm_name=settings.keycloak.realm_name,
    )
    return OAuth2AuthorizationCodeBearer(
        authorizationUrl=openid_config["authorization_endpoint"],
        tokenUrl=openid_config["token_endpoint"],
        auto_error=False,  # handle error manually
    )


def get_token(token: Annotated[str | None, Depends(get_oauth2_scheme())]) -> str | None:
    """Dependency to extract the OAuth2 access token from the request.

    NOTE: If no token is present, it returns `None`.
    """
    return token
