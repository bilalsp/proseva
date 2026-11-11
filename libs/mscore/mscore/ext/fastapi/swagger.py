
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


_STATIC_DIR = Path(__file__).resolve().parent / "static" / "swagger"

_SWAGGER_UI_VERSION = "5.17.14"

_ASSETS_MOUNT = "/_mscore/swagger"
_ASSETS_MOUNT_NAME = "mscore-swagger-assets"

_DOCS_ROUTE_NAME = "mscore-swagger-docs"
_REDIRECT_ROUTE_NAME = "mscore-swagger-oauth2-redirect"


def _safe_json(value: Any) -> str:
    """Serialize JSON safely for embedding in HTML."""
    return (
        json.dumps(value)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def _route_path(request: Request, route_name: str, **path_params: Any) -> str:
    """Resolve a named route without retaining its scheme or authority.

    This avoids relying on forwarded headers for public URL generation.
    """
    url = request.url_for(route_name, **path_params)
    parsed = urlsplit(str(url))

    return parsed.path + (f"?{parsed.query}" if parsed.query else "")


def install_swagger_ui(
    app: FastAPI,
    *,
    docs_url: str = "/docs",
    oauth2_redirect_url: str = "/docs/oauth2-redirect",
    swagger_ui_parameters: dict[str, Any] | None = None,
    init_oauth: dict[str, Any] | None = None,
) -> None:
    """Install custom Swagger UI with OAuth2 scopes support.

    All generated Swagger URLs are relative paths. The browser resolves
    them against the public origin, so TLS termination at a reverse proxy
    does not require Uvicorn to trust forwarded headers.
    """

    if app.openapi_url is None:
        raise RuntimeError("FastAPI openapi_url must be enabled.")

    if not _STATIC_DIR.is_dir():
        raise RuntimeError(
            f"Swagger static directory does not exist: {_STATIC_DIR}"
        )

    required_files = (
        "swagger-initializer.js",
        "oauth2-scopes.js",
        "oauth2-scopes.css",
    )

    for filename in required_files:
        filepath = _STATIC_DIR / filename

        if not filepath.is_file():
            raise RuntimeError(f"Missing Swagger asset: {filepath}")

    # Register static assets.
    if not any(
        getattr(route, "name", None) == _ASSETS_MOUNT_NAME
        for route in app.routes
    ):
        app.mount(
            _ASSETS_MOUNT,
            StaticFiles(directory=str(_STATIC_DIR)),
            name=_ASSETS_MOUNT_NAME,
        )

    parameters = dict(swagger_ui_parameters or {})

    # Swagger documentation endpoint.
    @app.get(
        docs_url,
        include_in_schema=False,
        name=_DOCS_ROUTE_NAME,
    )
    async def swagger_docs(request: Request) -> HTMLResponse:

        # Resolve paths without depending on the request scheme.
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
        }

        config["oauth2RedirectUrl"] = redirect_path

        if init_oauth:
            config["oauth2"] = init_oauth

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>{html.escape(app.title)} - Swagger UI</title>

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
        id="mscore-swagger-config"
        type="application/json">{_safe_json(config)}</script>

    <script
        type="module"
        src="{html.escape(initializer_path, quote=True)}">
    </script>
</body>
</html>
"""

        return HTMLResponse(html_content)

    # OAuth2 redirect endpoint.
    @app.get(
        oauth2_redirect_url,
        include_in_schema=False,
        name=_REDIRECT_ROUTE_NAME,
    )
    async def swagger_oauth2_redirect() -> HTMLResponse:
        return get_swagger_ui_oauth2_redirect_html()
