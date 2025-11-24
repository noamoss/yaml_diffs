"""Text formatter for human-readable diff output."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from yaml_diffs.diff_types import ChangeType, DiffResult, DocumentDiff
from yaml_diffs.formatters._filters import (
    calculate_summary_counts,
    filter_by_change_type,
    filter_by_section_path,
    format_marker_path,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


class TextFormatter:
    """Formatter for outputting diff results as human-readable text.

    Provides context-rich text output with clear before/after comparisons
    and prominent marker path display.
    """

    @staticmethod
    def format(
        diff: DocumentDiff,
        filter_change_types: Optional[Sequence[ChangeType]] = None,
        filter_section_path: Optional[str] = None,
        show_context: bool = True,
    ) -> str:
        """Format diff as human-readable text.

        Args:
            diff: DocumentDiff to format
            filter_change_types: Optional list of change types to include
            filter_section_path: Optional marker path to filter by (exact match)
            show_context: Whether to show context around changes (default: True)

        Returns:
            Human-readable text representation of the diff

        Examples:
            >>> formatter = TextFormatter()
            >>> text = formatter.format(diff)
            >>> print(text)
        """
        lines = []

        # Apply filters first
        changes = diff.changes
        if filter_change_types is not None:
            changes = filter_by_change_type(changes, filter_change_types)
        if filter_section_path is not None:
            changes = filter_by_section_path(changes, filter_section_path)

        # Recalculate summary counts from filtered changes
        summary = calculate_summary_counts(changes)

        # Summary section
        lines.append("Document Diff Summary:")
        lines.append(f"  - Added: {summary['added_count']} section(s)")
        lines.append(f"  - Deleted: {summary['deleted_count']} section(s)")
        lines.append(f"  - Modified: {summary['modified_count']} section(s)")
        lines.append(f"  - Moved: {summary['moved_count']} section(s)")
        lines.append("")

        # Changes section
        if not changes:
            lines.append("No changes found.")
            return "\n".join(lines)

        lines.append("Changes:")
        lines.append("")

        for i, change in enumerate(changes, 1):
            lines.extend(_format_change(change, show_context))
            if i < len(changes):
                lines.append("")  # Separator between changes

        return "\n".join(lines)


def _format_change(change: DiffResult, show_context: bool) -> list[str]:
    """Format a single change as text lines.

    Args:
        change: DiffResult to format
        show_context: Whether to show context

    Returns:
        List of text lines for this change
    """
    lines = []

    # Change type and marker path header
    change_type_display = change.change_type.value.upper().replace("_", " ")
    marker_path = _get_display_marker_path(change)
    lines.append(f"[{change_type_display}] {marker_path}")

    # Section ID
    lines.append(f"Section ID: {change.section_id}")
    lines.append("")

    # Title changes
    if change.old_title != change.new_title:
        if change.old_title:
            lines.append(f"Old title: {change.old_title}")
        if change.new_title:
            lines.append(f"New title: {change.new_title}")
        if change.old_title or change.new_title:
            lines.append("")

    # Content changes
    if change.old_content != change.new_content:
        if change.old_content is not None:
            lines.append("Old content:")
            if show_context and change.old_content.strip():
                # Indent content for readability
                content_lines = change.old_content.split("\n")
                for line in content_lines:
                    lines.append(f"  {line}")
            else:
                lines.append(f"  {change.old_content}")
            lines.append("")

        if change.new_content is not None:
            lines.append("New content:")
            if show_context and change.new_content.strip():
                # Indent content for readability
                content_lines = change.new_content.split("\n")
                for line in content_lines:
                    lines.append(f"  {line}")
            else:
                lines.append(f"  {change.new_content}")
            lines.append("")

    # Path changes (for moved sections)
    if change.old_marker_path != change.new_marker_path:
        old_path_str = format_marker_path(change.old_marker_path)
        new_path_str = format_marker_path(change.new_marker_path)
        if old_path_str and new_path_str:
            lines.append(f"Old path: {old_path_str}")
            lines.append(f"New path: {new_path_str}")
            lines.append("")

    # Show unchanged content for context (if show_context is True)
    if show_context and change.change_type == ChangeType.UNCHANGED:
        if change.new_title:
            lines.append(f"Title: {change.new_title}")
        if change.new_content:
            lines.append("Content:")
            content_lines = change.new_content.split("\n")
            for line in content_lines:
                lines.append(f"  {line}")

    return lines


def _get_display_marker_path(change: DiffResult) -> str:
    """Get the marker path to display for a change.

    Prefers new_marker_path if available, otherwise old_marker_path.

    Args:
        change: DiffResult to get path from

    Returns:
        Formatted marker path string
    """
    # For added sections, use new path
    if change.change_type == ChangeType.SECTION_ADDED:
        return format_marker_path(change.new_marker_path) or change.marker

    # For removed sections, use old path
    if change.change_type == ChangeType.SECTION_REMOVED:
        return format_marker_path(change.old_marker_path) or change.marker

    # For moved sections, show both paths
    if change.change_type == ChangeType.SECTION_MOVED:
        old_path = format_marker_path(change.old_marker_path)
        new_path = format_marker_path(change.new_marker_path)
        if old_path and new_path and old_path != new_path:
            return f"{old_path} -> {new_path}"
        return new_path or old_path or change.marker

    # For other changes, prefer new path, fallback to old
    path = format_marker_path(change.new_marker_path) or format_marker_path(change.old_marker_path)
    return path or change.marker
