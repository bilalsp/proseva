from typing import Callable

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.middleware import Middleware
from starlette.types import Lifespan

from mscore.errors import ErrorResponsesBuilder
from mscore.logging import setup_logging
from mscore.middlewares import ErrorHandlingMiddleware, RequestIdMiddleware
from mscore.monitoring.health import get_health_router
from mscore.settings import BaseAppSettings
from mscore.types import AppType
from mscore.utils import get_project_version


def create_app(
    settings: BaseAppSettings,
    /,
    lifespan: Lifespan[AppType] | None = None,
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

    # from fastapi.openapi.models import Server

    # create an ASGI application
    app = FastAPI(
        # servers=[ {"url": "/api/v1", "description": "Main API (v1)"}],
        # title=
        # description=
        # summary=
        version=get_project_version("pyproject.toml"),
        lifespan=lifespan,
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


# from mscore.errors._middlewares import LifespanLoggerMiddleware

# app.add_middleware(LifespanLoggerMiddleware)

# from mscore.errors._middlewares import ErrorHandlingMiddleware2

# app.add_middleware(ErrorHandlingMiddleware2)
# from mscore.lifespan import KeycloakOpenIDLifespan, LifespanManager
# lifespan_manager = LifespanManager(
#     [
#         KeycloakOpenIDLifespan(
#             **settings.keycloak.model_dump(
#                 exclude={"authorization_url", "token_url"}, mode="json"
#             )
#         ),
#     ]
# )
