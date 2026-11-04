# `mscore.auth` Architecture

## 1. Purpose

`mscore.auth` provides provider-independent authentication and scope-based authorization for MSCORE applications.

Responsibilities:

- **Authentication:** Extract and validate OAuth2 bearer tokens.
- **Identity:** Normalize validated tokens into `AccessToken` and `Principal`.
- **Authorization:** Enforce endpoint-level OAuth2 scope requirements.
- **Providers:** Isolate identity-provider integrations.

Provider-specific implementations must not leak into authentication or authorization dependencies.

## 2. Package Structure

```text
auth/
├── __init__.py
├── exceptions.py
├── models.py
├── authentication/
│   ├── dependencies.py
│   └── schemes.py
├── authorization/
│   └── scope/
│       └── dependencies.py
└── providers/
    ├── factory.py
    ├── protocols.py
    ├── state.py
    ├── auth0/
    │   └── settings.py
    └── keycloak/
        ├── jwks.py
        ├── lifespan.py
        ├── settings.py
        └── validator.py
```

## 3. Core Contracts

### TokenValidator

Defined in `providers/protocols.py`.

```python
@runtime_checkable
class TokenValidator(Protocol):
    async def validate(self, token: str | None) -> AccessToken:
        ...
```

All providers must implement this contract.

### AccessToken

Defined in `models.py`. Immutable normalized representation of a validated token.

Fields: `sub`, `iss`, `aud`, `expires_at`, `issued_at`, `not_before`, `claims`.

### Principal

Defined in `models.py`. Immutable authorization identity.

Fields:
- `sub`: authenticated subject identifier.
- `scopes`: `frozenset[str]` of granted OAuth2 scopes.

Scopes are extracted from the whitespace-separated `scope` token claim.

### AuthProviderState

Defined in `providers/state.py`.

Stores the configured `TokenValidator` and exposes it through FastAPI request state as `request.state.auth_provider`.

## 4. Authentication

Implemented in `authentication/`.

| Dependency | Responsibility |
|---|---|
| `get_raw_access_token` | Extract bearer token. |
| `get_token_validator` | Retrieve validator from request state. |
| `get_access_token` | Validate token and return `AccessToken`. |
| `get_principal` | Build `Principal` from validated token. |

`schemes.py` provides a cached `OAuth2AuthorizationCodeBearer` configured from application settings.

Use `auto_error=False`; authentication errors are handled by the validator.

Authentication flow:

```text
Request
  → OAuth2 bearer extraction
  → TokenValidator.validate()
  → AccessToken
  → Principal
```

Missing or invalid credentials must raise `UnauthorizedError` (HTTP 401).

## 5. Authorization

Implemented in `authorization/scope/dependencies.py`.

`require_scopes()` uses FastAPI `SecurityScopes` and the authenticated `Principal`.

Authorization rule:

```python
required = frozenset(security_scopes.scopes)
missing = required - principal.scopes

if missing:
    raise ForbiddenError(
        "Insufficient permissions to access this endpoint.",
        error_log={
            "event": "authorization_failed",
            "reason": "insufficient_scopes",
            "required_scopes": sorted(required),
            "missing_scopes": sorted(missing),
        },
    )
```

All required scopes must be granted (AND semantics).

Use through FastAPI `Security`:

```python
principal: Annotated[
    Principal,
    Security(require_scopes, scopes=["users:read"]),
]
```

Insufficient permissions must raise `ForbiddenError` (HTTP 403).

Authentication and authorization must remain separate concerns.

## 6. Provider Integration

### Factory

`providers/factory.py` selects the provider lifespan from configuration.

Currently supported: `keycloak`.

Unsupported providers raise `RuntimeError`.

### Keycloak

Keycloak is the only implemented provider.

| Module | Responsibility |
|---|---|
| `settings.py` | Server, realm, client configuration and computed OIDC URLs. |
| `lifespan.py` | Initialize client, JWKS provider, validator and provider state. |
| `jwks.py` | Retrieve and cache signing keys. |
| `validator.py` | Validate JWTs and produce `AccessToken`. |

Validation requirements:

- Accept RS256 only.
- Require a valid JWT `kid`.
- Retrieve signing keys from Keycloak JWKS.
- Verify signature, issuer and audience.
- Require `sub`, `iss`, `aud`, and `exp`.
- Normalize validated claims into `AccessToken`.

JWKS caching uses an asynchronous lock and currently has a fixed 300-second TTL.

Unknown signing keys and invalid tokens must produce `UnauthorizedError`.

### Auth0

`providers/auth0/settings.py` is a placeholder.

Auth0 is unsupported and currently raises `ValueError` during settings validation.

New providers must implement `TokenValidator` and integrate through the provider lifespan mechanism.

## 7. Exceptions

Defined in `exceptions.py`.

| Exception | HTTP status | Meaning |
|---|---:|---|
| `UnauthorizedError` | 401 | Missing or invalid authentication. |
| `ForbiddenError` | 403 | Insufficient authorization. |

Both extend `HTTPCustomError` and support structured diagnostic logging.

## 8. Public API

Exported through `mscore.auth`:

- `get_raw_access_token`
- `get_access_token`
- `get_principal`
- `require_scopes`
- `AccessToken`
- `Principal`


## 9. Implementation Constraints

AI coding agents must preserve the following architectural rules:

1. Keep authentication and authorization provider-independent.
2. Implement new providers through `TokenValidator`.
3. Keep provider-specific logic inside `providers/<provider>/`.
4. Use `AccessToken` as the normalized validated-token representation.
5. Use `Principal` as the authorization identity.
6. Enforce scopes through `SecurityScopes` and `require_scopes`.
7. Require all declared scopes; do not introduce implicit OR semantics.
8. Preserve the distinction between HTTP 401 and HTTP 403.
9. Initialize provider resources through FastAPI lifespan.
10. Keep security models immutable.
11. Do not bypass JWT signature, issuer, audience, or expiration validation.
12. Keep the public API minimal and explicitly exported.
