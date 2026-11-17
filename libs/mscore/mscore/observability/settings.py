from typing import Annotated, Self

from pydantic import BaseModel, Field, model_validator

from mscore.observability.backends.elastic.settings import (
    ElasticBackendSettings,
)


class ObservabilitySettings(BaseModel):
    enabled: bool = False
    sample_rate: Annotated[
        float,
        Field(
            ge=0.0,
            le=1.0,
            description="Fraction of traces to sample.",
        ),
    ] = 1.0
    excluded_urls: Annotated[
        list[str],
        Field(
            description="URL patterns excluded from automatic instrumentation."
        ),
    ] = Field(default_factory=list)
    backend: ElasticBackendSettings | None = None

    @model_validator(mode="after")
    def validate_backend(self) -> Self:
        if self.enabled and self.backend is None:
            raise ValueError("A backend must be configured when observability is enabled.")
        return self
