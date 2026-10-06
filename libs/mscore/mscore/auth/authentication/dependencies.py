from typing import Annotated

from fastapi import Depends, Request

from mscore.auth.authentication.schemes import get_oauth2_scheme
from mscore.auth.exceptions import TokenValidationError, UnauthorizedError
from mscore.auth.models import AccessToken
from mscore.auth.providers.protocols import TokenValidator
from mscore.auth.providers.state import AuthProviderState


def get_raw_access_token(
    token: Annotated[str | None, Depends(get_oauth2_scheme())],
) -> str | None:
    """Dependency to extract the OAuth2 access token from the request.

    Returns:
        If no token is present, it returns `None`.
    """
    return token


def get_token_validator(request: Request) -> TokenValidator:
    """Return the token validator from the current request's auth provider state."""
    state: AuthProviderState = request.state.auth_provider
    return state.token_validator


async def get_access_token(
    token: Annotated[
        str,
        Depends(get_raw_access_token),
    ],
    validator: Annotated[
        TokenValidator,
        Depends(get_token_validator),
    ],
) -> AccessToken:
    """Validate the current access token and return its normalized model."""
    try:
        return await validator.validate(token)
    except TokenValidationError as exc:
        raise UnauthorizedError("Invalid authentication token.") from exc
