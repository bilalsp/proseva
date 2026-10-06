from typing import Protocol, runtime_checkable

from mscore.auth.models import AccessToken


@runtime_checkable
class TokenValidator(Protocol):
    async def validate(self, token: str | None) -> AccessToken:
        """Validate an access token and return its normalized representation."""
