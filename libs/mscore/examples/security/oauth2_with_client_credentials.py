"""
[REFERENCE]
- fastapi = "0.110.0"
- https://github.com/marcospereirampj/python-keycloak/pull/281
"""
import json
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from jwcrypto.jwt import JWException
from keycloak import KeycloakAuthenticationError
from pydantic import BaseModel, ValidationError

from mscore import create_app
from mscore.schemas import KeycloakState
from mscore.security import OAuth2ClientCredentials, OAuth2ClientCredentialsRequestForm
from mscore.settings import AppSettings, get_settings


#
# schemas
#
class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    sub: str
    preferred_username: str | None = None
    email: str | None = None
    name: str | None = None
    disabled: bool | None = None


class TokenData(BaseModel):
    sub: str
    preferred_username: str | None = None


#
# dependencies
#
# oauth2_scheme = OAuth2ClientCredentials(
#     tokenUrl="http://localhost:8080/realms/oauth2-client-credentials-demo/protocol/openid-connect/token"
# )
oauth2_scheme = OAuth2ClientCredentials(tokenUrl="/token")


async def get_current_user(
    req: Request, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    keycloak_state: KeycloakState = req.state.keycloak
    try:
        keycloak_state.openid_client.decode_token(
            token,
            keycloak_state.public_key,
            algorithms=["RS256"],
            options={"verify_aud": True},
        )
        # token_data = TokenData(**payload)
        user = User.model_validate(keycloak_state.openid_client.userinfo(token))
    except (JWException, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    return user


#
# routes
#
router = APIRouter()


@router.post("/token")
async def login(
    req: Request, form_data: Annotated[OAuth2ClientCredentialsRequestForm, Depends()]
) -> Token:
    try:
        keycloak_state: KeycloakState = req.state.keycloak
        token = keycloak_state.openid_client.token(
            # username=form_data.client_id,
            # password=form_data.client_secret,
            grant_type=form_data.grant_type,
        )
    except KeycloakAuthenticationError as ex:
        raise HTTPException(
            status_code=ex.response_code,
            detail=json.loads(ex.error_message.decode("utf-8"))["error_description"],
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    return Token(**token)


@router.get("/users/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


#
# app
#
class TestAppSettings(AppSettings, env_file="examples/examples.env"):
    ...


settings: TestAppSettings = get_settings(TestAppSettings)

app = create_app(settings=settings)
app.include_router(router=router)
