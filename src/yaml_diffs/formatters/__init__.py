"""Diff output formatters for various formats."""

from __future__ import annotations

import inspect
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
    # Filter kwargs to only include parameters accepted by the selected formatter
    if output_format == "json":
        formatter = JsonFormatter()
        # Get valid parameters for JsonFormatter.format()
        sig = inspect.signature(formatter.format)
        valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return formatter.format(
            diff,
            filter_change_types=filter_change_types,
            filter_section_path=filter_section_path,
            **valid_kwargs,
        )
    elif output_format == "text":
        text_formatter = TextFormatter()
        # Get valid parameters for TextFormatter.format()
        sig = inspect.signature(text_formatter.format)
        valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return text_formatter.format(
            diff,
            filter_change_types=filter_change_types,
            filter_section_path=filter_section_path,
            **valid_kwargs,
        )
    elif output_format == "yaml":
        yaml_formatter = YamlFormatter()
        # Get valid parameters for YamlFormatter.format()
        sig = inspect.signature(yaml_formatter.format)
        valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return yaml_formatter.format(
            diff,
            filter_change_types=filter_change_types,
            filter_section_path=filter_section_path,
            **valid_kwargs,
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
