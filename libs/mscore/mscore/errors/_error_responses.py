import http
from typing import Any, Literal, Mapping

from fastapi import status
from pydantic import BaseModel, Field, create_model

from ..settings import Environment, MicroServiceSettings

# fields name of dynamic error-model
TYPE = "type"
TITLE = "title"
STATUS = "status"
DETAIL = "detail"
INSTANCE = "instance"
VOILATIONS = "voilations"
ERROR_LOG = "error_log"
ERROR_STACKTRACE = "error_stacktrace"


def convert_status_code_to_text(status_code: int, /) -> str:
    return http.HTTPStatus(status_code).phrase


class ErrorModelBuilder:
    def __init__(self, settings: MicroServiceSettings):
        self.microservice_environment = settings.environment

    def build(
        self, status_code: int, error_response_example: dict[str, Any] | None = None
    ) -> type[BaseModel]:
        example = self._get_error_model_example(status_code, error_response_example)

        # fields for dyanmic error-model
        fields = {
            TITLE: (
                str,
                Field(
                    example[TITLE],
                    description="Short error title explaining the issue",
                    examples=[example[TITLE]],
                ),
            ),
            STATUS: (
                Literal[example[STATUS]],
                Field(
                    example[STATUS],
                    description="HTTP status code",
                    examples=[example[STATUS]],
                ),
            ),
            DETAIL: (
                str,
                Field(
                    ...,
                    description="A descriptive error message",
                    examples=[example[DETAIL]],
                ),
            ),
            INSTANCE: (
                str,
                Field(
                    ...,
                    description="The URL that caused the error, helping with tracing",
                    examples=[example[INSTANCE]],
                ),
            ),
            VOILATIONS: (
                Mapping[str, Any],
                Field(
                    {},
                    description="Dictionary context for the input voilations.",
                    examples=[example[VOILATIONS]],
                ),
            ),
        }

        if self.microservice_environment != Environment.PRODUCTION:
            # for debugging and server logs
            fields.update(
                {
                    TYPE: (
                        str,
                        Field(
                            example[TYPE],
                            description="Error type (hidden in production).",
                            examples=[example[TYPE]],
                        ),
                    ),
                    ERROR_LOG: (
                        Mapping[str, Any],
                        Field(
                            {},
                            description="Dictionary context for server logs (hidden in production). "
                            "Mainly to log third-party API calls",
                            examples=[example[ERROR_LOG]],
                        ),
                    ),
                    ERROR_STACKTRACE: (
                        str | None,
                        Field(
                            None,
                            description="Stacktrace of the error (hidden in production)",
                            examples=[example[ERROR_STACKTRACE]],
                        ),
                    ),
                }
            )

        return create_model(f"ErrorResponseModel_{status_code}", **fields)

    @staticmethod
    def _get_error_model_example(
        status_code: int, error_response_example: dict[str, Any] | None
    ) -> dict[str, Any]:
        error_response_example = error_response_example or {}
        return {
            TYPE: error_response_example.get(TYPE, "HTTPException"),
            TITLE: error_response_example.get(
                TITLE, convert_status_code_to_text(status_code).title()
            ),
            STATUS: status_code,
            DETAIL: error_response_example.get(
                DETAIL, convert_status_code_to_text(status_code)
            ),
            INSTANCE: error_response_example.get(INSTANCE, "/api/v1/listing"),
            VOILATIONS: error_response_example.get(VOILATIONS, {}),
            ERROR_LOG: error_response_example.get(
                ERROR_LOG,
                {"call": {"method": "GET", "url": "https://third-party/api/item/1"}},
            ),
            ERROR_STACKTRACE: error_response_example.get(
                ERROR_STACKTRACE, "Traceback (most recent call last):\n File..."
            ),
        }


class ErrorResponsesBuilder:
    def __init__(self, settings: MicroServiceSettings) -> None:
        """Build error responses according to RFC-7807

        Reference: https://www.rfc-editor.org/rfc/rfc7807.html
        """
        self.error_model_builder = ErrorModelBuilder(settings)
        self.error_descriptions = {
            status.HTTP_400_BAD_REQUEST: "Bad request error with problem detail",
            status.HTTP_401_UNAUTHORIZED: "Unauthorized access error with problem detial",
            status.HTTP_403_FORBIDDEN: "Forbidden access error with problem detail",
            status.HTTP_404_NOT_FOUND: "Resource not found error with problem detial",
            status.HTTP_412_PRECONDITION_FAILED: "Generic error with problem detail",
            status.HTTP_422_UNPROCESSABLE_ENTITY: "Unprocessable entity with problem detail",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal server error",
        }

    def build(
        self,
        status_codes: list[int],
        error_response_examples: dict[int, dict[str, Any]] | None = None,
    ) -> dict[int, Any]:
        """Build additional responses that could be returned by the *path operation*.

        Args:
            status_codes: error responses will be build for given status-codes.
            error_response_examples: Optionally, error response example with status code as a key.

        NOTE: It will be added to the generated OpenAPI (e.g. visible at `/docs`).
        """
        error_responses = {}
        error_response_examples = error_response_examples or {}

        for status_code in status_codes:
            error_response_example = error_response_examples.get(status_code)
            ErrorModel = self.error_model_builder.build(
                status_code, error_response_example
            )
            error_responses[status_code] = {
                "description": self.error_descriptions.get(status_code, ""),
                # NOTE: FastAPI sets media-type as "application/json" on passing model.
                # "model": ErrorModel,
                "content": {
                    "application/problem+json": {
                        "schema": ErrorModel.model_json_schema(),
                    }
                },
            }
        return error_responses
