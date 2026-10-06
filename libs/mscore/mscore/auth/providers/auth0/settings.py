from typing import Literal, Self

from pydantic import BaseModel, model_validator


class Auth0Settings(BaseModel):
    provider: Literal["auth0"] = "auth0"

    @model_validator(mode="after")
    def not_supported(self) -> Self:
        raise ValueError("Auth provider `Auth0` is not supported yet")
