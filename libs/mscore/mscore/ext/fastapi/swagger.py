from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from mscore.settings import BaseAppSettings, get_settings



# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_SETTINGS: BaseAppSettings = get_settings()
_MICROSERVICE_NAME = _SETTINGS.ms.name

_STATIC_DIR = Path(__file__).resolve().parent / "static" / "swagger"

_SWAGGER_UI_VERSION = "5"

_ASSETS_MOUNT = f"/_{_MICROSERVICE_NAME}/swagger"
_ASSETS_MOUNT_NAME = f"{_MICROSERVICE_NAME}-swagger-assets"

_DOCS_ROUTE_NAME = f"{_MICROSERVICE_NAME}-swagger-docs"
_REDIRECT_ROUTE_NAME = f"{_MICROSERVICE_NAME}-swagger-oauth2-redirect"

_REQUIRED_ASSETS = (
    "swagger-initializer.js",
    "oauth2-scopes.js",
    "oauth2-scopes.css",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_json(value: Any) -> str:
    """Serialize JSON safely for embedding inside an HTML document."""
    return (
        json.dumps(value)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def _route_path(
    request: Request,
    route_name: str,
    **path_params: Any,
) -> str:
    """Resolve a named route into a relative URL path."""
    url = request.url_for(route_name, **path_params)
    parsed_url = urlsplit(str(url))

    path = parsed_url.path

    if parsed_url.query:
        path = f"{path}?{parsed_url.query}"

    return path


def _validate_static_assets() -> None:
    """Ensure the Swagger static directory and required files exist."""
    if not _STATIC_DIR.is_dir():
        raise RuntimeError(
            f"Swagger static directory does not exist: {_STATIC_DIR}"
        )

    missing_assets = [
        filename
        for filename in _REQUIRED_ASSETS
        if not (_STATIC_DIR / filename).is_file()
    ]

    if missing_assets:
        raise RuntimeError(
            f"Missing Swagger assets: {', '.join(missing_assets)}"
        )


def _mount_static_assets(app: FastAPI) -> None:
    """Mount Swagger static assets if they are not already mounted."""
    already_mounted = any(
        getattr(route, "name", None) == _ASSETS_MOUNT_NAME
        for route in app.routes
    )

    if already_mounted:
        return

    app.mount(
        _ASSETS_MOUNT,
        StaticFiles(directory=str(_STATIC_DIR)),
        name=_ASSETS_MOUNT_NAME,
    )


def _build_swagger_html(
    app: FastAPI,
    request: Request,
    parameters: dict[str, Any],
    init_oauth: dict[str, Any] | None,
) -> str:
    """Build the Swagger UI HTML document."""
    openapi_path = _route_path(request, "openapi")

    initializer_path = _route_path(
        request,
        _ASSETS_MOUNT_NAME,
        path="swagger-initializer.js",
    )

    css_path = _route_path(
        request,
        _ASSETS_MOUNT_NAME,
        path="oauth2-scopes.css",
    )

    redirect_path = _route_path(
        request,
        _REDIRECT_ROUTE_NAME,
    )

    config = {
        "url": openapi_path,
        **parameters,
        "oauth2RedirectUrl": redirect_path,
    }

    if init_oauth:
        config["oauth2"] = init_oauth

    title = html.escape(app.title, quote=True)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{title} - Swagger UI</title>

    <link
        rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@{_SWAGGER_UI_VERSION}/swagger-ui.css"
    >

    <link
        rel="stylesheet"
        href="{html.escape(css_path, quote=True)}"
    >
</head>

<body>
    <div id="swagger-ui"></div>

    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@{_SWAGGER_UI_VERSION}/swagger-ui-bundle.js"></script>

    <script
        id="swagger-config"
        type="application/json">{_safe_json(config)}</script>

    <script
        type="module"
        src="{html.escape(initializer_path, quote=True)}">
    </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def install_swagger_ui(
    app: FastAPI,
    *,
    docs_url: str = "/docs",
    oauth2_redirect_url: str = "/docs/oauth2-redirect",
    swagger_ui_parameters: dict[str, Any] | None = None,
    init_oauth: dict[str, Any] | None = None,
) -> None:
    """Install a customized Swagger UI with OAuth2 scopes support.

    The Swagger UI configuration uses browser-resolved relative paths
    to support deployments behind HTTPS-terminating reverse proxies.

    Args:
        app: FastAPI application instance.
        docs_url: URL path for Swagger UI.
        oauth2_redirect_url: URL path for OAuth2 redirect handling.
        swagger_ui_parameters: Additional Swagger UI configuration.
        init_oauth: OAuth2 initialization configuration.

    Raises:
        RuntimeError: If OpenAPI is disabled or required static assets
            are missing.
    """
    if app.openapi_url is None:
        raise RuntimeError("FastAPI openapi_url must be enabled.")

    _validate_static_assets()
    _mount_static_assets(app)

    parameters = dict(swagger_ui_parameters or {})

    @app.get(
        docs_url,
        include_in_schema=False,
        name=_DOCS_ROUTE_NAME,
    )
    async def swagger_docs(request: Request) -> HTMLResponse:
        content = _build_swagger_html(
            app=app,
            request=request,
            parameters=parameters,
            init_oauth=init_oauth,
        )

        return HTMLResponse(content=content)

    @app.get(
        oauth2_redirect_url,
        include_in_schema=False,
        name=_REDIRECT_ROUTE_NAME,
    )
    async def swagger_oauth2_redirect() -> HTMLResponse:
        return get_swagger_ui_oauth2_redirect_html()
