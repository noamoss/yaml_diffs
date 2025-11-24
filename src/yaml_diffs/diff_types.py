"""Diff result types for document diffing."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    """Type of change detected in document diffing.

    Attributes:
        ADDED: New marker in new version
        DELETED: Marker removed from old version
        CONTENT_CHANGED: Same marker+path, content changed
        MOVED: Same marker, different parent path
        RENAMED: Same marker+path+content, title changed
        UNCHANGED: No changes detected
    """

    ADDED = "added"
    DELETED = "deleted"
    CONTENT_CHANGED = "content_changed"
    MOVED = "moved"
    RENAMED = "renamed"
    UNCHANGED = "unchanged"


class DiffResult(BaseModel):
    """Represents a single change detected in document diffing.

    Attributes:
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
    """

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
    old_marker_path: Optional[tuple[str, ...]] = Field(
        default=None,
        description="Marker path in old version (markers from root)",
    )
    new_marker_path: Optional[tuple[str, ...]] = Field(
        default=None,
        description="Marker path in new version",
    )
    old_id_path: Optional[list[str]] = Field(
        default=None,
        description="ID path in old version (for tracking)",
    )
    new_id_path: Optional[list[str]] = Field(
        default=None,
        description="ID path in new version (for tracking)",
    )
    old_content: Optional[str] = Field(
        default=None,
        description="Content in old version",
    )
    new_content: Optional[str] = Field(
        default=None,
        description="Content in new version",
    )
    old_title: Optional[str] = Field(
        default=None,
        description="Title in old version",
    )
    new_title: Optional[str] = Field(
        default=None,
        description="Title in new version",
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
