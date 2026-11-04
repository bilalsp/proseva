
from typing import Annotated

from fastapi import Depends
from fastapi.security import SecurityScopes

from mscore.auth.authentication.dependencies import get_principal
from mscore.auth.exceptions import ForbiddenError
from mscore.auth.models import Principal


def require_scopes(
    security_scopes: SecurityScopes,
    principal: Annotated[
        Principal,
        Depends(get_principal),
    ],
) -> Principal:
    """Require every OAuth scope declared for the endpoint."""
    required = frozenset(security_scopes.scopes)
    missing = required - principal.scopes

    if missing:
        raise ForbiddenError(
            "Insufficient permissions to access this endpoint.",
            error_log={
                "event": "authorization_failed",
                "reason": "insufficient_scopes",
                "required_scopes": sorted(required),
                "missing_scopes": sorted(missing),
            },
        )

    return principal
