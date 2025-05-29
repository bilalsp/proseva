from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.middleware import Middleware
from starlette.types import Lifespan

from .errors import ErrorHandlingMiddleware, ErrorResponsesBuilder
from .lifespan_manager import LifespanManager
from .logging import setup_logging
from .middlewares import RequestIdMiddleware
from .monitoring.health import get_health_router
from .settings import BaseAppSettings
from .utils import get_project_version

if TYPE_CHECKING:
    from .types import AppType


def create_app(
    settings: BaseAppSettings,
    /,
    lifespans: list[Lifespan[AppType]] | None = None,
    health_checks: list[Callable] | None = None,
) -> AppType:
    """Create a FastAPI application.

    Args:
        settings: it is used to configure the application.
        lifespan:
        health_checks:

    Returns:
        An instance of FastAPI application.
    """

    async def _re_raise_exception(_: Request, exc: Exception):
        """Re-raise an exception to handle it inside `ErrorHandlingMiddleware`."""
        raise exc

    if not isinstance(lifespans, list):
        lifespans = []

    # include default lifespan
    # lifespans.append(KeycloakOpenIDLifespan(settings.keycloak))

    # create an ASGI application
    app = FastAPI(
        # servers=[ {"url": "/api/v1", "description": "Main API (v1)"}],
        # title=
        # description=
        # summary=
        version=get_project_version("pyproject.toml"),
        lifespan=LifespanManager(lifespans),
        exception_handlers={
            # handle all exceptions inside `ErrorHandlingMiddleware`
            HTTPException: _re_raise_exception,
            RequestValidationError: _re_raise_exception,
        },
        middleware=[
            Middleware(RequestIdMiddleware),
            Middleware(ErrorHandlingMiddleware, settings.ms),
        ],
        responses=ErrorResponsesBuilder(settings=settings.ms).build(
            status_codes=[
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_412_PRECONDITION_FAILED,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ],
        ),
        swagger_ui_init_oauth={
            # "clientId": f"{settings.keycloak.client_id}-swagger-ui",
            "usePkceWithAuthorizationCodeGrant": True,
        },
    )

    # monitoring router
    health_router = get_health_router(health_checks=health_checks)
    app.include_router(health_router, tags=["Monitoring"])

    setup_logging(settings=settings.ms)

    return app
