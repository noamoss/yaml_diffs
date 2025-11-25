"""API request and response schemas.

Defines Pydantic models for API request/response validation and serialization.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from pydantic import BaseModel, Field

from yaml_diffs.diff_types import DocumentDiff
from yaml_diffs.models import Document


def _get_max_yaml_size() -> int:
    """Get maximum YAML size from environment variable.

    Returns:
        Maximum YAML size in bytes, defaulting to 10MB if not set or invalid.
    """
    value = os.getenv("MAX_YAML_SIZE", "10_000_000")
    try:
        return int(value)
    except ValueError:
        logging.warning(
            f"Invalid MAX_YAML_SIZE environment variable: {value}. Using default: 10_000_000"
        )
        return 10_000_000


# Maximum YAML size (10MB default, configurable via environment variable)
MAX_YAML_SIZE = _get_max_yaml_size()


class ValidateRequest(BaseModel):
    """Request schema for document validation endpoint.

    Attributes:
        yaml: YAML content as string to validate.
    """

    yaml: str = Field(
        description="YAML document content as string",
        min_length=1,
        max_length=MAX_YAML_SIZE,
        examples=[
            """document:
  id: "law-1234"
  title: "חוק הדוגמה"
  type: "law"
  language: "hebrew"
  version:
    number: "2024-01-01"
  source:
    url: "https://example.gov.il/law1234"
    fetched_at: "2025-01-20T09:50:00Z"
  sections: []"""
        ],
    )


class ValidateResponse(BaseModel):
    """Response schema for document validation endpoint.

    Attributes:
        valid: Whether the document is valid.
        document: Validated document object (if valid).
        error: Error type (if invalid).
        message: Human-readable error message (if invalid).
        details: Detailed error information (if invalid).
    """

    valid: bool = Field(description="Whether the document is valid")
    document: Document | None = Field(
        default=None, description="Validated document object (if valid)"
    )
    error: str | None = Field(default=None, description="Error type (if invalid)")
    message: str | None = Field(
        default=None, description="Human-readable error message (if invalid)"
    )
    details: list[dict[str, Any]] | None = Field(
        default=None, description="Detailed error information (if invalid)"
    )


class DiffRequest(BaseModel):
    """Request schema for document diff endpoint.

    Attributes:
        old_yaml: Old document version YAML content as string.
        new_yaml: New document version YAML content as string.
    """

    old_yaml: str = Field(
        description="Old document version YAML content as string",
        min_length=1,
        max_length=MAX_YAML_SIZE,
        examples=[
            """document:
  id: "law-1234"
  title: "חוק הדוגמה"
  type: "law"
  language: "hebrew"
  version:
    number: "2024-01-01"
  source:
    url: "https://example.gov.il/law1234"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: "1"
      content: "Original content"
      sections: []"""
        ],
    )
    new_yaml: str = Field(
        description="New document version YAML content as string",
        min_length=1,
        max_length=MAX_YAML_SIZE,
        examples=[
            """document:
  id: "law-1234"
  title: "חוק הדוגמה"
  type: "law"
  language: "hebrew"
  version:
    number: "2024-01-01"
  source:
    url: "https://example.gov.il/law1234"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: "1"
      content: "Updated content"
      sections: []"""
        ],
    )


class DiffResponse(BaseModel):
    """Response schema for document diff endpoint.

    Attributes:
        diff: DocumentDiff object containing all detected changes.
    """

    diff: DocumentDiff = Field(description="Document diff results")


class ErrorResponse(BaseModel):
    """Standardized error response schema.

    Attributes:
        error: Error type/class name.
        message: Human-readable error message.
        details: Optional detailed error information.
    """

    error: str = Field(description="Error type/class name")
    message: str = Field(description="Human-readable error message")
    details: list[dict[str, Any]] | None = Field(
        default=None, description="Optional detailed error information"
    )


class HealthResponse(BaseModel):
    """Response schema for health check endpoint.

    Attributes:
        status: Health status (always "healthy" if endpoint is reachable).
        version: Application version.
    """

    status: str = Field(default="healthy", description="Health status")
    version: str = Field(description="Application version")
