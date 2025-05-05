import traceback

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from mscore.errors._error_responses import (
    ErrorModelBuilder,
    convert_status_code_to_text,
)
from mscore.errors._exceptions import HTTPCustomError
from mscore.logging import get_logger
from mscore.settings import MicroServiceSettings

ErrorMediaType = "application/problem+json"


class ErrorHandlingMiddleware:
    def __init__(self, app: ASGIApp, settings: MicroServiceSettings) -> None:
        self.app = app
        self.error_model_builder = ErrorModelBuilder(settings=settings)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            request = Request(scope)
            await self.app(scope, receive, send)
        except HTTPCustomError as ex:
            ErrorModel = self.error_model_builder.build(status_code=ex.status_code)
            response = JSONResponse(
                content=ErrorModel(
                    title=ex.title,
                    status=ex.status_code,
                    detail=ex.detail,
                    instance=request.url.path,
                    voilations=ex.voialations,
                    type=ex.__class__.__name__,
                    error_log=ex.error_log,
                    error_stacktrace=traceback.format_exc(),
                ).model_dump(),
                status_code=ex.status_code,
                headers=ex.headers,
                media_type=ErrorMediaType,
            )
            await response(scope, receive, send)

        # except ExpiredSignature as ex

        except HTTPException as ex:
            ErrorModel = self.error_model_builder.build(status_code=ex.status_code)
            response = JSONResponse(
                content=ErrorModel(
                    title=convert_status_code_to_text(ex.status_code),
                    status=ex.status_code,
                    detail=ex.detail,
                    instance=request.url.path,
                    voilations={},
                    type=ex.__class__.__name__,
                    error_log={},
                    error_stacktrace=traceback.format_exc(),
                ).model_dump(),
                status_code=ex.status_code,
                headers=ex.headers,
                media_type=ErrorMediaType,
            )

        # except RequestValidationError as ex:

        except BaseException as ex:
            logger = get_logger()

            logger.exception(ex)

            response = JSONResponse(
                content="BaseException",
                status_code=500,
            )
            await response(scope, receive, send)
