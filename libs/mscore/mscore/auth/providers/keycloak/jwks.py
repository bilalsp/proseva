import asyncio
import time
from typing import Any

import jwt

from keycloak import KeycloakOpenID


class KeycloakJwksProvider:
    def __init__(self, client: KeycloakOpenID, *, ttl: float = 300.0) -> None:
        """It provides cached Keycloak JWKS (JSON Web Key Set) public keys.

        Fetches public keys from Keycloak when the cache expires and uses an async lock to prevent concurrent JWKS refreshes.

        Args:
            client: Keycloak OpenID client used to fetch JWKS.
            ttl: Cache lifetime in seconds. Defaults to 300 seconds.
        """
        self._client = client
        self._ttl = ttl
        self._keys: dict[str, Any] = {}
        self._expires_at = 0.0
        self._lock = asyncio.Lock()

    async def get_public_key(self, kid: str) -> Any:
        """It returns the public key associated with a Keycloak key ID.

        Args:
            kid: Key ID (`kid`) from the JWT header.

        Returns:
            The public key used to verify the JWT signature.
        """
        key = self._get_cached_key(kid)

        if key is not None:
            return key

        async with self._lock:
            # another request may have refreshed while we waited.
            key = self._get_cached_key(kid)

            if key is not None:
                return key

            await self._refresh()
            key = self._get_cached_key(kid)

            if key is None:
                raise KeyError(f"Unknown Keycloak key id: {kid!r}")

            return key

    async def _refresh(self) -> None:
        response = await self._client.a_certs()
        keys = response.get("keys")

        if not isinstance(keys, list):
            raise RuntimeError("Invalid JWKS response from Keycloak")

        self._keys = {
            jwk["kid"]: jwt.PyJWK.from_dict(jwk).key
            for jwk in keys
            if isinstance(jwk, dict)
            and isinstance(jwk.get("kid"), str)
            and jwk.get("use") == "sig"
        }

        self._expires_at = time.monotonic() + self._ttl

    def _get_cached_key(self, kid: str) -> Any | None:
        if time.monotonic() >= self._expires_at:
            return None
        return self._keys.get(kid)
