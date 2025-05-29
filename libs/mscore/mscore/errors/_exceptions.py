import json
from typing import Any, Mapping

from fastapi import status

from ._error_responses import convert_status_code_to_text


class HTTPCustomError(Exception):
    def __init__(
        self,
        status_code: int,
        title: str | None = None,
        detail: str | None = None,
        voilations: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        error_log: Mapping[str, Any] | None = None,
    ):
        """

        Args:
            status_code: HTTP status code to send to the client.

        """
        self.status_code = status_code
        self.title = title or convert_status_code_to_text(status_code).title()
        self.detail = detail or convert_status_code_to_text(status_code)
        self.voialations = voilations or {}
        self.headers = headers or {}
        self.error_log = error_log or {}
        super().__init__(self._build_error_message())

    def _build_error_message(self) -> str:
        error_message = {}
        error_message["title"] = self.title
        error_message["voilations"] = json.dumps(
            self.error_log, sort_keys=True, default=str
        )
        error_message["error_log"] = json.dumps(
            self.error_log, sort_keys=True, default=str
        )

        error_message = ", ".join(
            f"{key} = {val}" for key, val in error_message.items()
        )
        error_message = f"{self.detail} ({error_message})"
        return error_message


class BadRequestError(HTTPCustomError):
    def __init__(
        self,
        detail: str,
        title: str = "Bad Request",
        voilations: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        error_log: Mapping[str, Any] | None = None,
    ) -> None:
        """Raise this error if user has not authenticated."""
        super().__init__(
            status.HTTP_400_BAD_REQUEST, title, detail, voilations, headers, error_log
        )


class UnauthorizedError(HTTPCustomError):
    def __init__(
        self,
        detail: str,
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
        """Raise this error if user does not have permission to access the requested resource."""
        super().__init__(
            status.HTTP_403_FORBIDDEN, title, detail, voilations, headers, error_log
        )


class NotFoundError(HTTPCustomError):
    def __init__(
        self,
        detail: str,
        title: str = "Resource Not Found",
        voilations: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        error_log: Mapping[str, Any] | None = None,
    ) -> None:
        """Raise this error if resource not found."""
        super().__init__(
            status.HTTP_404_NOT_FOUND, title, detail, voilations, headers, error_log
        )
