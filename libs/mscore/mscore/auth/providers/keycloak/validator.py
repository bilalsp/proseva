from __future__ import annotations

import jwt

from mscore.auth.exceptions import TokenValidationError, UnauthorizedError
from mscore.auth.models import AccessToken
from mscore.auth.providers.keycloak.jwks import KeycloakJwksProvider
from mscore.auth.providers.protocols import TokenValidator


class KeycloakTokenValidator(TokenValidator):
    _ALGORITHMS = ("RS256",)

    def __init__(
        self, jwks: KeycloakJwksProvider, *, issuer: str, audience: str
    ) -> None:
        self._jwks = jwks
        self._issuer = issuer
        self._audience = audience

    async def validate(self, token: str | None) -> AccessToken:
        # TODO: raise proper exception
        if token is None:
            ...

        try:
            header = jwt.get_unverified_header(token)
            if header.get("alg") not in self._ALGORITHMS:
                raise TokenValidationError("Unsupported token algorithm.")

            kid = header.get("kid")
            if not isinstance(kid, str) or not kid:
                raise TokenValidationError("Token is missing a valid key id.")

            public_key = await self._jwks.get_public_key(kid)
            payload = jwt.decode(
                token,
                public_key,
                algorithms=self._ALGORITHMS,
                issuer=self._issuer,
                audience=self._audience,
                options={
                    "verify_exp": True,
                    "verify_aud": False,
                    "require": ("sub", "iss", "aud", "exp"),
                },
            )
        except KeyError as ex:
            raise TokenValidationError("Unknown signing key.") from ex
        except jwt.exceptions.InvalidTokenError as ex:
            raise UnauthorizedError("Invalid token.") from ex

        return AccessToken(
            sub=payload["sub"],
            iss=payload["iss"],
            aud=payload["aud"],
            expires_at=payload["exp"],
            issued_at=payload.get("iat"),
            not_before=payload.get("nbf"),
            claims=payload,
        )
