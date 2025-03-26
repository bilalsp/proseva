"""
[REFERENCE]
- fastapi = "0.110.0"
- https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/
"""
import json
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Security,
    status,
)
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jwcrypto.jwt import JWException
from keycloak import KeycloakAuthenticationError
from pydantic import BaseModel, BeforeValidator, Field, ValidationError

from mscore import create_app
from mscore.schemas import KeycloakState
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


class TokenPayload(BaseModel):
    sub: str
    scopes: Annotated[list[str], BeforeValidator(lambda v: v.split())] = Field(
        [], alias="scope"
    )


#
# dependencies
#
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)


async def get_current_user(
    req: Request,
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    keycloak_state: KeycloakState = req.state.keycloak

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    try:
        payload = TokenPayload.model_validate(
            keycloak_state.openid_client.decode_token(
                token,
                keycloak_state.public_key,
                algorithms=["RS256"],
                options={"verify_aud": True},
            )
        )
        user = User.model_validate(keycloak_state.openid_client.userinfo(token))
    except (JWException, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": authenticate_value},
        ) from None
    for scope in security_scopes.scopes:
        if scope not in payload.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user, scopes=["me"])],
) -> User:
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


#
# routes
#
router = APIRouter()


@router.post("/token")
async def login(
    req: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    try:
        keycloak_state: KeycloakState = req.state.keycloak
        token = keycloak_state.openid_client.token(
            username=form_data.username,
            password=form_data.password,
            scope=" ".join(["openid"] + form_data.scopes),
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
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
) -> list[dict[str, str]]:
    return [{"item_id": "Foo", "owner": current_user.sub}]


@router.get("/status/", dependencies=[Depends(get_current_user)])
async def read_system_status() -> dict[str, str]:
    return {"status": "ok"}


#
# app
#
class TestAppSettings(AppSettings, env_file="examples/examples.env"):
    ...


settings: TestAppSettings = get_settings(TestAppSettings)

app = create_app(settings=settings)
app.include_router(router=router)
