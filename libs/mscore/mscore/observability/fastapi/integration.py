
import asyncio

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider

from mscore.observability.backends.elastic.backend import ElasticBackend
from mscore.observability.exceptions import ObservabilityInitializationError
from mscore.observability.settings import ObservabilitySettings


def instrument_fastapi(
    app: FastAPI,
    settings: ObservabilitySettings,
    *,
    service_name: str,
    service_version: str | None = None,
    environment: str = "development",
) -> None:
    """Configure OpenTelemetry and instrument a FastAPI application."""

    if not settings.enabled:
        return

    if getattr(app.state, "_mscore_observability_enabled", False):
        raise ObservabilityInitializationError(
            "FastAPI application is already instrumented by mscore.observability."
        )

    if settings.backend is None:
        raise ObservabilityInitializationError(
            "Observability backend is not configured."
        )

    backend = ElasticBackend(settings.backend)

    try:
        tracer_provider = backend.configure(
            service_name=service_name,
            service_version=service_version,
            environment=environment,
            sample_rate=settings.sample_rate,
        )

        current_provider = trace.get_tracer_provider()

        if isinstance(current_provider, TracerProvider):
            raise ObservabilityInitializationError(
                "An OpenTelemetry TracerProvider is already configured "
                "for this process."
            )

        trace.set_tracer_provider(tracer_provider)

        excluded_urls = ",".join(settings.excluded_urls) or None

        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=tracer_provider,
            excluded_urls=excluded_urls,
        )

        app.state._mscore_observability_enabled = True
        app.state._mscore_observability_backend = backend

        async def shutdown_observability() -> None:
            await asyncio.to_thread(backend.shutdown)

        app.add_event_handler(
            "shutdown",
            shutdown_observability,
        )

    except Exception as exc:
        backend.shutdown()

        if isinstance(exc, ObservabilityInitializationError):
            raise

        raise ObservabilityInitializationError(
            "Failed to initialize FastAPI observability."
        ) from exc
