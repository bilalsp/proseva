from fastapi import FastAPI
from starlette.types import Lifespan

from mscore.settings import BaseAppSettings
from mscore.types import AppType
from mscore.utils import get_project_version

__all__ = [
    "create_app",
]


def create_app(
    settings: BaseAppSettings, /, lifespan: Lifespan[AppType] | None = None
) -> AppType:
    """Create a FastAPI application.

    Args:
        settings: it is used to configure the application.

    Returns:
        An instance of FastAPI application.
    """
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

    app = FastAPI(
        # title=
        # description=
        # summary=
        version=get_project_version("pyproject.toml"),
        # lifespan=lifespan_manager,
        swagger_ui_init_oauth={
            # "clientId": f"{settings.keycloak.client_id}-swagger-ui",
            "usePkceWithAuthorizationCodeGrant": True,
        },
        lifespan=lifespan,
    )
    return app
