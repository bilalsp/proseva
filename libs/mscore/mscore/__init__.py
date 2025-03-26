from fastapi import FastAPI

from mscore.lifespan import KeycloakOpenIDLifespan, LifespanManager
from mscore.settings import AppSettings
from mscore.utils import get_project_version

__all__ = [
    "create_app",
]


def create_app(settings: AppSettings) -> FastAPI:
    """Create a FastAPI application.

    Args:
        settings: it is used to configure the application.

    Returns:
        An instance of FastAPI application.
    """
    lifespan_manager = LifespanManager(
        [
            KeycloakOpenIDLifespan(
                **settings.keycloak.model_dump(
                    exclude={"authorization_url", "token_url"}, mode="json"
                )
            ),
        ]
    )

    app = FastAPI(
        # title=
        # description=
        # summary=
        version=get_project_version("pyproject.toml"),
        lifespan=lifespan_manager,
        swagger_ui_init_oauth={
            "clientId": f"{settings.keycloak.client_id}-swagger-ui",
            "usePkceWithAuthorizationCodeGrant": True,
        },
    )
    return app
