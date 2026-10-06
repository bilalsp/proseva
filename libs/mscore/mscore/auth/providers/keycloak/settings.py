from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    computed_field,
)


class KeycloakSettings(BaseModel):
    provider: Literal["keycloak"] = "keycloak"

    server_url: Annotated[HttpUrl, Field(description="Keycloak server url.")]
    realm_name: Annotated[
        str,
        Field(
            description="""Realm where you manage objects, including users, clients,
            roles, and groups. Note: only applications in a same realm can use SSO."""
        ),
    ]
    client_id: Annotated[
        str,
        Field(
            description="""Keycloak client which will be used for authentication and
            authorization in order to secure the microservice. NOTE: Two microservices
            should not use the same client."""
        ),
    ]
    client_secret_key: Annotated[
        str | None,
        Field(
            None,
            description="""The secret which allows the client to prove its identity to the
            Keycloak server. NOTE: It should be known only to the application and the
            authorization server. A public Keycloak client doesn't need it.""",
        ),
    ]

    @computed_field
    @property
    def issuer(self) -> str:
        """The issuer URL identifying the Keycloak realm that issued the token."""
        return f"{str(self.server_url).rstrip('/')}/realms/{self.realm_name}"

    @computed_field
    @property
    def authorization_url(self) -> str:
        """Client application redirects users to this url in order to authenticate them."""
        return f"{str(self.server_url).rstrip('/')}/realms/{self.realm_name}/protocol/openid-connect/auth"

    @computed_field
    @property
    def token_url(self) -> str:
        """It is used to fetch a token from the keycloak."""
        return f"{str(self.server_url).rstrip('/')}/realms/{self.realm_name}/protocol/openid-connect/token"
