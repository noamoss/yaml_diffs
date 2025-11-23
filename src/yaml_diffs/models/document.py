"""Document model for legal documents."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

from yaml_diffs.models.section import Section


class DocumentType(str, Enum):
    """Type of legal document."""

    LAW = "law"
    REGULATION = "regulation"
    DIRECTIVE = "directive"
    CIRCULAR = "circular"
    POLICY = "policy"
    OTHER = "other"


class Version(BaseModel):
    """Document version information.

    Attributes:
        number: Version identifier or date (e.g., "2024-11-01", "v1.0").
        description: Optional version description.
    """

    number: str = Field(
        description="Version identifier or date (e.g., '2024-11-01', 'v1.0').",
        min_length=1,
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional version description.",
    )


class Source(BaseModel):
    """Document source information.

    Attributes:
        url: Original source URL (must be valid URI).
        fetched_at: ISO 8601 timestamp when document was fetched.
    """

    url: str = Field(
        description="Original source URL (must be valid URI).",
        min_length=1,
    )
    fetched_at: str = Field(
        description="ISO 8601 timestamp when document was fetched.",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that url is a valid URI."""
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError(f"url must be a valid URI with scheme and netloc, got: {v}")
            return v
        except Exception as err:
            raise ValueError(f"url must be a valid URI, got: {v}") from err

    @field_validator("fetched_at")
    @classmethod
    def validate_fetched_at_format(cls, v: str) -> str:
        """Validate that fetched_at is in ISO 8601 format."""
        try:
            # Handle 'Z' timezone indicator - only replace trailing 'Z'
            # Guard against edge case where v is just "Z"
            if v.endswith("Z") and len(v) > 1:
                date_str = v[:-1] + "+00:00"
            else:
                date_str = v
            datetime.fromisoformat(date_str)
            return v
        except ValueError as err:
            raise ValueError(
                f"fetched_at must be in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS), got: {v}"
            ) from err


class Document(BaseModel):
    """Represents a complete legal document.

    A document contains metadata and a list of root sections. Sections can be
    nested recursively to unlimited depth. Matches the JSON Schema structure.

    Attributes:
        id: Stable document identifier (recommended: UUID or canonical ID).
        title: Document title in Hebrew. Required.
        type: Type of legal document (law, regulation, directive, etc.). Required.
        language: Document language (must be 'hebrew'). Required.
        version: Document version information (object with number and optional description). Required.
        source: Document source information (object with url and fetched_at). Required.
        authors: Optional list of authors, entities, or organizations. Supports Hebrew text.
        published_date: Optional publication date in ISO 8601 format.
        updated_date: Optional last update date in ISO 8601 format.
        sections: Required list of root-level sections in the document (can be empty).

    Examples:
        >>> doc = Document(
        ...     id="law-1234",
        ...     title="חוק יסוד: כבוד האדם וחירותו",
        ...     type=DocumentType.LAW,
        ...     language="hebrew",
        ...     version=Version(number="1.0"),
        ...     source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
        ...     authors=["הכנסת"],
        ...     published_date="1992-03-17",
        ...     updated_date="2024-01-15",
        ...     sections=[Section(id="sec-1", content="Introduction")]
        ... )
    """

    id: str = Field(
        description="Stable document identifier (recommended: UUID or canonical ID).",
        min_length=1,
    )
    title: str = Field(
        description="Document title in Hebrew. Required.",
        min_length=1,
    )
    type: DocumentType = Field(
        description="Type of legal document (law, regulation, directive, etc.). Required.",
    )
    language: Literal["hebrew"] = Field(
        default="hebrew",
        description="Document language (must be 'hebrew'). Required.",
    )
    version: Version = Field(
        description="Document version information (object with number and optional description). Required.",
    )
    source: Source = Field(
        description="Document source information (object with url and fetched_at). Required.",
    )
    authors: Optional[list[str]] = Field(
        default=None,
        description="Optional list of authors, entities, or organizations. Supports Hebrew text (UTF-8).",
    )
    published_date: Optional[str] = Field(
        default=None,
        description="Optional publication date in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).",
    )
    updated_date: Optional[str] = Field(
        default=None,
        description="Optional last update date in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).",
    )
    sections: list[Section] = Field(
        default_factory=list,
        description="Required list of root-level sections in the document (can be empty).",
    )

    @field_validator("published_date", "updated_date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate that date strings are in ISO 8601 format."""
        if v is None:
            return v
        try:
            # Try parsing as ISO 8601 (supports both date and datetime)
            # Handle 'Z' timezone indicator - only replace trailing 'Z'
            # Guard against edge case where v is just "Z"
            if v.endswith("Z") and len(v) > 1:
                date_str = v[:-1] + "+00:00"
            else:
                date_str = v
            datetime.fromisoformat(date_str)
            return v
        except ValueError as err:
            raise ValueError(
                f"Date must be in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS), got: {v}"
            ) from err

    model_config = {
        "str_strip_whitespace": False,  # Preserve whitespace in metadata
        "validate_assignment": True,
        "frozen": False,  # Allow mutation for diffing operations
    }
