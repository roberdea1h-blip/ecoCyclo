from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import EcoCycleException


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EcoCycleException)
    async def eco_cycle_exception_handler(request: Request, exc: EcoCycleException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error_code": "validation_error",
                "message": "Datos inválidos en la solicitud",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "internal_server_error",
                "message": "Ocurrió un error inesperado",
                "details": None,
            },
        )
