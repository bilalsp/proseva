
import OAuth2ScopesPlugin from "./oauth2-scopes.js";

const configElement = document.getElementById(
    "mscore-swagger-config"
);

if (!configElement) {
    throw new Error("Swagger config element not found");
}

if (!window.SwaggerUIBundle) {
    throw new Error("SwaggerUIBundle is not loaded");
}

const config = JSON.parse(configElement.textContent);

const { oauth2, ...swaggerConfig } = config;

const ui = window.SwaggerUIBundle({
    ...swaggerConfig,

    dom_id: "#swagger-ui",

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
