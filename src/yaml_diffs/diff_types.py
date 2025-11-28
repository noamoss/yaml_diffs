"""Diff result types for document diffing."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    """Type of change detected in document diffing.

    Attributes:
        SECTION_ADDED: New section added in new version
        SECTION_REMOVED: Section removed from old version
        CONTENT_CHANGED: Content changed (same marker+path)
        SECTION_MOVED: Path changed (and possibly marker changed) but title+content same
        TITLE_CHANGED: Title changed (same marker+path+content)
        UNCHANGED: No changes detected
    """

    SECTION_ADDED = "section_added"
    SECTION_REMOVED = "section_removed"
    CONTENT_CHANGED = "content_changed"
    SECTION_MOVED = "section_moved"
    TITLE_CHANGED = "title_changed"
    UNCHANGED = "unchanged"


class DiffResult(BaseModel):
    """Represents a single change detected in document diffing.

    Attributes:
        id: Unique identifier for this change (UUID)
        section_id: The section ID (for tracking, from old or new version)
        change_type: Type of change detected
        marker: The section marker (primary identifier)
        old_marker_path: Marker path in old version (markers from root)
        new_marker_path: Marker path in new version
        old_id_path: ID path in old version (for tracking)
        new_id_path: ID path in new version (for tracking)
        old_content: Content in old version
        new_content: Content in new version
        old_title: Title in old version
        new_title: Title in new version
        old_section_yaml: Full YAML representation of section in old version
        new_section_yaml: Full YAML representation of section in new version
        old_line_number: Starting line number in old document (1-indexed)
        new_line_number: Starting line number in new document (1-indexed)
    """

    id: str = Field(
        description="Unique identifier for this change (UUID)",
        min_length=1,
    )
    section_id: str = Field(
        description="The section ID (for tracking, from old or new version)",
        min_length=1,
    )
    change_type: ChangeType = Field(
        description="Type of change detected",
    )
    marker: str = Field(
        description="The section marker (primary identifier)",
        min_length=1,
    )
    old_marker_path: tuple[str, ...] | None = Field(
        default=None,
        description="Marker path in old version (markers from root)",
    )
    new_marker_path: tuple[str, ...] | None = Field(
        default=None,
        description="Marker path in new version",
    )
    old_id_path: list[str] | None = Field(
        default=None,
        description="ID path in old version (for tracking)",
    )
    new_id_path: list[str] | None = Field(
        default=None,
        description="ID path in new version (for tracking)",
    )
    old_content: str | None = Field(
        default=None,
        description="Content in old version",
    )
    new_content: str | None = Field(
        default=None,
        description="Content in new version",
    )
    old_title: str | None = Field(
        default=None,
        description="Title in old version",
    )
    new_title: str | None = Field(
        default=None,
        description="Title in new version",
    )
    old_section_yaml: str | None = Field(
        default=None,
        description="Full YAML representation of section in old version",
    )
    new_section_yaml: str | None = Field(
        default=None,
        description="Full YAML representation of section in new version",
    )
    old_line_number: int | None = Field(
        default=None,
        description="Starting line number in old document (1-indexed)",
    )
    new_line_number: int | None = Field(
        default=None,
        description="Starting line number in new document (1-indexed)",
    )

    model_config = {
        "str_strip_whitespace": False,
        "validate_assignment": True,
        "frozen": False,
    }


class DocumentDiff(BaseModel):
    """Complete diff results for two document versions.

    Attributes:
        changes: List of all changes detected
        added_count: Count of added sections
        deleted_count: Count of deleted sections
        modified_count: Count of modified sections (content/title changes)
        moved_count: Count of moved sections
    """

    changes: list[DiffResult] = Field(
        default_factory=list,
        description="List of all changes detected",
    )
    added_count: int = Field(
        default=0,
        description="Count of added sections",
        ge=0,
    )
    deleted_count: int = Field(
        default=0,
        description="Count of deleted sections",
        ge=0,
    )
    modified_count: int = Field(
        default=0,
        description="Count of modified sections (content/title changes)",
        ge=0,
    )
    moved_count: int = Field(
        default=0,
        description="Count of moved sections",
        ge=0,
    )

    model_config = {
        "str_strip_whitespace": False,
        "validate_assignment": True,
        "frozen": False,
    }
