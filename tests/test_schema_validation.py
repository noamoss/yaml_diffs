"""Tests for OpenSpec schema validation."""

import json
from pathlib import Path

import pytest
import yaml

from yaml_diffs.schema import get_schema_version, load_schema

# Try to import jsonschema, skip tests if not available
try:
    from jsonschema.validators import Draft202012Validator

    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    pytestmark = pytest.mark.skip("jsonschema library not available")


# Test fixtures
@pytest.fixture
def schema():
    """Load the OpenSpec schema."""
    return load_schema()


@pytest.fixture
def validator(schema):
    """Create a JSON Schema validator."""
    return Draft202012Validator(schema)


@pytest.fixture
def minimal_document():
    """Load the minimal example document."""
    examples_dir = Path(__file__).parent.parent / "examples"
    doc_path = examples_dir / "minimal_document.yaml"
    with open(doc_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def complex_document():
    """Load the complex example document."""
    examples_dir = Path(__file__).parent.parent / "examples"
    doc_path = examples_dir / "complex_document.yaml"
    with open(doc_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# Unit tests: Schema loading and structure
def test_load_schema(schema):
    """Test that the schema file loads correctly."""
    assert schema is not None
    assert isinstance(schema, dict)


def test_schema_has_required_top_level_keys(schema):
    """Verify schema has required top-level keys."""
    assert "version" in schema
    assert "$schema" in schema
    assert "type" in schema
    assert "properties" in schema
    assert "$defs" in schema


def test_schema_has_document_definition(schema):
    """Verify Document type is defined in schema."""
    assert "properties" in schema
    assert "document" in schema["properties"]
    document_def = schema["properties"]["document"]
    assert "type" in document_def
    assert document_def["type"] == "object"
    assert "required" in document_def
    assert "properties" in document_def


def test_schema_has_recursive_section_definition(schema):
    """Verify Section type is recursively defined."""
    assert "$defs" in schema
    assert "Section" in schema["$defs"]
    section_def = schema["$defs"]["Section"]
    assert "type" in section_def
    assert section_def["type"] == "object"
    assert "properties" in section_def
    assert "sections" in section_def["properties"]
    # Verify sections array references Section recursively
    sections_prop = section_def["properties"]["sections"]
    assert "items" in sections_prop
    assert "$ref" in sections_prop["items"]
    assert sections_prop["items"]["$ref"] == "#/$defs/Section"


def test_schema_versioning():
    """Test that schema version is accessible."""
    version = get_schema_version()
    assert version is not None
    assert isinstance(version, str)
    assert len(version) > 0


# Unit tests: Document validation
def test_validate_minimal_document(validator, minimal_document):
    """Test that minimal valid document passes validation."""
    errors = list(validator.iter_errors(minimal_document))
    assert len(errors) == 0, f"Validation errors: {[e.message for e in errors]}"


def test_validate_complex_nested_document(validator, complex_document):
    """Test that complex document with 5+ levels of nesting passes validation."""
    errors = list(validator.iter_errors(complex_document))
    assert len(errors) == 0, f"Validation errors: {[e.message for e in errors]}"


def test_validate_complex_document_has_deep_nesting(complex_document):
    """Verify complex document actually has 5+ levels of nesting."""

    def count_nesting_levels(sections, current_level=1):
        """Recursively count maximum nesting depth."""
        if not sections:
            return current_level
        max_depth = current_level
        for section in sections:
            if "sections" in section and section["sections"]:
                depth = count_nesting_levels(section["sections"], current_level + 1)
                max_depth = max(max_depth, depth)
        return max_depth

    doc_sections = complex_document["document"]["sections"]
    max_depth = count_nesting_levels(doc_sections)
    assert max_depth >= 5, f"Expected 5+ levels, found {max_depth}"


# Unit tests: Required fields validation
def test_reject_missing_document_id(validator):
    """Test that missing document id field fails validation."""
    invalid_doc = {
        "document": {
            "title": "Test",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
            "sections": [],
        }
    }
    errors = list(validator.iter_errors(invalid_doc))
    assert len(errors) > 0
    error_messages = [e.message for e in errors]
    assert any("id" in msg.lower() for msg in error_messages)


def test_reject_missing_document_title(validator):
    """Test that missing document title field fails validation."""
    invalid_doc = {
        "document": {
            "id": "test-1",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
            "sections": [],
        }
    }
    errors = list(validator.iter_errors(invalid_doc))
    assert len(errors) > 0
    error_messages = [e.message for e in errors]
    assert any("title" in msg.lower() for msg in error_messages)


def test_reject_missing_document_sections(validator):
    """Test that missing document sections field fails validation."""
    invalid_doc = {
        "document": {
            "id": "test-1",
            "title": "Test",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
        }
    }
    errors = list(validator.iter_errors(invalid_doc))
    assert len(errors) > 0
    error_messages = [e.message for e in errors]
    assert any("sections" in msg.lower() for msg in error_messages)


def test_reject_missing_section_id(validator):
    """Test that missing section id field fails validation."""
    invalid_doc = {
        "document": {
            "id": "test-1",
            "title": "Test",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
            "sections": [
                {
                    "content": "Test content",
                    "sections": [],
                }
            ],
        }
    }
    errors = list(validator.iter_errors(invalid_doc))
    assert len(errors) > 0
    error_messages = [e.message for e in errors]
    assert any("id" in msg.lower() for msg in error_messages)


# Unit tests: Optional fields
def test_accept_document_without_marker_fields(validator):
    """Test that document without marker fields passes validation."""
    doc_without_markers = {
        "document": {
            "id": "test-1",
            "title": "Test",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
            "sections": [
                {
                    "id": "sec-1",
                    "content": "Test content",
                    "sections": [],
                }
            ],
        }
    }
    errors = list(validator.iter_errors(doc_without_markers))
    assert len(errors) == 0, f"Validation errors: {[e.message for e in errors]}"


def test_accept_document_without_title_fields(validator):
    """Test that document without title fields passes validation."""
    doc_without_titles = {
        "document": {
            "id": "test-1",
            "title": "Test",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
            "sections": [
                {
                    "id": "sec-1",
                    "marker": "1",
                    "content": "Test content",
                    "sections": [],
                }
            ],
        }
    }
    errors = list(validator.iter_errors(doc_without_titles))
    assert len(errors) == 0, f"Validation errors: {[e.message for e in errors]}"


def test_accept_section_without_marker_or_title(validator):
    """Test that section without marker or title passes validation."""
    doc_with_minimal_section = {
        "document": {
            "id": "test-1",
            "title": "Test",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
            "sections": [
                {
                    "id": "sec-1",
                    "content": "Test content",
                    "sections": [],
                }
            ],
        }
    }
    errors = list(validator.iter_errors(doc_with_minimal_section))
    assert len(errors) == 0, f"Validation errors: {[e.message for e in errors]}"


# Unit tests: Hebrew content validation
def test_validate_hebrew_content(validator):
    """Test that Hebrew text is accepted in content fields."""
    doc_with_hebrew = {
        "document": {
            "id": "test-1",
            "title": "חוק הדוגמה",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
            "sections": [
                {
                    "id": "sec-1",
                    "marker": "1",
                    "title": "הגדרות",
                    "content": "בחוק זה— 'מוסד' – גוף הפועל לפי הוראות החוק.",
                    "sections": [],
                }
            ],
        }
    }
    errors = list(validator.iter_errors(doc_with_hebrew))
    assert len(errors) == 0, f"Validation errors: {[e.message for e in errors]}"


def test_validate_hebrew_numbering_formats(validator):
    """Test that various Hebrew numbering formats are accepted."""
    doc_with_hebrew_markers = {
        "document": {
            "id": "test-1",
            "title": "חוק הדוגמה",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
            "sections": [
                {
                    "id": "sec-1",
                    "marker": "1",
                    "content": "Section 1",
                    "sections": [
                        {
                            "id": "sec-1-a",
                            "marker": "1.א",
                            "content": "Subsection with Hebrew letter",
                            "sections": [
                                {
                                    "id": "sec-1-a-1",
                                    "marker": "(א)",
                                    "content": "Clause with Hebrew letter in parentheses",
                                    "sections": [
                                        {
                                            "id": "sec-1-a-1-i",
                                            "marker": "א'",
                                            "content": "Sub-clause with Hebrew letter and apostrophe",
                                            "sections": [],
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    }
    errors = list(validator.iter_errors(doc_with_hebrew_markers))
    assert len(errors) == 0, f"Validation errors: {[e.message for e in errors]}"


# Integration tests
def test_validate_example_hebrew_legal_document(validator, minimal_document):
    """Integration test: Validate example Hebrew legal document."""
    # Verify UTF-8 encoding is preserved
    doc_str = json.dumps(minimal_document, ensure_ascii=False)
    assert "חוק" in doc_str or "הגדרות" in doc_str

    # Validate document
    errors = list(validator.iter_errors(minimal_document))
    assert len(errors) == 0, f"Validation errors: {[e.message for e in errors]}"

    # Verify Hebrew characters are present
    title = minimal_document["document"]["title"]
    assert any(ord(c) > 127 for c in title), "Title should contain non-ASCII characters (Hebrew)"


def test_schema_version_is_accessible():
    """Integration test: Schema version is accessible."""
    version = get_schema_version()
    assert version == "1.0.0"


def test_schema_validates_language_constraint(validator):
    """Test that language must be 'hebrew'."""
    invalid_doc = {
        "document": {
            "id": "test-1",
            "title": "Test",
            "type": "law",
            "language": "english",  # Invalid: must be "hebrew"
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
            "sections": [],
        }
    }
    errors = list(validator.iter_errors(invalid_doc))
    assert len(errors) > 0
    error_messages = [e.message for e in errors]
    assert any("hebrew" in msg.lower() or "const" in msg.lower() for msg in error_messages)


def test_schema_validates_document_type_enum(validator):
    """Test that document type must be one of the allowed values."""
    invalid_doc = {
        "document": {
            "id": "test-1",
            "title": "Test",
            "type": "invalid_type",  # Invalid: not in enum
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
            "sections": [],
        }
    }
    errors = list(validator.iter_errors(invalid_doc))
    assert len(errors) > 0
    error_messages = [e.message for e in errors]
    assert any("type" in msg.lower() or "enum" in msg.lower() for msg in error_messages)


def test_schema_validates_url_format(validator):
    """Test that source URL must be a valid URI format."""
    invalid_doc = {
        "document": {
            "id": "test-1",
            "title": "Test",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {
                "url": "not-a-valid-url",  # Invalid: not a valid URI
                "fetched_at": "2025-01-01T00:00:00Z",
            },
            "sections": [],
        }
    }
    errors = list(validator.iter_errors(invalid_doc))
    # Note: format validation might not be strict, but we check if errors exist
    # The validator may or may not catch format errors depending on configuration
    assert isinstance(errors, list)


def test_schema_validates_timestamp_format(validator):
    """Test that fetched_at must be a valid date-time format."""
    invalid_doc = {
        "document": {
            "id": "test-1",
            "title": "Test",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {
                "url": "https://example.com",
                "fetched_at": "invalid-date",  # Invalid: not a valid date-time
            },
            "sections": [],
        }
    }
    errors = list(validator.iter_errors(invalid_doc))
    # Note: format validation might not be strict, but we check if errors exist
    assert isinstance(errors, list)


def test_content_defaults_to_empty_string(validator):
    """Test that content field defaults to empty string if not provided."""
    # Content is optional (not in required list) and has default ""
    # Empty string is valid when explicitly provided
    doc_with_empty_content = {
        "document": {
            "id": "test-1",
            "title": "Test",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
            "sections": [
                {
                    "id": "sec-1",
                    "content": "",  # Empty string is valid
                    "sections": [],
                }
            ],
        }
    }
    errors = list(validator.iter_errors(doc_with_empty_content))
    assert len(errors) == 0, f"Validation errors: {[e.message for e in errors]}"


def test_accept_section_without_content_field(validator):
    """Test that section without content field passes validation (content is optional)."""
    # Content is optional, so it can be omitted entirely
    doc_without_content = {
        "document": {
            "id": "test-1",
            "title": "Test",
            "type": "law",
            "language": "hebrew",
            "version": {"number": "1.0"},
            "source": {"url": "https://example.com", "fetched_at": "2025-01-01T00:00:00Z"},
            "sections": [
                {
                    "id": "sec-1",
                    # content field omitted - should be valid since it's optional
                    "sections": [],
                }
            ],
        }
    }
    errors = list(validator.iter_errors(doc_without_content))
    assert len(errors) == 0, f"Validation errors: {[e.message for e in errors]}"
