"""Tests for the main library API."""

from io import StringIO
from pathlib import Path

import pytest

# Try to import jsonschema, skip tests if not available
try:
    from jsonschema import FormatChecker  # noqa: F401
    from jsonschema.validators import Draft202012Validator  # noqa: F401
except ImportError:
    pytestmark = pytest.mark.skip("jsonschema library not available")

from yaml_diffs.api import (
    ChangeType,
    Document,
    DocumentDiff,
    OpenSpecValidationError,
    PydanticValidationError,
    YAMLLoadError,
    diff_and_format,
    diff_documents,
    diff_files,
    format_diff,
    load_and_validate,
    load_document,
    validate_document,
)
from yaml_diffs.models import DocumentType, Section, Source, Version


# Test fixtures
@pytest.fixture
def minimal_yaml_content() -> str:
    """Minimal valid YAML document content."""
    return """document:
  id: "test-123"
  title: "חוק בדיקה"
  type: "law"
  language: "hebrew"
  version:
    number: "2024-01-01"
  source:
    url: "https://example.com/test"
    fetched_at: "2025-01-20T09:50:00Z"
  sections: []
"""


@pytest.fixture
def minimal_yaml_file(tmp_path: Path, minimal_yaml_content: str) -> Path:
    """Create a temporary YAML file with minimal content."""
    file_path = tmp_path / "minimal.yaml"
    file_path.write_text(minimal_yaml_content, encoding="utf-8")
    return file_path


@pytest.fixture
def document_v1_content() -> str:
    """Content for document version 1."""
    return """document:
  id: "law-1234"
  title: "חוק הדוגמה"
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com/law"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: "1"
      title: "סעיף ראשון"
      content: "תוכן הסעיף הראשון"
      sections: []
    - id: "sec-2"
      marker: "2"
      title: "סעיף שני"
      content: "תוכן הסעיף השני"
      sections: []
"""


@pytest.fixture
def document_v2_content() -> str:
    """Content for document version 2 (modified version 1)."""
    return """document:
  id: "law-1234"
  title: "חוק הדוגמה"
  type: "law"
  language: "hebrew"
  version:
    number: "2.0"
  source:
    url: "https://example.com/law"
    fetched_at: "2025-01-21T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: "1"
      title: "סעיף ראשון"
      content: "תוכן הסעיף הראשון - עודכן"
      sections: []
    - id: "sec-2"
      marker: "2"
      title: "סעיף שני"
      content: "תוכן הסעיף השני"
      sections: []
    - id: "sec-3"
      marker: "3"
      title: "סעיף שלישי"
      content: "תוכן הסעיף השלישי החדש"
      sections: []
"""


@pytest.fixture
def document_v1_file(tmp_path: Path, document_v1_content: str) -> Path:
    """Create a temporary YAML file with document v1 content."""
    file_path = tmp_path / "document_v1.yaml"
    file_path.write_text(document_v1_content, encoding="utf-8")
    return file_path


@pytest.fixture
def document_v2_file(tmp_path: Path, document_v2_content: str) -> Path:
    """Create a temporary YAML file with document v2 content."""
    file_path = tmp_path / "document_v2.yaml"
    file_path.write_text(document_v2_content, encoding="utf-8")
    return file_path


@pytest.fixture
def invalid_yaml_content() -> str:
    """Invalid YAML content (missing required fields)."""
    return """document:
  id: "test-123"
  # Missing required fields
"""


@pytest.fixture
def invalid_yaml_file(tmp_path: Path, invalid_yaml_content: str) -> Path:
    """Create a temporary YAML file with invalid content."""
    file_path = tmp_path / "invalid.yaml"
    file_path.write_text(invalid_yaml_content, encoding="utf-8")
    return file_path


class TestLoadDocument:
    """Test load_document function."""

    def test_load_document_file_path(self, minimal_yaml_file: Path):
        """Test loading document from file path."""
        doc = load_document(minimal_yaml_file)
        assert isinstance(doc, Document)
        assert doc.id == "test-123"
        assert doc.title == "חוק בדיקה"

    def test_load_document_string_path(self, minimal_yaml_file: Path):
        """Test loading document from string path."""
        doc = load_document(str(minimal_yaml_file))
        assert isinstance(doc, Document)
        assert doc.id == "test-123"

    def test_load_document_file_like(self, minimal_yaml_content: str):
        """Test loading document from file-like object."""
        file_like = StringIO(minimal_yaml_content)
        doc = load_document(file_like)
        assert isinstance(doc, Document)
        assert doc.id == "test-123"

    def test_load_document_raises_yaml_load_error_file_not_found(self):
        """Test load_document raises YAMLLoadError for missing file."""
        with pytest.raises(YAMLLoadError) as exc_info:
            load_document("nonexistent.yaml")
        assert "not found" in str(exc_info.value).lower()

    def test_load_document_raises_pydantic_validation_error(self, invalid_yaml_file: Path):
        """Test load_document raises PydanticValidationError for invalid document."""
        with pytest.raises(PydanticValidationError):
            load_document(invalid_yaml_file)


class TestValidateDocument:
    """Test validate_document function."""

    def test_validate_document_file_path(self, minimal_yaml_file: Path):
        """Test validating document from file path."""
        doc = validate_document(minimal_yaml_file)
        assert isinstance(doc, Document)
        assert doc.id == "test-123"

    def test_validate_document_file_like(self, minimal_yaml_content: str):
        """Test validating document from file-like object."""
        file_like = StringIO(minimal_yaml_content)
        doc = validate_document(file_like)
        assert isinstance(doc, Document)
        assert doc.id == "test-123"

    def test_validate_document_raises_yaml_load_error(self):
        """Test validate_document raises YAMLLoadError for missing file."""
        with pytest.raises(YAMLLoadError):
            validate_document("nonexistent.yaml")

    def test_validate_document_raises_openspec_validation_error(self, tmp_path: Path):
        """Test validate_document raises OpenSpecValidationError for schema violation."""
        # Create a file with invalid schema (missing required fields)
        invalid_file = tmp_path / "invalid_schema.yaml"
        invalid_file.write_text(
            """document:
  id: "test"
  # Missing required fields: title, type, version, source
""",
            encoding="utf-8",
        )
        with pytest.raises(OpenSpecValidationError):
            validate_document(invalid_file)


class TestDiffDocuments:
    """Test diff_documents function."""

    def test_diff_documents(self, document_v1_file: Path, document_v2_file: Path):
        """Test diffing two documents."""
        old_doc = load_document(document_v1_file)
        new_doc = load_document(document_v2_file)
        diff = diff_documents(old_doc, new_doc)
        assert isinstance(diff, DocumentDiff)
        assert diff.added_count == 1  # Section 3 added
        assert diff.modified_count == 1  # Section 1 content changed

    def test_diff_documents_raises_value_error_duplicate_markers(self):
        """Test diff_documents raises ValueError for duplicate markers."""
        doc1 = Document(
            id="test-1",
            title="Test",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com", fetched_at="2025-01-20T09:50:00Z"),
            sections=[
                Section(id="sec-1", marker="1", content="Content 1"),
                Section(id="sec-2", marker="1", content="Content 2"),  # Duplicate marker
            ],
        )
        doc2 = Document(
            id="test-2",
            title="Test",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com", fetched_at="2025-01-20T09:50:00Z"),
            sections=[],
        )
        with pytest.raises(ValueError, match="Duplicate marker"):
            diff_documents(doc1, doc2)


class TestLoadAndValidate:
    """Test load_and_validate convenience function."""

    def test_load_and_validate_file_path(self, minimal_yaml_file: Path):
        """Test load_and_validate with file path."""
        doc = load_and_validate(minimal_yaml_file)
        assert isinstance(doc, Document)
        assert doc.id == "test-123"

    def test_load_and_validate_file_like(self, minimal_yaml_content: str):
        """Test load_and_validate with file-like object."""
        file_like = StringIO(minimal_yaml_content)
        doc = load_and_validate(file_like)
        assert isinstance(doc, Document)
        assert doc.id == "test-123"

    def test_load_and_validate_raises_errors(self, invalid_yaml_file: Path):
        """Test load_and_validate raises appropriate errors."""
        # Should raise OpenSpecValidationError (schema validation happens first)
        with pytest.raises(OpenSpecValidationError):
            load_and_validate(invalid_yaml_file)


class TestDiffFiles:
    """Test diff_files convenience function."""

    def test_diff_files(self, document_v1_file: Path, document_v2_file: Path):
        """Test diffing two files."""
        diff = diff_files(document_v1_file, document_v2_file)
        assert isinstance(diff, DocumentDiff)
        assert diff.added_count == 1
        assert diff.modified_count == 1

    def test_diff_files_string_paths(self, document_v1_file: Path, document_v2_file: Path):
        """Test diff_files with string paths."""
        diff = diff_files(str(document_v1_file), str(document_v2_file))
        assert isinstance(diff, DocumentDiff)

    def test_diff_files_file_like(self, document_v1_content: str, document_v2_content: str):
        """Test diff_files with file-like objects."""
        old_file = StringIO(document_v1_content)
        new_file = StringIO(document_v2_content)
        diff = diff_files(old_file, new_file)
        assert isinstance(diff, DocumentDiff)

    def test_diff_files_raises_yaml_load_error_second_file(self, document_v1_file: Path):
        """Test diff_files raises YAMLLoadError when second file is missing."""
        with pytest.raises(YAMLLoadError):
            diff_files(document_v1_file, "nonexistent.yaml")

    def test_diff_files_raises_yaml_load_error_first_file(self, document_v2_file: Path):
        """Test diff_files raises YAMLLoadError when first file is missing."""
        with pytest.raises(YAMLLoadError):
            diff_files("nonexistent.yaml", document_v2_file)

    def test_diff_files_raises_yaml_load_error_both_files(self):
        """Test diff_files raises YAMLLoadError when both files are missing."""
        with pytest.raises(YAMLLoadError):
            diff_files("nonexistent1.yaml", "nonexistent2.yaml")


class TestDiffAndFormat:
    """Test diff_and_format convenience function."""

    def test_diff_and_format_json(self, document_v1_file: Path, document_v2_file: Path):
        """Test diff_and_format with JSON output."""
        result = diff_and_format(document_v1_file, document_v2_file, output_format="json")
        assert isinstance(result, str)
        assert "added_count" in result
        assert "modified_count" in result

    def test_diff_and_format_text(self, document_v1_file: Path, document_v2_file: Path):
        """Test diff_and_format with text output."""
        result = diff_and_format(document_v1_file, document_v2_file, output_format="text")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_diff_and_format_yaml(self, document_v1_file: Path, document_v2_file: Path):
        """Test diff_and_format with YAML output."""
        result = diff_and_format(document_v1_file, document_v2_file, output_format="yaml")
        assert isinstance(result, str)
        assert "changes:" in result or "added_count:" in result

    def test_diff_and_format_with_filters(self, document_v1_file: Path, document_v2_file: Path):
        """Test diff_and_format with change type filters (using list)."""
        result = diff_and_format(
            document_v1_file,
            document_v2_file,
            output_format="json",
            filter_change_types=[ChangeType.CONTENT_CHANGED],
        )
        assert isinstance(result, str)

    def test_diff_and_format_with_filters_tuple(
        self, document_v1_file: Path, document_v2_file: Path
    ):
        """Test diff_and_format with change type filters (using tuple)."""
        # Verify that filter_change_types accepts tuple as well as list
        result = diff_and_format(
            document_v1_file,
            document_v2_file,
            output_format="json",
            filter_change_types=(ChangeType.CONTENT_CHANGED, ChangeType.SECTION_ADDED),
        )
        assert isinstance(result, str)

    def test_diff_and_format_raises_value_error_invalid_format(
        self, document_v1_file: Path, document_v2_file: Path
    ):
        """Test diff_and_format raises ValueError for invalid format."""
        with pytest.raises(ValueError, match="Unknown format"):
            diff_and_format(document_v1_file, document_v2_file, output_format="invalid")


class TestFormatDiff:
    """Test format_diff function."""

    def test_format_diff_json(self, document_v1_file: Path, document_v2_file: Path):
        """Test formatting diff as JSON."""
        diff = diff_files(document_v1_file, document_v2_file)
        result = format_diff(diff, output_format="json")
        assert isinstance(result, str)
        assert "added_count" in result

    def test_format_diff_text(self, document_v1_file: Path, document_v2_file: Path):
        """Test formatting diff as text."""
        diff = diff_files(document_v1_file, document_v2_file)
        result = format_diff(diff, output_format="text")
        assert isinstance(result, str)

    def test_format_diff_yaml(self, document_v1_file: Path, document_v2_file: Path):
        """Test formatting diff as YAML."""
        diff = diff_files(document_v1_file, document_v2_file)
        result = format_diff(diff, output_format="yaml")
        assert isinstance(result, str)


class TestCompleteWorkflow:
    """Test complete workflow integration."""

    def test_complete_workflow(self, document_v1_file: Path, document_v2_file: Path):
        """Test complete workflow: Load → Validate → Diff → Format."""
        # Load and validate
        old_doc = load_and_validate(document_v1_file)
        new_doc = load_and_validate(document_v2_file)
        assert isinstance(old_doc, Document)
        assert isinstance(new_doc, Document)

        # Diff
        diff = diff_documents(old_doc, new_doc)
        assert isinstance(diff, DocumentDiff)

        # Format
        json_output = format_diff(diff, output_format="json")
        assert isinstance(json_output, str)
        assert "added_count" in json_output

    def test_complete_workflow_convenience(self, document_v1_file: Path, document_v2_file: Path):
        """Test complete workflow using convenience functions."""
        # Use convenience function
        json_output = diff_and_format(document_v1_file, document_v2_file, output_format="json")
        assert isinstance(json_output, str)
        assert "added_count" in json_output


class TestAPIWithRealExamples:
    """Test API with real example documents."""

    def test_api_with_minimal_document(self):
        """Test API with minimal example document."""
        example_path = Path("examples/minimal_document.yaml")
        if not example_path.exists():
            pytest.skip("Example file not found")
        doc = load_and_validate(example_path)
        assert isinstance(doc, Document)

    def test_api_with_document_versions(self):
        """Test API with document version examples."""
        v1_path = Path("examples/document_v1.yaml")
        v2_path = Path("examples/document_v2.yaml")
        if not (v1_path.exists() and v2_path.exists()):
            pytest.skip("Example files not found")
        diff = diff_files(v1_path, v2_path)
        assert isinstance(diff, DocumentDiff)


class TestAPIEdgeCases:
    """Test API edge cases."""

    def test_api_with_hebrew_content(self, minimal_yaml_file: Path):
        """Test API with Hebrew content."""
        doc = load_document(minimal_yaml_file)
        assert doc.title == "חוק בדיקה"
        assert isinstance(doc.title, str)

    def test_api_with_empty_sections(self, minimal_yaml_file: Path):
        """Test API with document having empty sections."""
        doc = load_document(minimal_yaml_file)
        assert doc.sections == []
        assert isinstance(doc.sections, list)

    def test_api_with_deeply_nested_document(self):
        """Test API with deeply nested document structure."""
        nested_content = """document:
  id: "nested-test"
  title: "חוק מקונן"
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
      title: "סעיף ראשון"
      content: "תוכן"
      sections:
        - id: "sec-1-1"
          marker: "א"
          title: "תת-סעיף"
          content: "תוכן תת-סעיף"
          sections:
            - id: "sec-1-1-1"
              marker: "i"
              title: "תת-תת-סעיף"
              content: "תוכן עמוק"
              sections: []
"""
        file_like = StringIO(nested_content)
        doc = load_and_validate(file_like)
        assert isinstance(doc, Document)
        assert len(doc.sections) == 1
        assert len(doc.sections[0].sections) == 1
        assert len(doc.sections[0].sections[0].sections) == 1

    def test_api_with_empty_file(self, tmp_path: Path):
        """Test API with empty file (should raise validation error)."""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("", encoding="utf-8")
        # Empty file should raise YAMLLoadError or PydanticValidationError
        with pytest.raises((YAMLLoadError, PydanticValidationError)):
            load_document(empty_file)

    def test_api_with_whitespace_only_file(self, tmp_path: Path):
        """Test API with file containing only whitespace (should raise validation error)."""
        whitespace_file = tmp_path / "whitespace.yaml"
        whitespace_file.write_text("   \n\t  \n  ", encoding="utf-8")
        # Whitespace-only file should raise YAMLLoadError or PydanticValidationError
        with pytest.raises((YAMLLoadError, PydanticValidationError)):
            load_document(whitespace_file)
