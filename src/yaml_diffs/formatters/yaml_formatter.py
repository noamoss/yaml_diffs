"""YAML formatter for structured diff output."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import yaml  # type: ignore[import-untyped]

from yaml_diffs.diff_types import ChangeType, DocumentDiff
from yaml_diffs.formatters._filters import (
    calculate_summary_counts,
    diff_result_to_dict,
    filter_by_change_type,
    filter_by_section_path,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


class YamlFormatter:
    """Formatter for outputting diff results as YAML.

    Provides structured YAML output with support for filtering
    by change type and section path.
    """

    @staticmethod
    def format(
        diff: DocumentDiff,
        filter_change_types: Sequence[ChangeType] | None = None,
        filter_section_path: str | None = None,
        default_flow_style: bool = False,
        allow_unicode: bool = True,
    ) -> str:
        """Format diff as YAML string.

        Args:
            diff: DocumentDiff to format
            filter_change_types: Optional list of change types to include
            filter_section_path: Optional marker path to filter by (exact match)
            default_flow_style: Use flow style for collections (default: False)
            allow_unicode: Allow Unicode characters in output (default: True)

        Returns:
            YAML string representation of the diff

        Examples:
            >>> formatter = YamlFormatter()
            >>> yaml_str = formatter.format(diff)
            >>> yaml.safe_load(yaml_str)  # Valid YAML
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

        # Serialize to YAML
        return cast(
            str,
            yaml.dump(
                output,
                default_flow_style=default_flow_style,
                allow_unicode=allow_unicode,
                sort_keys=False,
            ),
        )
