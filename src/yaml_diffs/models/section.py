"""Section model for recursive document structure."""

from __future__ import annotations

import re
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Section(BaseModel):
    """Represents a section in a legal document.

    Sections can be nested recursively to unlimited depth. Each section
    must have a stable identifier for reliable diffing across versions.

    Attributes:
        id: Unique identifier (string). Auto-generated UUID if not provided.
            Must match pattern: alphanumeric characters, hyphens, underscores.
        content: Text content for this section level only (not children).
            Defaults to empty string. Supports Hebrew text (UTF-8).
        marker: Optional structural marker (e.g., "א", "1", "a").
        title: Optional section title. Supports Hebrew text (UTF-8).
        sections: Required list of nested child sections (can be empty).

    Examples:
        >>> section = Section(id="sec-1", content="Hello")
        >>> nested = Section(id="sec-1-a", content="World", sections=[section])
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier (string). Auto-generated UUID if not provided.",
        min_length=1,
    )
    content: str = Field(
        default="",
        description="Text content for this section level only (not children).",
    )
    marker: Optional[str] = Field(
        default=None,
        description="Optional structural marker (e.g., 'א', '1', 'a').",
    )
    title: Optional[str] = Field(
        default=None,
        description="Optional section title.",
    )
    sections: list[Section] = Field(
        default_factory=list,
        description="Required list of nested child sections (can be empty).",
    )

    @field_validator("id")
    @classmethod
    def validate_id_pattern(cls, v: str) -> str:
        """Validate that id matches the required pattern."""
        pattern = r"^[a-zA-Z0-9_-]+$"
        if not re.match(pattern, v):
            raise ValueError(f"Section id must match pattern [a-zA-Z0-9_-], got: {v}")
        return v

    model_config = {
        "str_strip_whitespace": False,  # Preserve whitespace in content
        "validate_assignment": True,
        "frozen": False,  # Allow mutation for diffing operations
    }
