from pydantic import BaseModel

from mscore.auth.providers.protocols import TokenValidator


class AuthProviderState(BaseModel, arbitrary_types_allowed=True, frozen=True):
    token_validator: TokenValidator
