from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    OK = "ok"
    ERROR = "error"


class HealthCheckResult(BaseModel):
    name: Annotated[str, Field(description="Health check name", examples=["db_check"])]
    status: Annotated[HealthStatus, Field(description="Health check status")]
    detail: Annotated[
        str,
        Field(
            description="Optional details shown only when the health check status is 'error'"
        ),
    ] = ""


class ReadinessProbeDTO(BaseModel):
    status: Annotated[HealthStatus, Field(description="Health check status")]
    checks: list[HealthCheckResult]


class LivenessProbeDTO(BaseModel):
    status: Annotated[
        Literal[HealthStatus.OK], Field(description="Health check status")
    ]
