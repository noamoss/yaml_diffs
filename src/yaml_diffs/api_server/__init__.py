"""REST API server for yaml-diffs service.

This package provides a FastAPI-based REST API for document validation and diffing.
The API is designed for Railway deployment with proper environment configuration,
health checks, and error handling.
"""

from yaml_diffs.api_server.main import app

__all__ = ["app"]

