
class ObservabilityError(Exception):
    """Base exception for observability-related errors."""


class ObservabilityBackendError(ObservabilityError):
    """Raised when a backend cannot be configured."""


class ObservabilityInitializationError(ObservabilityError):
    """Raised when observability cannot be initialized."""

# class ObservabilityConfigurationError(ObservabilityError):
#     """Raised when observability configuration is invalid."""
