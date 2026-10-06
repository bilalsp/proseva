from functools import lru_cache

from fastapi.security import OAuth2AuthorizationCodeBearer

from mscore.settings import BaseAppSettings, get_settings


@lru_cache
def get_oauth2_scheme() -> OAuth2AuthorizationCodeBearer:
    """It returns a cached instance of OAuth2AuthorizationCodeBearer.

    NOTE: Caching ensures it is created only once during the app lifecycle.
    """
    settings: BaseAppSettings = get_settings()
    return OAuth2AuthorizationCodeBearer(
        authorizationUrl=settings.auth_provider.authorization_url,
        tokenUrl=settings.auth_provider.token_url,
        auto_error=False,  # handle error manually
    )
