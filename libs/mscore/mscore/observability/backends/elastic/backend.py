
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import (
    ParentBased,
    TraceIdRatioBased,
)
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from mscore.observability.backends.elastic.settings import ElasticBackendSettings
from mscore.observability.exceptions import ObservabilityBackendError


class ElasticBackend:
    def __init__(self, settings: ElasticBackendSettings) -> None:
        self._settings = settings
        self._tracer_provider: TracerProvider | None = None

    def configure(
        self,
        *,
        service_name: str,
        service_version: str | None,
        environment: str,
        sample_rate: float,
    ) -> TracerProvider:
        if self._tracer_provider is not None:
            return self._tracer_provider

        try:
            attributes: dict[str, str] = {
                "service.name": service_name,
                "deployment.environment.name": environment,
            }

            if service_version is not None:
                attributes["service.version"] = service_version

            resource = Resource.create(attributes)

            exporter = OTLPSpanExporter(
                endpoint=str(self._settings.endpoint).rstrip("/") + "/v1/traces",
                headers={
                    "Authorization": (
                        f"ApiKey {self._settings.api_key.get_secret_value()}"
                    )
                },
            )

            provider = TracerProvider(
                resource=resource,
                sampler=ParentBased(
                    root=TraceIdRatioBased(sample_rate)
                ),
            )

            provider.add_span_processor(
                BatchSpanProcessor(exporter)
            )

            self._tracer_provider = provider

            return provider

        except Exception as exc:
            raise ObservabilityBackendError(
                "Failed to initialize the Elastic observability backend."
            ) from exc

    def shutdown(self) -> None:
        if self._tracer_provider is None:
            return

        self._tracer_provider.force_flush()
        self._tracer_provider.shutdown()
        self._tracer_provider = None
