from __future__ import annotations

import jwt

from mscore.auth.exceptions import UnauthorizedError
from mscore.auth.models import AccessToken
from mscore.auth.providers.keycloak.jwks import KeycloakJwksProvider
from mscore.auth.providers.protocols import TokenValidator


class KeycloakTokenValidator(TokenValidator):
    _ALGORITHMS = ("RS256",)
    _UNAUTHORIZED_MESSAGE = "User must be authenticated to access this endpoint."
    _AUTH_HEADERS = {"WWW-Authenticate": "Bearer"}

    def __init__(
        self, jwks: KeycloakJwksProvider, *, issuer: str, audience: str
    ) -> None:
        self._jwks = jwks
        self._issuer = issuer
        self._audience = audience

    async def validate(self, token: str | None) -> AccessToken:
        if token is None:
            raise UnauthorizedError(
                self._UNAUTHORIZED_MESSAGE,
                headers=self._AUTH_HEADERS,
                error_log={
                    "event": "token_validation_failed",
                    "reason": "missing_token",
                },
            )

        # 1. Parse token header
        try:
            header = jwt.get_unverified_header(token)
        except jwt.exceptions.InvalidTokenError as ex:
            raise UnauthorizedError(
                self._UNAUTHORIZED_MESSAGE,
                headers=self._AUTH_HEADERS,
                error_log={
                    "event": "token_validation_failed",
                    "reason": "malformed_token",
                    "exception": type(ex).__name__,
                },
            ) from ex

        # 2. Validate algorithm and kid
        algorithm = header.get("alg")
        kid = header.get("kid")

        if algorithm not in self._ALGORITHMS:
            raise UnauthorizedError(
                self._UNAUTHORIZED_MESSAGE,
                headers=self._AUTH_HEADERS,
                error_log={
                    "event": "token_validation_failed",
                    "reason": "unsupported_algorithm",
                    "algorithm": algorithm,
                    "allowed_algorithms": self._ALGORITHMS,
                },
            )

        if not isinstance(kid, str) or not kid:
            raise UnauthorizedError(
                self._UNAUTHORIZED_MESSAGE,
                headers=self._AUTH_HEADERS,
                error_log={
                    "event": "token_validation_failed",
                    "reason": "missing_or_invalid_kid",
                },
            )

        # 3. Retrieve public signing key
        try:
            public_key = await self._jwks.get_public_key(kid)
        except KeyError as ex:
            raise UnauthorizedError(
                self._UNAUTHORIZED_MESSAGE,
                headers=self._AUTH_HEADERS,
                error_log={
                    "event": "token_validation_failed",
                    "reason": "unknown_signing_key",
                    "kid": kid,
                    "exception": type(ex).__name__,
                },
            ) from ex

        # 4. Verify token
        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=self._ALGORITHMS,
                issuer=self._issuer,
                audience=self._audience,
                options={
                    "require": ("sub", "iss", "aud", "exp"),
                },
            )
        except jwt.exceptions.InvalidTokenError as ex:
            raise UnauthorizedError(
                self._UNAUTHORIZED_MESSAGE,
                headers=self._AUTH_HEADERS,
                error_log={
                    "event": "token_validation_failed",
                    "reason": "invalid_token",
                    "exception": type(ex).__name__,
                    "exception_message": str(ex),
                },
            ) from ex

        return AccessToken(
            sub=payload["sub"],
            iss=payload["iss"],
            aud=payload["aud"],
            expires_at=payload["exp"],
            issued_at=payload.get("iat"),
            not_before=payload.get("nbf"),
            claims=payload,
        )
