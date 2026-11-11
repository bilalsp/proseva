
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles


_STATIC_DIR = Path(__file__).resolve().parent / "static" / "swagger"

_SWAGGER_UI_VERSION = "5.17.14"


def _safe_json(value: Any) -> str:
    return (
        json.dumps(value)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def install_swagger_ui(
    app: FastAPI,
    *,
    docs_url: str = "/docs",
    oauth2_redirect_url: str = "/docs/oauth2-redirect",
    swagger_ui_parameters: dict[str, Any] | None = None,
    init_oauth: dict[str, Any] | None = None,
) -> None:
    """Install custom Swagger UI with OAuth2 scopes support."""

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
            raise RuntimeError(
                f"Missing Swagger asset: {filepath}"
            )

    # Register static files.
    mount_name = "mscore-swagger-assets"

    if not any(
        getattr(route, "name", None) == mount_name
        for route in app.routes
    ):
        app.mount(
            "/_mscore/swagger",
            StaticFiles(directory=str(_STATIC_DIR)),
            name=mount_name,
        )

    parameters = dict(swagger_ui_parameters or {})

    # Custom Swagger documentation endpoint.
    @app.get(
        docs_url,
        include_in_schema=False,
        name="mscore-swagger-docs",
    )
    async def swagger_docs(request: Request) -> HTMLResponse:

        openapi_url = str(request.url_for("openapi"))

        initializer_url = str(
            request.url_for(
                mount_name,
                path="swagger-initializer.js",
            )
        )

        css_url = str(
            request.url_for(
                mount_name,
                path="oauth2-scopes.css",
            )
        )

        redirect_url = str(
            request.url_for("mscore-swagger-oauth2-redirect")
        )


        print("Request URL:", request.url)
        print("Request base URL:", request.base_url)
        print("Request scheme:", request.scope.get("scheme"))
        print(
            "X-Forwarded-Proto:",
            request.headers.get("x-forwarded-proto"),
        )

        print("CSS URL:", css_url)
        print("Initializer URL:", initializer_url)



        config = {
            "url": openapi_url,
            "oauth2RedirectUrl": redirect_url,
            **parameters,
        }

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
        href="{html.escape(css_url, quote=True)}"
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
        src="{html.escape(initializer_url, quote=True)}">
    </script>
</body>
</html>
"""

        return HTMLResponse(html_content)

    # OAuth2 redirect endpoint.
    @app.get(
        oauth2_redirect_url,
        include_in_schema=False,
        name="mscore-swagger-oauth2-redirect",
    )
    async def swagger_oauth2_redirect() -> HTMLResponse:
        return get_swagger_ui_oauth2_redirect_html()
