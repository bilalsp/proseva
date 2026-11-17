
from typing import Protocol

from opentelemetry.sdk.trace import TracerProvider


class ObservabilityBackend(Protocol):
    def configure(
        self,
        *,
        service_name: str,
        service_version: str | None,
        environment: str,
        sample_rate: float,
    ) -> TracerProvider:
        """Configure OpenTelemetry and return its TracerProvider."""

    def shutdown(self) -> None:
        """Flush and shut down backend telemetry resources."""
