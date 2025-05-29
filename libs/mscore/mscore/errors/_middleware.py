import os
import traceback

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from starlette.types import ASGIApp, Receive, Scope, Send

from mscore.errors._error_responses import (
    ErrorModelBuilder,
    convert_status_code_to_text,
)
from mscore.errors._exceptions import HTTPCustomError
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
            req = Request(scope)
            logger.info(f"PID {os.getpid()} handles {req.method} {req.url.path}")
            await self.app(scope, receive, send)
        except HTTPCustomError as ex:
            response = self.handle_http_custom_error(instance=req.url.path, error=ex)
            await response(scope, receive, send)
        except HTTPException as ex:
            response = self.handle_fastapi_http_error(instance=req.url.path, error=ex)
            await response(scope, receive, send)
        # except ExpiredSignature as ex:
        #     response = self.handle_expired_signature(instance=req.url.path, error=ex)
        #     await response(scope, receive, send)
        except RequestValidationError as ex:
            response = self.handle_request_validation_error(
                instance=req.url.path, error=ex
            )
            await response(scope, receive, send)
        except ValidationError as ex:
            response = self.handle_pydantic_validation_error(
                instance=req.url.path, error=ex
            )
            await response(scope, receive, send)
        except BaseException as ex:
            response = self.handle_base_error(instance=req.url.path, error=ex)
            await response(scope, receive, send)

    def handle_http_custom_error(
        self, instance: str, error: HTTPCustomError
    ) -> JSONResponse:
        if error.status_code == 500:
            logger.exception(error)
        else:
            logger.warning(error)

        ErrorModel = self.error_model_builder.build(status_code=error.status_code)
        error_model = ErrorModel(
            title=error.title,
            status=error.status_code,
            detail=error.detail,
            instance=instance,
            voilations=error.voialations,
            type=error.__class__.__name__,
            error_log=error.error_log,
            error_stacktrace=traceback.format_exc(),
        )
        return JSONResponse(
            content=error_model.model_dump(),
            status_code=error.status_code,
            headers=error.headers,
            media_type=ErrorMediaType,
        )

    def handle_fastapi_http_error(
        self, instance: str, error: HTTPException
    ) -> JSONResponse:
        logger.exception(error)
        ErrorModel = self.error_model_builder.build(status_code=error.status_code)
        error_model = ErrorModel(
            title=convert_status_code_to_text(error.status_code),
            status=error.status_code,
            detail=error.detail,
            instance=instance,
            voilations={},
            type=error.__class__.__name__,
            error_log={},
            error_stacktrace=traceback.format_exc(),
        )
        return JSONResponse(
            content=error_model.model_dump(),
            status_code=error.status_code,
            headers=error.headers,
            media_type=ErrorMediaType,
        )

    def handle_expired_signature(self, instance: str, error) -> JSONResponse:
        logger.warning(error)
        ErrorModel = self.error_model_builder.build(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
        error_model = ErrorModel(
            detail="expired_signature_error",
            instance=instance,
        )
        return JSONResponse(
            content=error_model.model_dump(),
            status_code=error_model.status,
            media_type=ErrorMediaType,
        )

    def handle_request_validation_error(
        self, instance: str, error: RequestValidationError
    ) -> JSONResponse:
        logger.warning(error)

        log_messages, errors = [], []
        for err in error.errors():
            log_message = f"{err['msg']} in {err['loc'][0]}"
            if len(err["loc"]) > 1:
                log_message = f"{err['loc'][1]} {log_message}"
            log_messages.append(log_message)
            # pop non-serializable object `ctx`
            err.pop("ctx", None)
            errors.append(err)

        ErrorModel = self.error_model_builder.build(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        error_model = ErrorModel(
            detail=" && ".join(log_messages),
            instance=instance,
            voilations={"errors": errors},
            type=error.__class__.__name__,
            error_log={},
            error_stacktrace=traceback.format_exc(),
        )
        return JSONResponse(
            content=error_model.model_dump(),
            status_code=error_model.status,
            media_type=ErrorMediaType,
        )

    def handle_pydantic_validation_error(
        self, instance: str, error: ValidationError
    ) -> JSONResponse:
        logger.warning(error)

        log_messages, errors = [], []
        for err in error.errors():
            log_message = f"{err['msg']} {err['loc'][0]} in model"
            log_messages.append(log_message)
            # pop non-serializable object `ctx`
            err.pop("ctx", None)
            errors.append(err)

        ErrorModel = self.error_model_builder.build(
            status_code=status.HTTP_400_BAD_REQUEST
        )
        error_model = ErrorModel(
            detail=" && ".join(log_messages),
            instance=instance,
            voilations={"errors": errors},
            type=error.__class__.__name__,
            error_log={},
            error_stacktrace=traceback.format_exc(),
        )
        return JSONResponse(
            content=error_model.model_dump(),
            status_code=error_model.status,
            media_type=ErrorMediaType,
        )

    def handle_base_error(self, instance: str, error: BaseException) -> JSONResponse:
        logger.exception(error)

        ErrorModel = self.error_model_builder.build(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        error_model = ErrorModel(
            detail="",
            instance=instance,
            voilations={},
            type=error.__class__.__name__,
            error_log={},
            error_stacktrace=traceback.format_exc(),
        )
        return JSONResponse(
            content=error_model.model_dump(),
            status_code=error_model.status,
            media_type=ErrorMediaType,
        )
