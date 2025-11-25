"""Section model for recursive document structure."""

from __future__ import annotations

import re
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Section(BaseModel):
    """Represents a section in a legal document.

    Sections can be nested recursively to unlimited depth. Each section
    must have a stable identifier and a marker for reliable diffing across
    versions. Markers are the primary identifiers used for matching sections.

    Attributes:
        id: Unique identifier (string). Auto-generated UUID if not provided.
            Must match pattern: alphanumeric characters, hyphens, underscores.
        marker: Required structural marker (e.g., "א", "1", "a"). Used as
            primary identifier for diffing. Must be unique within same nesting level.
        content: Text content for this section level only (not children).
            Defaults to empty string. Supports Hebrew text (UTF-8).
        title: Optional section title. Supports Hebrew text (UTF-8).
        sections: Required list of nested child sections (can be empty).

    Examples:
        >>> section = Section(id="sec-1", marker="1", content="Hello")
        >>> nested = Section(id="sec-1-a", marker="א", content="World", sections=[section])
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier (string). Auto-generated UUID if not provided.",
        min_length=1,
    )
    marker: str = Field(
        description="Required structural marker (e.g., 'א', '1', 'a'). Used for diffing.",
        min_length=1,
    )
    content: str = Field(
        default="",
        description="Text content for this section level only (not children).",
    )
    title: str | None = Field(
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
        """Validate that id matches the required pattern.

        The pattern allows alphanumeric characters, hyphens, and underscores.
        This means auto-generated UUIDs (which contain hyphens, e.g.,
        "550e8400-e29b-41d4-a716-446655440000") are valid and will pass validation.
        """
        pattern = r"^[a-zA-Z0-9_-]+$"
        if not re.match(pattern, v):
            raise ValueError(f"Section id must match pattern [a-zA-Z0-9_-], got: {v}")
        return v

    model_config = {
        "str_strip_whitespace": False,  # Preserve whitespace in content
        "validate_assignment": True,
        "frozen": False,  # Allow mutation for diffing operations
    }
