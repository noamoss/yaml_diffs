"""Diff output formatters for various formats."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from yaml_diffs.diff_types import ChangeType, DocumentDiff
from yaml_diffs.formatters._filters import (
    filter_by_change_type,
    filter_by_section_path,
    format_marker_path,
)
from yaml_diffs.formatters.json_formatter import JsonFormatter
from yaml_diffs.formatters.text_formatter import TextFormatter
from yaml_diffs.formatters.yaml_formatter import YamlFormatter

if TYPE_CHECKING:
    from collections.abc import Sequence


def format_diff(
    diff: DocumentDiff,
    output_format: str = "json",
    filter_change_types: Optional[Sequence[ChangeType]] = None,
    filter_section_path: Optional[str] = None,
    **kwargs,
) -> str:
    """Format diff using the specified formatter.

    Convenience function to format a DocumentDiff using any of the
    available formatters.

    Args:
        diff: DocumentDiff to format
        output_format: Output format ("json", "text", or "yaml", default: "json")
        filter_change_types: Optional list of change types to include
        filter_section_path: Optional marker path to filter by (exact match)
        **kwargs: Additional formatter-specific options

    Returns:
        Formatted string representation of the diff

    Raises:
        ValueError: If output_format is not one of "json", "text", or "yaml"

    Examples:
        >>> diff = diff_documents(old_doc, new_doc)
        >>> json_output = format_diff(diff, output_format="json")
        >>> text_output = format_diff(diff, output_format="text")
        >>> yaml_output = format_diff(diff, output_format="yaml")
    """
    if output_format == "json":
        formatter = JsonFormatter()
        return formatter.format(
            diff,
            filter_change_types=filter_change_types,
            filter_section_path=filter_section_path,
            **kwargs,
        )
    elif output_format == "text":
        formatter = TextFormatter()  # type: ignore[assignment]
        return formatter.format(
            diff,
            filter_change_types=filter_change_types,
            filter_section_path=filter_section_path,
            **kwargs,
        )
    elif output_format == "yaml":
        formatter = YamlFormatter()  # type: ignore[assignment]
        return formatter.format(
            diff,
            filter_change_types=filter_change_types,
            filter_section_path=filter_section_path,
            **kwargs,
        )
    else:
        raise ValueError(f"Unknown format: {output_format}. Must be one of: json, text, yaml")


__all__ = [
    "format_marker_path",
    "filter_by_change_type",
    "filter_by_section_path",
    "JsonFormatter",
    "TextFormatter",
    "YamlFormatter",
    "format_diff",
]
