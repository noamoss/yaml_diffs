"""JSON formatter for diff output."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional

from yaml_diffs.diff_types import ChangeType, DocumentDiff
from yaml_diffs.formatters._filters import (
    calculate_summary_counts,
    diff_result_to_dict,
    filter_by_change_type,
    filter_by_section_path,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


class JsonFormatter:
    """Formatter for outputting diff results as JSON.

    Provides machine-readable JSON output with support for filtering
    by change type and section path.
    """

    @staticmethod
    def format(
        diff: DocumentDiff,
        filter_change_types: Optional[Sequence[ChangeType]] = None,
        filter_section_path: Optional[str] = None,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> str:
        """Format diff as JSON string.

        Args:
            diff: DocumentDiff to format
            filter_change_types: Optional list of change types to include
            filter_section_path: Optional marker path to filter by (exact match)
            indent: JSON indentation level (default: 2)
            ensure_ascii: If False, output non-ASCII characters as-is (default: False)

        Returns:
            JSON string representation of the diff

        Examples:
            >>> formatter = JsonFormatter()
            >>> json_str = formatter.format(diff)
            >>> json.loads(json_str)  # Valid JSON
        """
        # Apply filters
        changes = diff.changes
        if filter_change_types is not None:
            changes = filter_by_change_type(changes, filter_change_types)
        if filter_section_path is not None:
            changes = filter_by_section_path(changes, filter_section_path)

        # Recalculate summary counts from filtered changes
        summary = calculate_summary_counts(changes)

        # Build output structure
        output = {
            "summary": summary,
            "changes": [diff_result_to_dict(change) for change in changes],
        }

        # Serialize to JSON
        return json.dumps(output, indent=indent, ensure_ascii=ensure_ascii)
