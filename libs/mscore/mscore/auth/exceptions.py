class TokenValidationError(Exception):
    """Raised when an access token cannot be validated."""


class UnauthorizedError(Exception):
    ...


class ForbiddenError(Exception):
    """Raised when an authenticated principal lacks permission."""
