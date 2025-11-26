"""Tests for YAML loader utilities."""

from io import StringIO
from pathlib import Path

import pytest
import yaml

from yaml_diffs.exceptions import PydanticValidationError, YAMLLoadError
from yaml_diffs.loader import load_document, load_yaml, load_yaml_file
from yaml_diffs.models import Document


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
def hebrew_yaml_content() -> str:
    """YAML document with Hebrew content."""
    return """document:
  id: "hebrew-test"
  title: "חוק יסוד: כבוד האדם וחירותו"
  type: "law"
  language: "hebrew"
  version:
    number: "1992-03-17"
  source:
    url: "https://example.gov.il/law"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: "א"
      title: "הגדרות"
      content: |
        בחוק זה—
        "מוסד" – גוף הפועל לפי הוראות החוק.
      sections: []
"""


@pytest.fixture
def invalid_yaml_content() -> str:
    """Invalid YAML syntax."""
    return """document:
  id: "test"
  title: [invalid: yaml
"""


# Tests for load_yaml_file
def test_load_yaml_file_success(minimal_yaml_content: str, tmp_path: Path) -> None:
    """Test loading valid YAML file."""
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(minimal_yaml_content, encoding="utf-8")

    data = load_yaml_file(yaml_file)

    assert isinstance(data, dict)
    assert "document" in data
    assert data["document"]["id"] == "test-123"


def test_load_yaml_file_with_string_path(minimal_yaml_content: str, tmp_path: Path) -> None:
    """Test loading YAML file with string path."""
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(minimal_yaml_content, encoding="utf-8")

    data = load_yaml_file(str(yaml_file))

    assert isinstance(data, dict)
    assert "document" in data


def test_load_yaml_file_not_found() -> None:
    """Test loading non-existent file raises YAMLLoadError."""
    with pytest.raises(YAMLLoadError) as exc_info:
        load_yaml_file("nonexistent_file.yaml")

    assert "not found" in str(exc_info.value).lower()
    assert exc_info.value.file_path == "nonexistent_file.yaml"


def test_load_yaml_file_invalid_syntax(invalid_yaml_content: str, tmp_path: Path) -> None:
    """Test loading file with invalid YAML syntax raises YAMLLoadError."""
    yaml_file = tmp_path / "invalid.yaml"
    yaml_file.write_text(invalid_yaml_content, encoding="utf-8")

    with pytest.raises(YAMLLoadError) as exc_info:
        load_yaml_file(yaml_file)

    assert "Failed to parse YAML" in str(exc_info.value)
    assert exc_info.value.original_error is not None
    assert isinstance(exc_info.value.original_error, yaml.YAMLError)


def test_load_yaml_file_empty_file(tmp_path: Path) -> None:
    """Test loading empty file raises YAMLLoadError."""
    yaml_file = tmp_path / "empty.yaml"
    yaml_file.write_text("", encoding="utf-8")

    with pytest.raises(YAMLLoadError) as exc_info:
        load_yaml_file(yaml_file)

    assert "empty" in str(exc_info.value).lower() or "null" in str(exc_info.value).lower()


def test_load_yaml_file_hebrew_content(hebrew_yaml_content: str, tmp_path: Path) -> None:
    """Test loading YAML file with Hebrew content."""
    yaml_file = tmp_path / "hebrew.yaml"
    yaml_file.write_text(hebrew_yaml_content, encoding="utf-8")

    data = load_yaml_file(yaml_file)

    assert isinstance(data, dict)
    assert "document" in data
    assert "חוק יסוד" in data["document"]["title"]


# Tests for load_yaml
def test_load_yaml_from_string(minimal_yaml_content: str) -> None:
    """Test loading YAML from string."""
    data = load_yaml(minimal_yaml_content)

    assert isinstance(data, dict)
    assert "document" in data
    assert data["document"]["id"] == "test-123"


def test_load_yaml_from_file_like(minimal_yaml_content: str) -> None:
    """Test loading YAML from file-like object."""
    file_like = StringIO(minimal_yaml_content)

    data = load_yaml(file_like)

    assert isinstance(data, dict)
    assert "document" in data


def test_load_yaml_invalid_syntax() -> None:
    """Test loading invalid YAML syntax raises YAMLLoadError."""
    invalid_yaml = "document:\n  id: [invalid: syntax"

    with pytest.raises(YAMLLoadError) as exc_info:
        load_yaml(invalid_yaml)

    assert "Failed to parse YAML" in str(exc_info.value)
    assert exc_info.value.original_error is not None


def test_load_yaml_empty_string() -> None:
    """Test loading empty string raises YAMLLoadError."""
    with pytest.raises(YAMLLoadError) as exc_info:
        load_yaml("")

    assert "empty" in str(exc_info.value).lower() or "null" in str(exc_info.value).lower()


def test_load_yaml_invalid_type() -> None:
    """Test loading with invalid type raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        load_yaml(123)  # type: ignore[arg-type]

    assert "must be str or TextIO" in str(exc_info.value)


def test_load_yaml_hebrew_content(hebrew_yaml_content: str) -> None:
    """Test loading YAML with Hebrew content from string."""
    data = load_yaml(hebrew_yaml_content)

    assert isinstance(data, dict)
    assert "חוק יסוד" in data["document"]["title"]


# Tests for load_document
def test_load_document_success(minimal_yaml_content: str, tmp_path: Path) -> None:
    """Test loading document from file path."""
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(minimal_yaml_content, encoding="utf-8")

    doc = load_document(yaml_file)

    assert isinstance(doc, Document)
    assert doc.id == "test-123"
    assert doc.title == "חוק בדיקה"
    assert doc.type.value == "law"


def test_load_document_from_string_path(minimal_yaml_content: str, tmp_path: Path) -> None:
    """Test loading document from string path."""
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(minimal_yaml_content, encoding="utf-8")

    doc = load_document(str(yaml_file))

    assert isinstance(doc, Document)
    assert doc.id == "test-123"


def test_load_document_from_file_like(minimal_yaml_content: str) -> None:
    """Test loading document from file-like object."""
    file_like = StringIO(minimal_yaml_content)

    doc = load_document(file_like)

    assert isinstance(doc, Document)
    assert doc.id == "test-123"


def test_load_document_missing_document_key(tmp_path: Path) -> None:
    """Test loading document without 'document' key raises YAMLLoadError."""
    yaml_file = tmp_path / "invalid.yaml"
    yaml_file.write_text("id: test\n", encoding="utf-8")

    with pytest.raises(YAMLLoadError) as exc_info:
        load_document(yaml_file)

    assert "document" in str(exc_info.value).lower()


def test_load_document_missing_required_fields(tmp_path: Path) -> None:
    """Test loading document with missing required fields raises PydanticValidationError."""
    yaml_file = tmp_path / "incomplete.yaml"
    yaml_file.write_text(
        """document:
  id: "test"
""",
        encoding="utf-8",
    )

    with pytest.raises(PydanticValidationError) as exc_info:
        load_document(yaml_file)

    assert "validation failed" in str(exc_info.value).lower()
    assert len(exc_info.value.errors) > 0


def test_load_document_hebrew_content(hebrew_yaml_content: str, tmp_path: Path) -> None:
    """Test loading document with Hebrew content."""
    yaml_file = tmp_path / "hebrew.yaml"
    yaml_file.write_text(hebrew_yaml_content, encoding="utf-8")

    doc = load_document(yaml_file)

    assert isinstance(doc, Document)
    assert "חוק יסוד" in doc.title
    assert len(doc.sections) == 1
    assert doc.sections[0].id == "sec-1"
    assert "הגדרות" in doc.sections[0].title or doc.sections[0].title == "הגדרות"


def test_load_document_error_messages_clear(tmp_path: Path) -> None:
    """Test that error messages are clear and actionable."""
    yaml_file = tmp_path / "bad.yaml"
    yaml_file.write_text(
        """document:
  id: "test"
  title: "Test"
""",
        encoding="utf-8",
    )

    with pytest.raises(PydanticValidationError) as exc_info:
        load_document(yaml_file)

    error_message = str(exc_info.value)
    # Should contain field paths
    assert " -> " in error_message or any("type" in str(err) for err in exc_info.value.errors)
    # Should be formatted clearly
    assert "\n" in error_message or ":" in error_message


def test_load_document_invalid_type() -> None:
    """Test loading document with invalid type raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        load_document(123)  # type: ignore[arg-type]

    assert "must be str, Path, or TextIO" in str(exc_info.value)

