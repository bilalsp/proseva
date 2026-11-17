from typing import Annotated, Literal

from pydantic import AnyHttpUrl, BaseModel, Field, SecretStr


class ElasticBackendSettings(BaseModel):
    provider: Literal["elastic"] = "elastic"
    endpoint: Annotated[
        AnyHttpUrl,
        Field(description="Elastic Cloud Managed OTLP endpoint."),
    ]
    api_key: Annotated[
        SecretStr,
        Field(description="Elastic Cloud API key for OTLP ingestion."),
    ]
