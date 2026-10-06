from datetime import datetime
from typing import Any, Mapping

from pydantic import BaseModel, Field


class AccessToken(BaseModel, frozen=True):
    sub: str = Field(
        ...,
        description="A unique identifier for the subject (typically the user) to whom the token was issued.",
    )
    iss: str = Field(
        ...,
        description="The issuer of the token, identifying the authority or service that issued it.",
        examples=["https://auth.example.com"],
    )
    aud: tuple[str, ...] = Field(
        ...,
        description="The intended audience of the token, identifying the service or services for which the token is intended.",
        examples=[("api-listing", "account")],
    )
    expires_at: datetime = Field(
        ...,
        description="The date and time at which the token expires and must no longer be accepted.",
    )
    issued_at: datetime | None = Field(
        default=None,
        description="The date and time at which the token was issued.",
    )
    not_before: datetime | None = Field(
        default=None,
        description="The date and time before which the token must not be accepted.",
    )
    claims: Mapping[str, Any] = Field(
        ...,
        description="Additional claims contained in the token that are not represented by the standard fields above.",
    )
