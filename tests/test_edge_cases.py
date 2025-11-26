"""Comprehensive edge case tests for yaml-diffs.

Tests for handling edge cases including empty documents, malformed YAML,
invalid encoding, missing fields, duplicate markers, and other boundary conditions.
"""

from io import StringIO
from pathlib import Path

import pytest

from yaml_diffs.api import diff_documents, load_and_validate, load_document
from yaml_diffs.diff import _validate_unique_markers
from yaml_diffs.exceptions import (
    OpenSpecValidationError,
    PydanticValidationError,
    ValidationError,
    YAMLLoadError,
)
from yaml_diffs.loader import load_yaml, load_yaml_file
from yaml_diffs.models import Document, DocumentType, Section, Source, Version


class TestEmptyDocuments:
    """Test handling of empty documents."""

    def test_empty_yaml_file(self, tmp_path: Path):
        """Test loading an empty YAML file."""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("", encoding="utf-8")

        with pytest.raises((YAMLLoadError, ValidationError)):
            load_and_validate(empty_file)

    def test_yaml_with_only_whitespace(self, tmp_path: Path):
        """Test loading YAML file with only whitespace."""
        whitespace_file = tmp_path / "whitespace.yaml"
        whitespace_file.write_text("   \n\n  \t  \n", encoding="utf-8")

        with pytest.raises((YAMLLoadError, ValidationError)):
            load_and_validate(whitespace_file)

    def test_document_with_empty_sections(self):
        """Test document with empty sections list."""
        doc = Document(
            id="empty-sections",
            title="מסמך ריק",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com", fetched_at="2025-01-20T09:50:00Z"),
            sections=[],
        )

        assert doc.sections == []
        assert len(doc.sections) == 0

    def test_section_with_empty_content(self):
        """Test section with empty content string."""
        section = Section(id="sec-1", marker="1", content="")
        assert section.content == ""
        assert section.marker == "1"


class TestMalformedYAML:
    """Test handling of malformed YAML."""

    def test_invalid_yaml_syntax(self, tmp_path: Path):
        """Test loading file with invalid YAML syntax."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("document:\n  id: [invalid: syntax\n", encoding="utf-8")

        with pytest.raises(YAMLLoadError) as exc_info:
            load_yaml_file(invalid_file)

        assert "yaml" in str(exc_info.value).lower() or "syntax" in str(exc_info.value).lower()

    def test_unclosed_brackets(self, tmp_path: Path):
        """Test YAML with unclosed brackets."""
        invalid_file = tmp_path / "unclosed.yaml"
        invalid_file.write_text("document:\n  sections: [\n    { id: '1'\n", encoding="utf-8")

        with pytest.raises(YAMLLoadError):
            load_yaml_file(invalid_file)

    def test_wrong_structure(self, tmp_path: Path):
        """Test YAML with wrong document structure."""
        wrong_structure_file = tmp_path / "wrong.yaml"
        wrong_structure_file.write_text("not_document:\n  something: else\n", encoding="utf-8")

        with pytest.raises((OpenSpecValidationError, PydanticValidationError)):
            load_and_validate(wrong_structure_file)

    def test_yaml_with_tabs_in_indentation(self, tmp_path: Path):
        """Test YAML with tabs instead of spaces (should fail - YAML spec doesn't allow tabs)."""
        tab_file = tmp_path / "tabs.yaml"
        tab_file.write_text("document:\n\tid: 'test'\n\ttitle: 'Test'", encoding="utf-8")

        # YAML parser doesn't allow tabs for indentation - should raise YAMLLoadError
        with pytest.raises(YAMLLoadError):
            load_and_validate(tab_file)


class TestInvalidEncoding:
    """Test handling of invalid encoding."""

    def test_invalid_utf8_bytes(self, tmp_path: Path):
        """Test file with invalid UTF-8 bytes."""
        invalid_file = tmp_path / "invalid_utf8.yaml"
        # Write invalid UTF-8 bytes
        invalid_file.write_bytes(b"document:\n  title: \xff\xfe\xfd\n")

        with pytest.raises((YAMLLoadError, UnicodeDecodeError)):
            load_yaml_file(invalid_file)

    def test_mixed_encoding(self, tmp_path: Path):
        """Test file with mixed encoding issues."""
        mixed_file = tmp_path / "mixed.yaml"
        try:
            # Try to write with latin-1 encoding (should fail for Hebrew)
            mixed_file.write_text("document:\n  title: hébreu\n", encoding="latin-1")
            # This might load but validation will fail
            with pytest.raises((ValidationError, YAMLLoadError)):
                load_and_validate(mixed_file)
        except UnicodeEncodeError:
            # If we can't even write it, that's fine
            pass


class TestMissingRequiredFields:
    """Test handling of missing required fields."""

    def test_missing_document_id(self, tmp_path: Path):
        """Test document missing required id field."""
        missing_id_file = tmp_path / "no_id.yaml"
        missing_id_file.write_text(
            """document:
  title: "חוק"
  type: "law"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
""",
            encoding="utf-8",
        )

        with pytest.raises((OpenSpecValidationError, PydanticValidationError)):
            load_and_validate(missing_id_file)

    def test_missing_section_marker(self, tmp_path: Path):
        """Test section missing required marker field."""
        missing_marker_file = tmp_path / "no_marker.yaml"
        missing_marker_file.write_text(
            """document:
  id: "test"
  title: "חוק"
  type: "law"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      title: "סעיף"
""",
            encoding="utf-8",
        )

        with pytest.raises((OpenSpecValidationError, PydanticValidationError)):
            load_and_validate(missing_marker_file)

    def test_missing_section_id(self, tmp_path: Path):
        """Test section missing required id field."""
        missing_id_file = tmp_path / "no_section_id.yaml"
        missing_id_file.write_text(
            """document:
  id: "test"
  title: "חוק"
  type: "law"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - marker: "1"
      title: "סעיף"
""",
            encoding="utf-8",
        )

        with pytest.raises((OpenSpecValidationError, PydanticValidationError)):
            load_and_validate(missing_id_file)

    def test_missing_version(self, tmp_path: Path):
        """Test document missing required version field."""
        missing_version_file = tmp_path / "no_version.yaml"
        missing_version_file.write_text(
            """document:
  id: "test"
  title: "חוק"
  type: "law"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
""",
            encoding="utf-8",
        )

        with pytest.raises((OpenSpecValidationError, PydanticValidationError)):
            load_and_validate(missing_version_file)

    def test_missing_source(self, tmp_path: Path):
        """Test document missing required source field."""
        missing_source_file = tmp_path / "no_source.yaml"
        missing_source_file.write_text(
            """document:
  id: "test"
  title: "חוק"
  type: "law"
  version:
    number: "1.0"
""",
            encoding="utf-8",
        )

        with pytest.raises((OpenSpecValidationError, PydanticValidationError)):
            load_and_validate(missing_source_file)


class TestDuplicateMarkers:
    """Test handling of duplicate markers."""

    def test_duplicate_markers_same_level(self):
        """Test duplicate markers at the same nesting level."""
        section1 = Section(id="sec-1", marker="1", content="First")
        section2 = Section(id="sec-2", marker="1", content="Second")  # Duplicate marker!

        with pytest.raises(ValueError) as exc_info:
            _validate_unique_markers([section1, section2])

        assert "Duplicate marker" in str(exc_info.value)
        assert "1" in str(exc_info.value)

    def test_duplicate_markers_nested(self):
        """Test duplicate markers in nested sections."""
        child1 = Section(id="child-1", marker="א", content="Child 1")
        child2 = Section(id="child-2", marker="א", content="Child 2")  # Duplicate!
        parent = Section(id="parent", marker="1", content="Parent", sections=[child1, child2])

        with pytest.raises(ValueError) as exc_info:
            _validate_unique_markers([parent])

        assert "Duplicate marker" in str(exc_info.value)

    def test_duplicate_markers_different_levels_allowed(self):
        """Test that duplicate markers at different levels are allowed."""
        child = Section(id="child", marker="1", content="Child")
        parent = Section(id="parent", marker="1", content="Parent", sections=[child])

        # Should not raise - different nesting levels
        _validate_unique_markers([parent])


class TestInvalidUUIDs:
    """Test handling of invalid UUID formats."""

    def test_invalid_uuid_format_in_section_id(self, tmp_path: Path):
        """Test section with invalid UUID format (should work - IDs are just strings)."""
        invalid_uuid_file = tmp_path / "invalid_uuid.yaml"
        invalid_uuid_file.write_text(
            """document:
  id: "test"
  title: "חוק"
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "not-a-valid-uuid-format"
      marker: "1"
      sections: []
""",
            encoding="utf-8",
        )

        # UUID validation is lenient - should still load
        # The id field accepts any string, not just UUIDs
        doc = load_and_validate(invalid_uuid_file)
        assert doc.sections[0].id == "not-a-valid-uuid-format"

    def test_empty_string_id(self, tmp_path: Path):
        """Test section with empty string ID."""
        empty_id_file = tmp_path / "empty_id.yaml"
        empty_id_file.write_text(
            """document:
  id: ""
  title: "חוק"
  type: "law"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
""",
            encoding="utf-8",
        )

        # Empty string might be invalid depending on schema
        with pytest.raises((OpenSpecValidationError, PydanticValidationError)):
            load_and_validate(empty_id_file)


class TestExtremelyLongStrings:
    """Test handling of extremely long strings."""

    def test_extremely_long_content(self, tmp_path: Path):
        """Test section with extremely long content (10K+ characters)."""
        long_content = "א" * 10000  # 10K Hebrew characters

        long_content_file = tmp_path / "long_content.yaml"
        long_content_file.write_text(
            f"""document:
  id: "test"
  title: "חוק"
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: "1"
      content: "{long_content}"
      sections: []
""",
            encoding="utf-8",
        )

        doc = load_and_validate(long_content_file)
        assert len(doc.sections[0].content) == 10000

    def test_extremely_long_title(self, tmp_path: Path):
        """Test document with extremely long title."""
        long_title = "א" * 5000  # 5K characters

        long_title_file = tmp_path / "long_title.yaml"
        long_title_file.write_text(
            f"""document:
  id: "test"
  title: "{long_title}"
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections: []
""",
            encoding="utf-8",
        )

        doc = load_and_validate(long_title_file)
        assert len(doc.title) == 5000

    def test_extremely_long_marker(self, tmp_path: Path):
        """Test section with extremely long marker."""
        long_marker = "א" * 1000  # 1K characters

        long_marker_file = tmp_path / "long_marker.yaml"
        long_marker_file.write_text(
            f"""document:
  id: "test"
  title: "חוק"
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: "{long_marker}"
      sections: []
""",
            encoding="utf-8",
        )

        doc = load_and_validate(long_marker_file)
        assert len(doc.sections[0].marker) == 1000


class TestSpecialCharacters:
    """Test handling of special characters."""

    def test_unicode_in_marker(self, tmp_path: Path):
        """Test section with unicode characters in marker."""
        unicode_marker_file = tmp_path / "unicode_marker.yaml"
        unicode_marker_file.write_text(
            """document:
  id: "test"
  title: "חוק"
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: "א'"
      title: "סעיף עם ניקוד"
      sections: []
""",
            encoding="utf-8",
        )

        doc = load_and_validate(unicode_marker_file)
        assert doc.sections[0].marker == "א'"

    def test_emoji_in_content(self, tmp_path: Path):
        """Test section with emoji in content."""
        emoji_file = tmp_path / "emoji.yaml"
        emoji_file.write_text(
            """document:
  id: "test"
  title: "חוק"
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: "1"
      content: "תוכן עם אימוג'י 😀 🎉"
      sections: []
""",
            encoding="utf-8",
        )

        doc = load_and_validate(emoji_file)
        assert "😀" in doc.sections[0].content
        assert "🎉" in doc.sections[0].content

    def test_special_characters_in_url(self, tmp_path: Path):
        """Test source URL with special characters."""
        special_url_file = tmp_path / "special_url.yaml"
        special_url_file.write_text(
            """document:
  id: "test"
  title: "חוק"
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com/path?query=value&other=test"
    fetched_at: "2025-01-20T09:50:00Z"
  sections: []
""",
            encoding="utf-8",
        )

        doc = load_and_validate(special_url_file)
        assert "?" in doc.source.url
        assert "&" in doc.source.url


class TestNullAndNoneValues:
    """Test handling of null/None values."""

    def test_null_in_optional_field(self, tmp_path: Path):
        """Test null value in optional field (title) - schema may not allow null."""
        null_title_file = tmp_path / "null_title.yaml"
        null_title_file.write_text(
            """document:
  id: "test"
  title: null
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections: []
""",
            encoding="utf-8",
        )

        # Title is optional in Pydantic, but schema validation may reject null
        # If schema allows null, it should work; otherwise it should raise an error
        try:
            doc = load_and_validate(null_title_file)
            # If it works, title should be None
            assert doc.title is None
        except OpenSpecValidationError:
            # If schema doesn't allow null, that's also valid behavior
            pass

    def test_null_in_required_field(self, tmp_path: Path):
        """Test null value in required field (should fail)."""
        null_id_file = tmp_path / "null_id.yaml"
        null_id_file.write_text(
            """document:
  id: null
  title: "חוק"
  type: "law"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
""",
            encoding="utf-8",
        )

        with pytest.raises((OpenSpecValidationError, PydanticValidationError)):
            load_and_validate(null_id_file)


class TestTypeMismatches:
    """Test handling of type mismatches."""

    def test_string_where_int_expected(self, tmp_path: Path):
        """Test string value where integer might be expected."""
        # Version number is a string, so this should work
        string_version_file = tmp_path / "string_version.yaml"
        string_version_file.write_text(
            """document:
  id: "test"
  title: "חוק"
  type: "law"
  language: "hebrew"
  version:
    number: "2024-01-01"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections: []
""",
            encoding="utf-8",
        )

        # Should work - version number is a string
        doc = load_and_validate(string_version_file)
        assert isinstance(doc.version.number, str)

    def test_list_where_string_expected(self, tmp_path: Path):
        """Test list value where string is expected."""
        list_id_file = tmp_path / "list_id.yaml"
        list_id_file.write_text(
            """document:
  id: ["not", "a", "string"]
  title: "חוק"
  type: "law"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
""",
            encoding="utf-8",
        )

        with pytest.raises((OpenSpecValidationError, PydanticValidationError)):
            load_and_validate(list_id_file)

    def test_dict_where_string_expected(self, tmp_path: Path):
        """Test dict value where string is expected."""
        dict_marker_file = tmp_path / "dict_marker.yaml"
        dict_marker_file.write_text(
            """document:
  id: "test"
  title: "חוק"
  type: "law"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: {not: "a string"}
""",
            encoding="utf-8",
        )

        with pytest.raises((OpenSpecValidationError, PydanticValidationError)):
            load_and_validate(dict_marker_file)


class TestEdgeCaseDiffing:
    """Test edge cases in diffing operations."""

    def test_diff_empty_documents(self):
        """Test diffing two empty documents."""
        doc1 = Document(
            id="doc-1",
            title="מסמך 1",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com", fetched_at="2025-01-20T09:50:00Z"),
            sections=[],
        )

        doc2 = Document(
            id="doc-2",
            title="מסמך 2",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com", fetched_at="2025-01-20T09:50:00Z"),
            sections=[],
        )

        diff = diff_documents(doc1, doc2)
        assert diff is not None
        # Diff only compares sections, not document-level metadata
        # Empty documents with no sections will have no changes
        assert isinstance(diff.changes, list)
        assert diff.added_count == 0
        assert diff.deleted_count == 0

    def test_diff_identical_documents(self):
        """Test diffing identical documents."""
        doc = Document(
            id="doc-1",
            title="מסמך",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com", fetched_at="2025-01-20T09:50:00Z"),
            sections=[],
        )

        diff = diff_documents(doc, doc)
        assert diff is not None
        # Should show no changes or only UNCHANGED
        assert diff.added_count == 0
        assert diff.deleted_count == 0
        assert diff.modified_count == 0
        assert diff.moved_count == 0

    def test_diff_with_duplicate_markers_in_one_doc(self):
        """Test diffing when one document has duplicate markers."""
        # This should fail validation before diffing
        section1 = Section(id="sec-1", marker="1", content="First")
        section2 = Section(id="sec-2", marker="1", content="Second")

        doc = Document(
            id="doc-1",
            title="מסמך",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com", fetched_at="2025-01-20T09:50:00Z"),
            sections=[section1, section2],
        )

        # Should raise ValueError when validating markers
        with pytest.raises(ValueError):
            diff_documents(doc, doc)


class TestEdgeCaseLoading:
    """Test edge cases in loading operations."""

    def test_load_yaml_from_string_io(self):
        """Test loading YAML from StringIO object."""
        yaml_content = """document:
  id: "test"
  title: "חוק"
  type: "law"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
"""
        file_like = StringIO(yaml_content)
        data = load_yaml(file_like)
        assert isinstance(data, dict)
        assert data["document"]["id"] == "test"

    def test_load_yaml_from_string(self):
        """Test loading YAML from string directly."""
        yaml_content = """document:
  id: "test"
  title: "חוק"
  type: "law"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
"""
        data = load_yaml(yaml_content)
        assert isinstance(data, dict)
        assert data["document"]["id"] == "test"

    def test_load_nonexistent_file(self):
        """Test loading non-existent file."""
        with pytest.raises(YAMLLoadError) as exc_info:
            load_document("nonexistent_file_12345.yaml")

        assert (
            "not found" in str(exc_info.value).lower()
            or "does not exist" in str(exc_info.value).lower()
        )
