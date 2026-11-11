
import OAuth2ScopesPlugin from "./oauth2-scopes.js";

const CONFIG_ELEMENT_ID = "swagger-config";
const SWAGGER_UI_ELEMENT_ID = "#swagger-ui";

const configElement = document.getElementById(CONFIG_ELEMENT_ID);

if (!configElement) {
    throw new Error("Swagger configuration element not found.");
}

if (!window.SwaggerUIBundle) {
    throw new Error("Swagger UI bundle is not loaded.");
}

const config = JSON.parse(configElement.textContent);

const {
    oauth2,
    oauth2RedirectUrl,
    ...swaggerConfig
} = config;

// Resolve the OAuth2 callback against the browser's public origin.
// This avoids depending on Uvicorn proxy headers.
const resolvedRedirectUrl = oauth2RedirectUrl
    ? new URL(oauth2RedirectUrl, window.location.origin).toString()
    : undefined;

const ui = window.SwaggerUIBundle({
    ...swaggerConfig,

    ...(resolvedRedirectUrl && {
        oauth2RedirectUrl: resolvedRedirectUrl,
    }),

    dom_id: SWAGGER_UI_ELEMENT_ID,

    presets: [
        window.SwaggerUIBundle.presets.apis,
    ],

    plugins: [
        OAuth2ScopesPlugin,
    ],

    layout: "BaseLayout",
});

if (oauth2) {
    ui.initOAuth(oauth2);
}

window.ui = ui;
