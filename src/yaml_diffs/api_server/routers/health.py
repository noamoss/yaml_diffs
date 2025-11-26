"""Health check endpoint for API server.

Provides a simple health check endpoint required for Railway deployment.
"""

from fastapi import APIRouter

from yaml_diffs.api_server.config import settings
from yaml_diffs.api_server.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns a simple health status response. This endpoint is required
    for Railway deployment and monitoring.

    Returns:
        HealthResponse with status and version information.

    Examples:
        >>> GET /health
        {
            "status": "healthy",
            "version": "0.1.0"
        }
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
    )

