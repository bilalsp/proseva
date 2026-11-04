from typing import Mapping, Any

from fastapi import status

from mscore.errors._exceptions import HTTPCustomError


class UnauthorizedError(HTTPCustomError):
    def __init__(
        self,
        detail: str,
        /,
        title: str = "Authentication Required",
        voilations: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        error_log: Mapping[str, Any] | None = None,
    ) -> None:
        """Raise this error if user has not authenticated."""
        super().__init__(
            status.HTTP_401_UNAUTHORIZED, title, detail, voilations, headers, error_log
        )


class ForbiddenError(HTTPCustomError):
    def __init__(
        self,
        detail: str,
        title: str = "Access Forbidden",
        voilations: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        error_log: Mapping[str, Any] | None = None,
    ) -> None:
        """Raised this error when an authenticated principal lacks permission."""
        super().__init__(
            status.HTTP_403_FORBIDDEN, title, detail, voilations, headers, error_log
        )
