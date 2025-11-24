"""Tests for diff output formatters."""

from __future__ import annotations

import json

import pytest
import yaml

from yaml_diffs.diff import diff_documents
from yaml_diffs.diff_types import ChangeType, DiffResult, DocumentDiff
from yaml_diffs.formatters import (
    JsonFormatter,
    TextFormatter,
    YamlFormatter,
    filter_by_change_type,
    filter_by_section_path,
    format_diff,
    format_marker_path,
)
from yaml_diffs.loader import load_document


class TestFormatMarkerPath:
    """Tests for format_marker_path utility."""

    def test_format_marker_path_with_path(self):
        """Test formatting a marker path tuple."""
        path = ("פרק א'", "1", "(א)")
        result = format_marker_path(path)
        assert result == "פרק א' -> 1 -> (א)"

    def test_format_marker_path_none(self):
        """Test formatting None marker path."""
        result = format_marker_path(None)
        assert result == ""

    def test_format_marker_path_empty(self):
        """Test formatting empty marker path."""
        result = format_marker_path(())
        assert result == ""

    def test_format_marker_path_single(self):
        """Test formatting single marker."""
        result = format_marker_path(("1",))
        assert result == "1"


class TestFilterByChangeType:
    """Tests for filter_by_change_type utility."""

    def test_filter_by_change_type_no_filter(self):
        """Test filtering with None (no filter)."""
        changes = [
            DiffResult(
                section_id="1",
                change_type=ChangeType.SECTION_ADDED,
                marker="1",
            ),
            DiffResult(
                section_id="2",
                change_type=ChangeType.CONTENT_CHANGED,
                marker="2",
            ),
        ]
        result = filter_by_change_type(changes, None)
        assert len(result) == 2

    def test_filter_by_change_type_single_type(self):
        """Test filtering by single change type."""
        changes = [
            DiffResult(
                section_id="1",
                change_type=ChangeType.SECTION_ADDED,
                marker="1",
            ),
            DiffResult(
                section_id="2",
                change_type=ChangeType.CONTENT_CHANGED,
                marker="2",
            ),
        ]
        result = filter_by_change_type(changes, [ChangeType.SECTION_ADDED])
        assert len(result) == 1
        assert result[0].change_type == ChangeType.SECTION_ADDED

    def test_filter_by_change_type_multiple_types(self):
        """Test filtering by multiple change types."""
        changes = [
            DiffResult(
                section_id="1",
                change_type=ChangeType.SECTION_ADDED,
                marker="1",
            ),
            DiffResult(
                section_id="2",
                change_type=ChangeType.CONTENT_CHANGED,
                marker="2",
            ),
            DiffResult(
                section_id="3",
                change_type=ChangeType.SECTION_REMOVED,
                marker="3",
            ),
        ]
        result = filter_by_change_type(
            changes, [ChangeType.SECTION_ADDED, ChangeType.CONTENT_CHANGED]
        )
        assert len(result) == 2


class TestFilterBySectionPath:
    """Tests for filter_by_section_path utility."""

    def test_filter_by_section_path_no_filter(self):
        """Test filtering with None (no filter)."""
        changes = [
            DiffResult(
                section_id="1",
                change_type=ChangeType.CONTENT_CHANGED,
                marker="1",
                old_marker_path=("פרק א'", "1"),
            ),
        ]
        result = filter_by_section_path(changes, None)
        assert len(result) == 1

    def test_filter_by_section_path_match_old(self):
        """Test filtering by old marker path."""
        changes = [
            DiffResult(
                section_id="1",
                change_type=ChangeType.CONTENT_CHANGED,
                marker="1",
                old_marker_path=("פרק א'", "1"),
            ),
            DiffResult(
                section_id="2",
                change_type=ChangeType.CONTENT_CHANGED,
                marker="2",
                old_marker_path=("פרק ב'", "1"),
            ),
        ]
        result = filter_by_section_path(changes, "פרק א' -> 1")
        assert len(result) == 1
        assert result[0].section_id == "1"

    def test_filter_by_section_path_match_new(self):
        """Test filtering by new marker path."""
        changes = [
            DiffResult(
                section_id="1",
                change_type=ChangeType.SECTION_ADDED,
                marker="1",
                new_marker_path=("פרק א'", "1"),
            ),
        ]
        result = filter_by_section_path(changes, "פרק א' -> 1")
        assert len(result) == 1


class TestJsonFormatter:
    """Tests for JSON formatter."""

    def test_format_json_valid(self):
        """Test that JSON output is valid JSON."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                    old_marker_path=("פרק א'", "1"),
                    new_marker_path=("פרק א'", "1"),
                    old_content="Old content",
                    new_content="New content",
                ),
            ],
            added_count=0,
            deleted_count=0,
            modified_count=1,
            moved_count=0,
        )
        formatter = JsonFormatter()
        output = formatter.format(diff)
        # Should be valid JSON
        parsed = json.loads(output)
        assert isinstance(parsed, dict)
        assert "summary" in parsed
        assert "changes" in parsed

    def test_format_json_parseable(self):
        """Test that JSON output can be parsed back."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.SECTION_ADDED,
                    marker="1",
                    new_marker_path=("פרק א'", "1"),
                    new_content="Content",
                ),
            ],
            added_count=1,
            deleted_count=0,
            modified_count=0,
            moved_count=0,
        )
        formatter = JsonFormatter()
        output = formatter.format(diff)
        parsed = json.loads(output)
        assert parsed["summary"]["added_count"] == 1
        assert len(parsed["changes"]) == 1
        assert parsed["changes"][0]["change_type"] == "section_added"

    def test_format_json_includes_paths(self):
        """Test that JSON includes both marker and ID paths."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="sec-1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                    old_marker_path=("פרק א'", "1"),
                    new_marker_path=("פרק א'", "1"),
                    old_id_path=["chap-1", "sec-1"],
                    new_id_path=["chap-1", "sec-1"],
                ),
            ],
        )
        formatter = JsonFormatter()
        output = formatter.format(diff)
        parsed = json.loads(output)
        change = parsed["changes"][0]
        assert change["old_marker_path"] == ["פרק א'", "1"]
        assert change["new_marker_path"] == ["פרק א'", "1"]
        assert change["old_id_path"] == ["chap-1", "sec-1"]
        assert change["new_id_path"] == ["chap-1", "sec-1"]

    def test_format_json_filter_by_change_type(self):
        """Test filtering by change type."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.SECTION_ADDED,
                    marker="1",
                ),
                DiffResult(
                    section_id="2",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="2",
                ),
            ],
        )
        formatter = JsonFormatter()
        output = formatter.format(diff, filter_change_types=[ChangeType.SECTION_ADDED])
        parsed = json.loads(output)
        assert len(parsed["changes"]) == 1
        assert parsed["changes"][0]["change_type"] == "section_added"

    def test_format_json_filter_by_section_path(self):
        """Test filtering by section path."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                    old_marker_path=("פרק א'", "1"),
                ),
                DiffResult(
                    section_id="2",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="2",
                    old_marker_path=("פרק ב'", "1"),
                ),
            ],
        )
        formatter = JsonFormatter()
        output = formatter.format(diff, filter_section_path="פרק א' -> 1")
        parsed = json.loads(output)
        assert len(parsed["changes"]) == 1
        assert parsed["changes"][0]["section_id"] == "1"

    def test_format_json_empty_diff(self):
        """Test formatting empty diff."""
        diff = DocumentDiff()
        formatter = JsonFormatter()
        output = formatter.format(diff)
        parsed = json.loads(output)
        assert parsed["summary"]["added_count"] == 0
        assert len(parsed["changes"]) == 0


class TestTextFormatter:
    """Tests for text formatter."""

    def test_format_text_shows_context(self):
        """Test that text output shows context."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                    old_marker_path=("פרק א'", "1"),
                    new_marker_path=("פרק א'", "1"),
                    old_content="Old content",
                    new_content="New content",
                ),
            ],
            modified_count=1,
        )
        formatter = TextFormatter()
        output = formatter.format(diff, show_context=True)
        assert "Old content" in output
        assert "New content" in output
        assert "Old content:" in output
        assert "New content:" in output

    def test_format_text_marker_paths(self):
        """Test that marker paths are shown prominently."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                    old_marker_path=("פרק א'", "1", "(א)"),
                    new_marker_path=("פרק א'", "1", "(א)"),
                ),
            ],
        )
        formatter = TextFormatter()
        output = formatter.format(diff)
        assert "פרק א' -> 1 -> (א)" in output

    def test_format_text_before_after(self):
        """Test that before/after are clearly separated."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                    old_content="Before",
                    new_content="After",
                ),
            ],
        )
        formatter = TextFormatter()
        output = formatter.format(diff)
        assert "Old content:" in output
        assert "New content:" in output

    def test_format_text_filter_by_change_type(self):
        """Test filtering by change type."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.SECTION_ADDED,
                    marker="1",
                ),
                DiffResult(
                    section_id="2",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="2",
                ),
            ],
        )
        formatter = TextFormatter()
        output = formatter.format(diff, filter_change_types=[ChangeType.SECTION_ADDED])
        assert "SECTION ADDED" in output
        assert "CONTENT CHANGED" not in output

    def test_format_text_filter_by_section_path(self):
        """Test filtering by section path."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                    old_marker_path=("פרק א'", "1"),
                ),
            ],
        )
        formatter = TextFormatter()
        output = formatter.format(diff, filter_section_path="פרק א' -> 1")
        assert "פרק א' -> 1" in output

    def test_format_text_hebrew_content(self):
        """Test that Hebrew content displays correctly."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                    old_content="תוכן ישן",
                    new_content="תוכן חדש",
                ),
            ],
        )
        formatter = TextFormatter()
        output = formatter.format(diff)
        assert "תוכן ישן" in output
        assert "תוכן חדש" in output


class TestYamlFormatter:
    """Tests for YAML formatter."""

    def test_format_yaml_structure(self):
        """Test that YAML output has correct structure."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                    old_marker_path=("פרק א'", "1"),
                    new_marker_path=("פרק א'", "1"),
                ),
            ],
            modified_count=1,
        )
        formatter = YamlFormatter()
        output = formatter.format(diff)
        parsed = yaml.safe_load(output)
        assert isinstance(parsed, dict)
        assert "summary" in parsed
        assert "changes" in parsed

    def test_format_yaml_parseable(self):
        """Test that YAML output can be parsed back."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.SECTION_ADDED,
                    marker="1",
                    new_marker_path=("פרק א'", "1"),
                ),
            ],
            added_count=1,
        )
        formatter = YamlFormatter()
        output = formatter.format(diff)
        parsed = yaml.safe_load(output)
        assert parsed["summary"]["added_count"] == 1
        assert len(parsed["changes"]) == 1

    def test_format_yaml_includes_paths(self):
        """Test that YAML includes both marker and ID paths."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="sec-1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                    old_marker_path=("פרק א'", "1"),
                    new_marker_path=("פרק א'", "1"),
                    old_id_path=["chap-1", "sec-1"],
                    new_id_path=["chap-1", "sec-1"],
                ),
            ],
        )
        formatter = YamlFormatter()
        output = formatter.format(diff)
        parsed = yaml.safe_load(output)
        change = parsed["changes"][0]
        assert change["old_marker_path"] == ["פרק א'", "1"]
        assert change["new_marker_path"] == ["פרק א'", "1"]
        assert change["old_id_path"] == ["chap-1", "sec-1"]
        assert change["new_id_path"] == ["chap-1", "sec-1"]

    def test_format_yaml_filter_by_change_type(self):
        """Test filtering by change type."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.SECTION_ADDED,
                    marker="1",
                ),
                DiffResult(
                    section_id="2",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="2",
                ),
            ],
        )
        formatter = YamlFormatter()
        output = formatter.format(diff, filter_change_types=[ChangeType.SECTION_ADDED])
        parsed = yaml.safe_load(output)
        assert len(parsed["changes"]) == 1
        assert parsed["changes"][0]["change_type"] == "section_added"

    def test_format_yaml_filter_by_section_path(self):
        """Test filtering by section path."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                    old_marker_path=("פרק א'", "1"),
                ),
            ],
        )
        formatter = YamlFormatter()
        output = formatter.format(diff, filter_section_path="פרק א' -> 1")
        parsed = yaml.safe_load(output)
        assert len(parsed["changes"]) == 1


class TestFormatDiffConvenience:
    """Tests for format_diff convenience function."""

    def test_format_diff_json(self):
        """Test format_diff with json format."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                ),
            ],
        )
        output = format_diff(diff, output_format="json")
        parsed = json.loads(output)
        assert "summary" in parsed

    def test_format_diff_text(self):
        """Test format_diff with text format."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                ),
            ],
        )
        output = format_diff(diff, output_format="text")
        assert "Document Diff Summary" in output

    def test_format_diff_yaml(self):
        """Test format_diff with yaml format."""
        diff = DocumentDiff(
            changes=[
                DiffResult(
                    section_id="1",
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker="1",
                ),
            ],
        )
        output = format_diff(diff, output_format="yaml")
        parsed = yaml.safe_load(output)
        assert "summary" in parsed

    def test_format_diff_invalid_format(self):
        """Test format_diff with invalid format raises error."""
        diff = DocumentDiff()
        with pytest.raises(ValueError, match="Unknown format"):
            format_diff(diff, output_format="invalid")


class TestFormatterIntegration:
    """Integration tests with example documents."""

    def test_format_example_diff_json(self):
        """Test formatting example document diff as JSON."""
        old_doc = load_document("examples/document_v1.yaml")
        new_doc = load_document("examples/document_v2.yaml")
        diff = diff_documents(old_doc, new_doc)

        formatter = JsonFormatter()
        output = formatter.format(diff)
        parsed = json.loads(output)

        assert "summary" in parsed
        assert "changes" in parsed
        assert isinstance(parsed["summary"]["added_count"], int)
        assert isinstance(parsed["changes"], list)

    def test_format_example_diff_text(self):
        """Test formatting example document diff as text."""
        old_doc = load_document("examples/document_v1.yaml")
        new_doc = load_document("examples/document_v2.yaml")
        diff = diff_documents(old_doc, new_doc)

        formatter = TextFormatter()
        output = formatter.format(diff)

        assert "Document Diff Summary" in output
        assert "Changes:" in output

    def test_format_example_diff_yaml(self):
        """Test formatting example document diff as YAML."""
        old_doc = load_document("examples/document_v1.yaml")
        new_doc = load_document("examples/document_v2.yaml")
        diff = diff_documents(old_doc, new_doc)

        formatter = YamlFormatter()
        output = formatter.format(diff)
        parsed = yaml.safe_load(output)

        assert "summary" in parsed
        assert "changes" in parsed

    def test_format_diff_all_change_types(self):
        """Test that all change types are represented in output."""
        old_doc = load_document("examples/document_v1.yaml")
        new_doc = load_document("examples/document_v2.yaml")
        diff = diff_documents(old_doc, new_doc)

        # Get all change types present
        change_types = {change.change_type for change in diff.changes}

        # Format as JSON and verify all types are present
        formatter = JsonFormatter()
        output = formatter.format(diff)
        parsed = json.loads(output)

        output_change_types = {ChangeType(change["change_type"]) for change in parsed["changes"]}
        assert output_change_types == change_types
