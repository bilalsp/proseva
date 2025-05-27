from inspect import Parameter, Signature
from typing import Callable

from fastapi import APIRouter, Depends, Response, status

from ._dto import HealthCheckResult, HealthStatus, LivenessProbeDTO, ReadinessProbeDTO


def _get_readiness_probe_endpoint(health_checks: list | None) -> Callable:
    """Dynamically builds a readiness probe endpoint with injected dependencies for each health check."""

    async def readiness_probe_endpoint(
        response: Response, **dependencies
    ) -> ReadinessProbeDTO:
        # extract the results of all injected health checks
        dependencies = list(dependencies.values())

        # determine overall readiness status based on individual check results
        if all(
            health_status.status == HealthStatus.OK for health_status in dependencies
        ):
            status_code = status.HTTP_200_OK
            health_status = HealthStatus.OK
        else:
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            health_status = HealthStatus.ERROR

        response.status_code = status_code

        return ReadinessProbeDTO(status=health_status, checks=dependencies)

    # dynamically construct the endpoint's signature as well docstring
    params = [
        Parameter(
            "response",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Response,
        )
    ]
    doc_lines = [
        "It is used to check if the application is ready to serve traffic.",
        "",
        "`NOTE: ` It checks the readiness of the application by evaluating the following health checks:",
    ]
    for health_check in health_checks or []:
        check_name = health_check.__name__
        doc = (health_check.__doc__ or "").strip()
        short_doc = doc.split("\n")[0]
        doc_lines.append(f"- `{check_name}`: {short_doc}")

        params.append(
            Parameter(
                f"{check_name}",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=HealthCheckResult,
                default=Depends(health_check),
            )
        )

    # set dynamically built signature and docstring
    readiness_probe_endpoint.__signature__ = Signature(
        params, return_annotation=ReadinessProbeDTO
    )
    readiness_probe_endpoint.__doc__ = "\n".join(doc_lines)
    return readiness_probe_endpoint


def get_health_router(health_checks: list | None) -> APIRouter:
    """It returns an APIRouter with liveness and (optionally) readiness endpoints.

    NOTE:
        - Liveness: Always available.
        - Readiness: Only added if health_checks are provided.
    """
    router = APIRouter()

    @router.get("/health/live")
    def _liveness_probe_endpoint() -> LivenessProbeDTO:
        """It is used to checks if the application is alive and not."""
        return LivenessProbeDTO(status=HealthStatus.OK)

    # readiness endpoint: dynamically created if health checks are provided
    if health_checks:
        router.add_api_route(
            path="/health/ready",
            endpoint=_get_readiness_probe_endpoint(health_checks=health_checks),
            methods=["GET"],
            responses={
                status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadinessProbeDTO}
            },
        )

    return router
