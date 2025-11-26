"""Integration tests for loading and validating example documents."""

from pathlib import Path

import pytest

from yaml_diffs.api import diff_documents, diff_files, format_diff, load_and_validate
from yaml_diffs.loader import load_document
from yaml_diffs.models import Document
from yaml_diffs.validator import validate_document


@pytest.fixture
def examples_dir() -> Path:
    """Get path to examples directory."""
    return Path(__file__).parent.parent / "examples"


def test_load_minimal_example(examples_dir: Path) -> None:
    """Test loading minimal_document.yaml."""
    minimal_file = examples_dir / "minimal_document.yaml"

    assert minimal_file.exists(), f"Example file not found: {minimal_file}"

    doc = load_document(minimal_file)

    assert isinstance(doc, Document)
    assert doc.id == "law-1234"
    assert doc.title == "חוק הדוגמה לרגולציה"
    assert doc.type.value == "law"
    assert doc.language == "hebrew"
    assert doc.version.number == "2024-01-01"
    assert doc.source.url == "https://example.gov.il/law1234"
    assert len(doc.sections) == 1
    assert doc.sections[0].id == "sec-1"
    assert doc.sections[0].marker == "1"
    assert doc.sections[0].title == "הגדרות"


def test_load_complex_example(examples_dir: Path) -> None:
    """Test loading complex_document.yaml."""
    complex_file = examples_dir / "complex_document.yaml"

    assert complex_file.exists(), f"Example file not found: {complex_file}"

    doc = load_document(complex_file)

    assert isinstance(doc, Document)
    assert doc.id == "reg-BOI-2025-01"
    assert doc.title == "הנחיה למוסדות פיננסיים – ניהול סיכוני סייבר"
    assert doc.type.value == "regulation"
    assert doc.language == "hebrew"
    assert doc.version.number == "2025-02-01"
    assert doc.version.description == "גרסה ראשונה של ההנחיה"
    assert doc.source.url == "https://boi.org.il/regulation/cyber-risk-2025"

    # Verify nested structure
    assert len(doc.sections) > 0
    # Check that sections have nested sections
    has_nested = any(len(section.sections) > 0 for section in doc.sections)
    assert has_nested, "Complex document should have nested sections"


def test_validate_minimal_example(examples_dir: Path) -> None:
    """Test validating minimal_document.yaml."""
    minimal_file = examples_dir / "minimal_document.yaml"

    assert minimal_file.exists(), f"Example file not found: {minimal_file}"

    # Should not raise
    doc = validate_document(minimal_file)

    assert isinstance(doc, Document)
    assert doc.id == "law-1234"


def test_validate_complex_example(examples_dir: Path) -> None:
    """Test validating complex_document.yaml."""
    complex_file = examples_dir / "complex_document.yaml"

    assert complex_file.exists(), f"Example file not found: {complex_file}"

    # Should not raise
    doc = validate_document(complex_file)

    assert isinstance(doc, Document)
    assert doc.id == "reg-BOI-2025-01"

    # Verify structure is valid
    assert len(doc.sections) > 0


def test_example_documents_structure(examples_dir: Path) -> None:
    """Test that example documents have expected structure."""
    minimal_file = examples_dir / "minimal_document.yaml"
    complex_file = examples_dir / "complex_document.yaml"

    for yaml_file in [minimal_file, complex_file]:
        if not yaml_file.exists():
            pytest.skip(f"Example file not found: {yaml_file}")

        doc = load_document(yaml_file)

        # Verify required fields
        assert doc.id
        assert doc.title
        assert doc.type
        assert doc.language == "hebrew"
        assert doc.version
        assert doc.version.number
        assert doc.source
        assert doc.source.url
        assert doc.source.fetched_at
        assert doc.sections is not None  # Can be empty list

        # Verify sections structure
        for section in doc.sections:
            assert section.id
            assert isinstance(section.sections, list)


def test_example_documents_hebrew_content(examples_dir: Path) -> None:
    """Test that example documents contain Hebrew content."""
    minimal_file = examples_dir / "minimal_document.yaml"
    complex_file = examples_dir / "complex_document.yaml"

    for yaml_file in [minimal_file, complex_file]:
        if not yaml_file.exists():
            pytest.skip(f"Example file not found: {yaml_file}")

        doc = load_document(yaml_file)

        # Title should contain Hebrew characters
        assert any(ord(c) >= 0x0590 and ord(c) <= 0x05FF for c in doc.title), (
            f"Title should contain Hebrew characters: {doc.title}"
        )

        # Check sections for Hebrew content
        for section in doc.sections:
            if section.title:
                assert any(ord(c) >= 0x0590 and ord(c) <= 0x05FF for c in section.title), (
                    f"Section title should contain Hebrew characters: {section.title}"
                )


@pytest.mark.integration
class TestFullWorkflowIntegration:
    """Integration tests for complete workflows."""

    def test_load_validate_diff_workflow(self, examples_dir: Path):
        """Test complete workflow: load → validate → diff."""
        v1_file = examples_dir / "document_v1.yaml"
        v2_file = examples_dir / "document_v2.yaml"

        if not (v1_file.exists() and v2_file.exists()):
            pytest.skip("Example files not found")

        # Load both documents
        doc1 = load_document(v1_file)
        doc2 = load_document(v2_file)

        # Validate both documents
        validated_doc1 = validate_document(v1_file)
        validated_doc2 = validate_document(v2_file)

        assert validated_doc1.id == doc1.id
        assert validated_doc2.id == doc2.id

        # Diff the documents
        diff = diff_documents(doc1, doc2)

        assert diff is not None
        assert len(diff.changes) > 0

    def test_load_and_validate_convenience(self, examples_dir: Path):
        """Test load_and_validate convenience function."""
        minimal_file = examples_dir / "minimal_document.yaml"

        if not minimal_file.exists():
            pytest.skip("Example file not found")

        doc = load_and_validate(minimal_file)

        assert isinstance(doc, Document)
        assert doc.id == "law-1234"

    def test_diff_files_convenience(self, examples_dir: Path):
        """Test diff_files convenience function."""
        v1_file = examples_dir / "document_v1.yaml"
        v2_file = examples_dir / "document_v2.yaml"

        if not (v1_file.exists() and v2_file.exists()):
            pytest.skip("Example files not found")

        diff = diff_files(v1_file, v2_file)

        assert diff is not None
        assert len(diff.changes) > 0

    def test_complete_workflow_with_formatting(self, examples_dir: Path):
        """Test complete workflow: load → diff → format."""
        v1_file = examples_dir / "document_v1.yaml"
        v2_file = examples_dir / "document_v2.yaml"

        if not (v1_file.exists() and v2_file.exists()):
            pytest.skip("Example files not found")

        # Load and diff
        doc1 = load_document(v1_file)
        doc2 = load_document(v2_file)
        diff = diff_documents(doc1, doc2)

        # Format as JSON
        json_output = format_diff(diff, output_format="json")
        assert isinstance(json_output, str)
        assert "summary" in json_output
        assert "changes" in json_output

        # Format as text
        text_output = format_diff(diff, output_format="text")
        assert isinstance(text_output, str)
        assert "Document Diff Summary" in text_output or "Summary" in text_output

        # Format as YAML
        yaml_output = format_diff(diff, output_format="yaml")
        assert isinstance(yaml_output, str)
        assert "summary" in yaml_output or "changes" in yaml_output


@pytest.mark.integration
class TestErrorPropagation:
    """Test error propagation through layers."""

    def test_validation_error_propagation(self, tmp_path: Path):
        """Test that validation errors propagate correctly."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text(
            """document:
  id: "test"
  # Missing required fields
""",
            encoding="utf-8",
        )

        # Should raise validation error
        from yaml_diffs.exceptions import OpenSpecValidationError, PydanticValidationError

        with pytest.raises((OpenSpecValidationError, PydanticValidationError)):
            load_and_validate(invalid_file)

    def test_yaml_error_propagation(self, tmp_path: Path):
        """Test that YAML errors propagate correctly."""
        invalid_yaml_file = tmp_path / "bad_yaml.yaml"
        invalid_yaml_file.write_text(
            "document:\n  id: [invalid: syntax\n",
            encoding="utf-8",
        )

        # Should raise YAMLLoadError
        from yaml_diffs.exceptions import YAMLLoadError

        with pytest.raises(YAMLLoadError):
            load_and_validate(invalid_yaml_file)
