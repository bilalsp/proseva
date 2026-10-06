# `mscore.auth` Architecture

## 1. Purpose

The `mscore.auth` package provides the authentication and authorization foundation for MSCORE applications.

The package separates:

* **Authentication** — extracting and validating access tokens.
* **Authorization** — the future boundary for access-control functionality.
* **Providers** — integration with external identity providers such as Keycloak.

The public authentication API is provider-agnostic. Provider-specific implementation details remain inside the corresponding provider package.

---

## 2. Package Structure

```text
mscore/
└── auth/
    ├── __init__.py
    ├── exceptions.py
    ├── models.py
    │
    ├── authentication/
    │   ├── dependencies.py
    │   └── schemes.py
    │
    ├── authorization/
    │
    └── providers/
        ├── factory.py
        ├── protocols.py
        ├── state.py
        │
        ├── auth0/
        │   └── settings.py
        │
        └── keycloak/
            ├── jwks.py
            ├── lifespan.py
            ├── settings.py
            └── validator.py
```

---

## 3. Architecture

The package is built around a provider-independent `TokenValidator` protocol.

```text
                    FastAPI request
                          │
                          ▼
                Authentication layer
                          │
                          ▼
                  TokenValidator
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
      Keycloak provider          Future providers
             │
             ▼
        AccessToken
```

Application code interacts with the authentication layer through:

* `get_raw_access_token()`
* `get_access_token()`
* `AccessToken`

It does not need to depend directly on Keycloak-specific classes.

---

## 4. Authentication

The authentication layer uses FastAPI's OAuth2 authorization-code bearer scheme to extract access tokens from requests.

The configured provider supplies the token validator through application lifespan state:

```text
Request
  │
  ▼
OAuth2 bearer token
  │
  ▼
Provider TokenValidator
  │
  ▼
AccessToken
```

Validation failures are translated into an `UnauthorizedError` at the authentication boundary.

---

## 5. Provider Integration

Provider-specific functionality is isolated under `providers/`.

The `TokenValidator` protocol defines the contract that providers must implement:

```python
class TokenValidator(Protocol):
    async def validate(self, token: str | None) -> AccessToken:
        ...
```

`AuthProviderState` stores the configured validator and makes it available to request dependencies.

The provider factory selects the appropriate provider lifespan from application configuration.

---

## 6. Keycloak

Keycloak is currently the supported authentication provider.

Its implementation consists of:

* `settings.py` — Keycloak connection and realm configuration.
* `lifespan.py` — initializes the Keycloak authentication components.
* `jwks.py` — retrieves and caches Keycloak signing keys.
* `validator.py` — validates JWT access tokens and produces `AccessToken`.

The Keycloak implementation currently validates RS256-signed JWTs against the configured issuer and audience.

---

## 7. Auth0

Auth0 configuration is present as a placeholder, but Auth0 is **not currently supported**.

Attempting to use the Auth0 settings raises an explicit configuration error.

---

## 8. Authorization

The `authorization/` package currently contains no authorization logic.

It is reserved for future functionality such as permissions, roles, scopes, or access policies.

---

## 9. Design Principles

The main architectural principles are:

1. **Provider independence**
   Authentication dependencies depend on `TokenValidator`, not on a specific identity provider.

2. **Provider isolation**
   Provider-specific clients, configuration, key management, and validation remain under `providers/<provider>/`.

3. **Normalized token model**
   Providers expose validated identities through the common `AccessToken` model.

4. **Application lifecycle integration**
   Provider resources are initialized through the FastAPI lifespan mechanism.

5. **Small public API**
   Application code should primarily use `get_access_token()` and `AccessToken`.
