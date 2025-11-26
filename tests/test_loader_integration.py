"""Integration tests for loading and validating example documents."""

from pathlib import Path

import pytest

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

