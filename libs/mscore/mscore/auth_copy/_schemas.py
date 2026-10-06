from typing import Annotated, Any

from keycloak import KeycloakOpenID
from pydantic import BaseModel, Field


class KeycloakState(BaseModel, arbitrary_types_allowed=True, frozen=True):
    openid_client: Annotated[
        KeycloakOpenID, Field(description="Keycloak OpenID client.")
    ]
    public_key: Annotated[str, Field(description="Public decoding key")]


class CurrentUser(BaseModel, frozen=True):
    # TODO: write fields description...
    sub: Annotated[str, Field(description="")]
    preferred_username: Annotated[str | None, Field(description="")] = None
    realm_access: Annotated[dict[str, Any], Field(description="")]
