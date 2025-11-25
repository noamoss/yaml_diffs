"""Main FastAPI application for yaml-diffs REST API.

Creates and configures the FastAPI app with routers, middleware, and exception handlers.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from yaml_diffs.__version__ import __version__
from yaml_diffs.api_server.config import configure_logging, settings
from yaml_diffs.api_server.routers import diff, health, validate
from yaml_diffs.exceptions import (
    OpenSpecValidationError,
    PathValidationError,
    PydanticValidationError,
    ValidationError,
    YAMLLoadError,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown events.

    Configures logging and logs startup/shutdown information.
    """
    # Startup
    configure_logging(settings.log_level)
    logger.info(f"Starting {settings.app_name} v{__version__}")
    logger.info(f"Server will bind to {settings.host}:{settings.port_from_env}")
    logger.info(f"Log level: {settings.log_level}")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name,
    description="REST API for validating and diffing Hebrew legal documents in YAML format",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Exception handlers
@app.exception_handler(YAMLLoadError)
async def yaml_load_error_handler(request: Request, exc: YAMLLoadError) -> JSONResponse:
    """Handle YAMLLoadError exceptions.

    Args:
        request: FastAPI request object.
        exc: YAMLLoadError exception.

    Returns:
        JSONResponse with 400 Bad Request status.
    """
    logger.warning(f"YAML load error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "YAMLLoadError",
            "message": str(exc),
            "details": [{"file_path": exc.file_path}] if exc.file_path else None,
        },
    )


@app.exception_handler(PathValidationError)
async def path_validation_error_handler(request: Request, exc: PathValidationError) -> JSONResponse:
    """Handle PathValidationError exceptions.

    This handler is for security violations related to path validation.
    It returns a generic error message to avoid exposing internal file system
    structure while logging the actual violation for monitoring.

    Args:
        request: FastAPI request object.
        exc: PathValidationError exception.

    Returns:
        JSONResponse with 400 Bad Request status.
    """
    logger.warning(f"Path validation error (security violation): {exc.reason} - {exc.file_path}")
    # Don't expose internal paths in error message for security
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "PathValidationError",
            "message": "Invalid file path provided",
            "details": None,  # Don't expose path details
        },
    )


@app.exception_handler(OpenSpecValidationError)
async def openspec_validation_error_handler(
    request: Request, exc: OpenSpecValidationError
) -> JSONResponse:
    """Handle OpenSpecValidationError exceptions.

    Args:
        request: FastAPI request object.
        exc: OpenSpecValidationError exception.

    Returns:
        JSONResponse with 422 Unprocessable Entity status.
    """
    logger.warning(f"OpenSpec validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "OpenSpecValidationError",
            "message": str(exc),
            "details": exc.errors,
        },
    )


@app.exception_handler(PydanticValidationError)
async def pydantic_validation_error_handler(
    request: Request, exc: PydanticValidationError
) -> JSONResponse:
    """Handle PydanticValidationError exceptions.

    Args:
        request: FastAPI request object.
        exc: PydanticValidationError exception.

    Returns:
        JSONResponse with 422 Unprocessable Entity status.
    """
    logger.warning(f"Pydantic validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "PydanticValidationError",
            "message": str(exc),
            "details": exc.errors,
        },
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle generic ValidationError exceptions.

    Args:
        request: FastAPI request object.
        exc: ValidationError exception.

    Returns:
        JSONResponse with 422 Unprocessable Entity status.
    """
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": str(exc),
            "details": exc.errors,
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions.

    Args:
        request: FastAPI request object.
        exc: ValueError exception.

    Returns:
        JSONResponse with 400 Bad Request status.
    """
    logger.warning(f"Value error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ValueError",
            "message": str(exc),
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions.

    Args:
        request: FastAPI request object.
        exc: Generic exception.

    Returns:
        JSONResponse with 500 Internal Server Error status.
    """
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": type(exc).__name__,
            "message": "An unexpected error occurred",
        },
    )


# Include routers
app.include_router(health.router)
app.include_router(validate.router)
app.include_router(diff.router)


@app.get("/", tags=["root"])
def root() -> dict[str, Any]:
    """Root endpoint with API information.

    Returns:
        Dictionary with API information and links to documentation.
    """
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "health": "/health",
    }
