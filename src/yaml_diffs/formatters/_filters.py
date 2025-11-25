"""Filtering utilities for diff results."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from yaml_diffs.diff_types import ChangeType, DiffResult

if TYPE_CHECKING:
    from collections.abc import Sequence


def format_marker_path(marker_path: tuple[str, ...] | None) -> str:
    """Format marker path tuple as a readable string.

    Args:
        marker_path: Tuple of markers from root, or None

    Returns:
        Formatted path string (e.g., "פרק א' -> 1 -> (א)") or empty string

    Examples:
        >>> format_marker_path(("פרק א'", "1", "(א)"))
        "פרק א' -> 1 -> (א)"
        >>> format_marker_path(None)
        ""
        >>> format_marker_path(())
        ""
    """
    if not marker_path:
        return ""
    return " -> ".join(marker_path)


def filter_by_change_type(
    changes: list[DiffResult],
    change_types: Sequence[ChangeType] | None,
) -> list[DiffResult]:
    """Filter changes by change type.

    Args:
        changes: List of diff results to filter
        change_types: List of change types to include, or None to include all

    Returns:
        Filtered list of changes

    Examples:
        >>> changes = [
        ...     DiffResult(..., change_type=ChangeType.SECTION_ADDED),
        ...     DiffResult(..., change_type=ChangeType.CONTENT_CHANGED),
        ... ]
        >>> filtered = filter_by_change_type(changes, [ChangeType.SECTION_ADDED])
        >>> len(filtered)
        1
    """
    if change_types is None:
        return changes
    change_type_set = set(change_types)
    return [change for change in changes if change.change_type in change_type_set]


def filter_by_section_path(
    changes: list[DiffResult],
    section_path: str | None,
) -> list[DiffResult]:
    """Filter changes by section marker path.

    Matches changes where either old_marker_path or new_marker_path
    matches the provided path (exact match).

    Args:
        changes: List of diff results to filter
        section_path: Marker path string to match (e.g., "פרק א' -> 1"), or None

    Returns:
        Filtered list of changes

    Examples:
        >>> changes = [
        ...     DiffResult(..., old_marker_path=("פרק א'", "1")),
        ...     DiffResult(..., old_marker_path=("פרק ב'", "1")),
        ... ]
        >>> filtered = filter_by_section_path(changes, "פרק א' -> 1")
        >>> len(filtered)
        1
    """
    if section_path is None:
        return changes

    # Normalize empty strings to None
    section_path = section_path.strip() if section_path else None
    if not section_path:
        return changes

    # Convert path string to tuple for comparison
    # Split by " -> " to handle marker paths
    path_parts = [part.strip() for part in section_path.split(" -> ") if part.strip()]
    if not path_parts:  # Empty path after splitting
        return changes

    path_tuple = tuple(path_parts)

    filtered = []
    for change in changes:
        # Check if old or new marker path matches
        if change.old_marker_path == path_tuple or change.new_marker_path == path_tuple:
            filtered.append(change)

    return filtered


def diff_result_to_dict(change: DiffResult) -> dict[str, Any]:
    """Convert DiffResult to dictionary for serialization.

    Args:
        change: DiffResult to convert

    Returns:
        Dictionary representation suitable for JSON/YAML serialization
    """
    result: dict[str, Any] = {
        "section_id": change.section_id,
        "change_type": change.change_type.value,
        "marker": change.marker,
    }

    # Add marker paths (convert tuple to list for serialization)
    result["old_marker_path"] = (
        list(change.old_marker_path) if change.old_marker_path is not None else None
    )
    result["new_marker_path"] = (
        list(change.new_marker_path) if change.new_marker_path is not None else None
    )

    # Add ID paths
    result["old_id_path"] = change.old_id_path
    result["new_id_path"] = change.new_id_path

    # Add content and title
    result["old_content"] = change.old_content
    result["new_content"] = change.new_content
    result["old_title"] = change.old_title
    result["new_title"] = change.new_title

    return result


def calculate_summary_counts(changes: list[DiffResult]) -> dict[str, int]:
    """Calculate summary counts from a list of changes.

    Args:
        changes: List of filtered changes

    Returns:
        Dictionary with added_count, deleted_count, modified_count, moved_count
    """
    added_count = sum(1 for c in changes if c.change_type == ChangeType.SECTION_ADDED)
    deleted_count = sum(1 for c in changes if c.change_type == ChangeType.SECTION_REMOVED)
    modified_count = sum(
        1
        for c in changes
        if c.change_type in (ChangeType.CONTENT_CHANGED, ChangeType.TITLE_CHANGED)
    )
    moved_count = sum(1 for c in changes if c.change_type == ChangeType.SECTION_MOVED)

    return {
        "added_count": added_count,
        "deleted_count": deleted_count,
        "modified_count": modified_count,
        "moved_count": moved_count,
    }


__all__ = [
    "format_marker_path",
    "filter_by_change_type",
    "filter_by_section_path",
    "diff_result_to_dict",
    "calculate_summary_counts",
]
