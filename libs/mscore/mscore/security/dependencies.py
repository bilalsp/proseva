from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from jwcrypto.jwt import JWException
from pydantic import ValidationError

from ..schemas import CurrentUser, KeycloakState
from ..settings import AppSettings, get_settings
from ._errors import (
    AuthenticationRequiredError,
    ForbiddenError,
    InvalidTokenError,
)
from .rlac import (
    Authenticated,
    Everyone,
    Principal,
    RolePrincipal,
    RowLevelAccessControl,
    UserPrincipal,
)

__all__ = [
    "get_token",
    "AuthenticationRequired",
    "get_current_user",
    "get_current_user_principals",
    "RowLevelSecurity",
]


#
# security: (AuthN and AuthZ)
#
OAUTH2_SCHEME = None


def _get_oauth2_scheme():
    global OAUTH2_SCHEME
    if OAUTH2_SCHEME is None:
        settings: AppSettings = get_settings()
        OAUTH2_SCHEME = OAuth2AuthorizationCodeBearer(
            authorizationUrl=settings.keycloak.authorization_url,
            tokenUrl=settings.keycloak.token_url,
            auto_error=False,
        )
    return OAUTH2_SCHEME


def get_token(
    token: Annotated[str | None, Depends(_get_oauth2_scheme())],
) -> str | None:
    return token


def get_current_user(
    req: Request, token: Annotated[str | None, Depends(get_token)]
) -> CurrentUser | None:
    if token is None:
        return None

    try:
        keycloak_state: KeycloakState = req.state.keycloak
        payload = keycloak_state.openid_client.decode_token(
            token,
            keycloak_state.public_key,
            algorithms=["RS256"],
            options={"verify_aud": True},
        )
        user = CurrentUser.model_validate(payload)
    except JWException:
        raise InvalidTokenError from None
    except ValidationError as ex:
        raise ForbiddenError("Error: structure of token payload is invalid.") from ex
    # TODO: raise MSCoreUserError if req.state does not have `keycloak`
    # Error: KeycloakOpenIDLifespan has not been setup...

    return user


class AuthenticationRequired:
    def __init__(self, user: Annotated[CurrentUser | None, Depends(get_current_user)]):
        if user is None:
            raise AuthenticationRequiredError


def get_current_user_principals(
    user: Annotated[CurrentUser | None, Depends(get_current_user)],
) -> list[Principal]:
    if user:
        if user.realm_access["roles"] is None:
            # TODO: use logger as well
            raise ForbiddenError(
                f"Error: no realm_access roles defined for user {user.sub}."
            )

        # user is logged in
        principals = [Everyone, Authenticated, UserPrincipal(value=user.sub)]
        principals.extend(
            [RolePrincipal(value=role) for role in user.realm_access["roles"]]
        )
    else:
        # user is not logged in
        principals = [Everyone]
    return principals


RowLevelSecurity = RowLevelAccessControl(get_current_user_principals)


#
# Logging
#
