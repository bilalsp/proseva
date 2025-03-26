#
# Discussion on OAuth2 client credentials flow
# - https://github.com/tiangolo/fastapi/discussions/7846
#
import binascii
from base64 import b64decode
from typing import Annotated, Any, Literal, Optional, cast

from fastapi import Form, Header, Request, status
from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param


#
# Request Form
#
class OAuth2ClientCredentialsRequestForm:
    def __init__(
        self,
        *,
        grant_type: Annotated[
            Literal["client_credentials"],
            Form(description="Oauth2 grant type."),
        ],
        scope: Annotated[
            str,
            Form(
                description="Oauth2 scope. A single string with several scopes separated by spaces."
            ),
        ] = "",
        client_id: Annotated[str | None, Form(description="Oauth2 client id.")] = None,
        client_secret: Annotated[
            str | None, Form(description="Oauth2 client sceret.")
        ] = None,
        authorization: Annotated[
            str | None,
            Header(
                description="The client ID and secret in the HTTP Basic auth header."
            ),
        ] = None,
        # refresh_token
    ):
        """Request form for OAuth2 client_credentials flow

        NOTE: There are two possibilities to receive client_id and client_secret:
            Example-1: [client_id and client_secret in the HTTP Basic auth header]
            POST /token HTTP/1.1
            Host: authorization-server.com
            Authorization: Basic czZCaGRSa3F0MzpnWDFmQmF0M2JW
            Content-Type: application/x-www-form-urlencoded

            grant_type=client_credentials


            Example-2:  [client_id and client_secret as form params]
            POST /token HTTP/1.1
            Host: authorization-server.com
            Content-Type: application/x-www-form-urlencoded

            grant_type=client_credentials
            &client_id=xxxxxxxxxx
            &client_secret=xxxxxxxxxx

        References:
            - https://datatracker.ietf.org/doc/html/rfc6749#section-4.4
            - https://swagger.io/docs/specification/authentication/oauth2
            - https://oauth.net/2/grant-types/client-credentials
        """
        invalid_credentials_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

        scheme, param = get_authorization_scheme_param(authorization)
        if scheme.lower() == "basic":
            try:
                data = b64decode(param).decode("ascii")
                client_id, separator, client_secret = data.partition(":")
            except (ValueError, UnicodeDecodeError, binascii.Error) as ex:
                raise invalid_credentials_exc from ex
            else:
                if not separator:
                    raise invalid_credentials_exc

        if not client_id or not client_secret:
            raise invalid_credentials_exc

        self.grant_type = grant_type
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


#
# Security Schemes
#
class OAuth2ClientCredentials(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        refreshUrl: str | None = None,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        """OAuth2 client_credentials security scheme

        This flow is especially used for Machine-to-Machine (M2M) applications, such as CLIs, daemons, or backend services,
        because the system must authenticate and authorize the application instead of a user.

        References:
            - https://auth0.com/docs/get-started/authentication-and-authorization-flow/client-credentials-flow
        """
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            clientCredentials=cast(
                Any, {"tokenUrl": tokenUrl, "refreshUrl": refreshUrl, "scopes": scopes}
            )
        )
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param
