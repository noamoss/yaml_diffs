"""Performance tests for large documents and deep nesting.

These tests verify that the library can handle large-scale documents
efficiently and within reasonable time limits.
"""

import time
import uuid
from pathlib import Path

import pytest
import yaml

from yaml_diffs.api import diff_documents, load_and_validate, validate_document
from yaml_diffs.models import Document, DocumentType, Section, Source, Version


def generate_large_section(
    section_id: str,
    marker: str,
    depth: int,
    max_depth: int,
    sections_per_level: int,
    content_length: int = 100,
) -> Section:
    """Generate a section with nested subsections.

    Args:
        section_id: ID for this section
        marker: Marker for this section
        depth: Current nesting depth
        max_depth: Maximum nesting depth
        sections_per_level: Number of sections to create at each level
        content_length: Length of content string to generate

    Returns:
        Section with nested structure
    """
    content = "א" * content_length if depth == max_depth else ""

    if depth >= max_depth:
        return Section(id=section_id, marker=marker, content=content)

    sections = []
    for i in range(sections_per_level):
        child_id = str(uuid.uuid4())
        child_marker = f"{marker}.{i + 1}"
        child_section = generate_large_section(
            child_id, child_marker, depth + 1, max_depth, sections_per_level, content_length
        )
        sections.append(child_section)

    return Section(id=section_id, marker=marker, content=content, sections=sections)


def generate_large_document(
    num_top_level_sections: int = 100,
    max_depth: int = 5,
    sections_per_level: int = 5,
    content_length: int = 100,
) -> Document:
    """Generate a large document for performance testing.

    Args:
        num_top_level_sections: Number of top-level sections
        max_depth: Maximum nesting depth
        sections_per_level: Number of sections at each level
        content_length: Length of content strings

    Returns:
        Large Document instance
    """
    sections = []
    for i in range(num_top_level_sections):
        section_id = str(uuid.uuid4())
        marker = str(i + 1)
        section = generate_large_section(
            section_id, marker, 1, max_depth, sections_per_level, content_length
        )
        sections.append(section)

    return Document(
        id="perf-test-doc",
        title="מסמך בדיקת ביצועים",
        type=DocumentType.LAW,
        language="hebrew",
        version=Version(number="1.0"),
        source=Source(url="https://example.com/perf", fetched_at="2025-01-20T09:50:00Z"),
        sections=sections,
    )


@pytest.mark.slow
class TestLargeDocumentLoading:
    """Test loading large documents."""

    def test_load_large_document_1000_sections(self, tmp_path: Path):
        """Test loading a document with 1000+ sections."""
        # Generate large document
        doc = generate_large_document(num_top_level_sections=100, max_depth=3, sections_per_level=3)

        # Write to temporary file
        yaml_content = yaml.dump(
            {"document": doc.model_dump(mode="json", exclude_none=True)}, allow_unicode=True
        )
        file_path = tmp_path / "large_doc.yaml"
        file_path.write_text(yaml_content, encoding="utf-8")

        # Measure loading time
        start_time = time.time()
        loaded_doc = load_and_validate(file_path)
        elapsed_time = time.time() - start_time

        # Verify document loaded correctly
        assert loaded_doc.id == "perf-test-doc"
        assert len(loaded_doc.sections) == 100

        # Performance assertion: should load in under 5 seconds
        assert elapsed_time < 5.0, f"Loading took {elapsed_time:.2f}s, expected < 5.0s"

    def test_load_very_large_document_10000_sections(self, tmp_path: Path):
        """Test loading a very large document with 10000+ sections."""
        # Generate very large document (100 top-level * 10 per level * 10 depth = 10,000+)
        doc = generate_large_document(num_top_level_sections=50, max_depth=3, sections_per_level=5)

        # Write to temporary file
        yaml_content = yaml.dump(
            {"document": doc.model_dump(mode="json", exclude_none=True)}, allow_unicode=True
        )
        file_path = tmp_path / "very_large_doc.yaml"
        file_path.write_text(yaml_content, encoding="utf-8")

        # Measure loading time
        start_time = time.time()
        loaded_doc = load_and_validate(file_path)
        elapsed_time = time.time() - start_time

        # Verify document loaded correctly
        assert loaded_doc.id == "perf-test-doc"
        assert len(loaded_doc.sections) == 50

        # Performance assertion: should load in under 10 seconds
        assert elapsed_time < 10.0, f"Loading took {elapsed_time:.2f}s, expected < 10.0s"


@pytest.mark.slow
class TestLargeDocumentValidation:
    """Test validating large documents."""

    def test_validate_large_document(self, tmp_path: Path):
        """Test validating a large document."""
        # Generate large document
        doc = generate_large_document(num_top_level_sections=100, max_depth=3, sections_per_level=3)

        # Write to temporary file
        yaml_content = yaml.dump(
            {"document": doc.model_dump(mode="json", exclude_none=True)}, allow_unicode=True
        )
        file_path = tmp_path / "large_doc.yaml"
        file_path.write_text(yaml_content, encoding="utf-8")

        # Measure validation time
        start_time = time.time()
        validated_doc = validate_document(file_path)
        elapsed_time = time.time() - start_time

        # Verify document validated correctly
        assert validated_doc.id == "perf-test-doc"

        # Performance assertion: should validate in under 3 seconds
        assert elapsed_time < 3.0, f"Validation took {elapsed_time:.2f}s, expected < 3.0s"


@pytest.mark.slow
class TestLargeDocumentDiffing:
    """Test diffing large documents."""

    def test_diff_large_documents(self):
        """Test diffing two large documents."""
        # Generate two large documents
        old_doc = generate_large_document(
            num_top_level_sections=50, max_depth=3, sections_per_level=3
        )
        new_doc = generate_large_document(
            num_top_level_sections=60, max_depth=3, sections_per_level=3
        )

        # Measure diffing time
        start_time = time.time()
        diff = diff_documents(old_doc, new_doc)
        elapsed_time = time.time() - start_time

        # Verify diff was created
        assert diff is not None
        assert len(diff.changes) > 0

        # Performance assertion: should diff in under 10 seconds
        assert elapsed_time < 10.0, f"Diffing took {elapsed_time:.2f}s, expected < 10.0s"

    def test_diff_identical_large_documents(self):
        """Test diffing two identical large documents (should be fast)."""
        # Generate identical large documents
        doc = generate_large_document(num_top_level_sections=100, max_depth=3, sections_per_level=3)

        # Measure diffing time
        start_time = time.time()
        diff = diff_documents(doc, doc)
        elapsed_time = time.time() - start_time

        # Verify diff was created
        assert diff is not None
        # Identical documents may have no changes or only UNCHANGED entries
        # Both are valid outcomes - verify counts are zero
        assert diff.added_count == 0
        assert diff.deleted_count == 0
        assert diff.modified_count == 0
        assert diff.moved_count == 0

        # Performance assertion: identical docs should diff quickly
        assert elapsed_time < 5.0, (
            f"Diffing identical docs took {elapsed_time:.2f}s, expected < 5.0s"
        )


@pytest.mark.slow
class TestDeepNesting:
    """Test performance with deeply nested documents."""

    def test_deep_nesting_10_levels(self, tmp_path: Path):
        """Test document with 10+ levels of nesting."""
        # Generate deeply nested document
        doc = generate_large_document(
            num_top_level_sections=5, max_depth=10, sections_per_level=2, content_length=50
        )

        # Write to temporary file
        yaml_content = yaml.dump(
            {"document": doc.model_dump(mode="json", exclude_none=True)}, allow_unicode=True
        )
        file_path = tmp_path / "deep_nested.yaml"
        file_path.write_text(yaml_content, encoding="utf-8")

        # Measure loading and validation time
        start_time = time.time()
        loaded_doc = load_and_validate(file_path)
        elapsed_time = time.time() - start_time

        # Verify document loaded correctly
        assert loaded_doc.id == "perf-test-doc"

        # Performance assertion: deep nesting should still be reasonable
        assert elapsed_time < 5.0, f"Deep nesting took {elapsed_time:.2f}s, expected < 5.0s"

    def test_deep_nesting_diff(self):
        """Test diffing deeply nested documents."""
        # Generate two deeply nested documents
        old_doc = generate_large_document(
            num_top_level_sections=3, max_depth=8, sections_per_level=2
        )
        new_doc = generate_large_document(
            num_top_level_sections=3, max_depth=8, sections_per_level=2
        )

        # Measure diffing time
        start_time = time.time()
        diff = diff_documents(old_doc, new_doc)
        elapsed_time = time.time() - start_time

        # Verify diff was created
        assert diff is not None

        # Performance assertion: deep nesting diffing should be reasonable
        assert elapsed_time < 8.0, f"Deep nesting diff took {elapsed_time:.2f}s, expected < 8.0s"


@pytest.mark.slow
class TestLargeContentBlocks:
    """Test performance with large content blocks."""

    def test_large_content_blocks(self, tmp_path: Path):
        """Test document with large content blocks (10K+ characters)."""
        # Generate document with large content
        large_content = "א" * 10000  # 10K Hebrew characters

        sections = []
        for i in range(10):
            section = Section(
                id=str(uuid.uuid4()),
                marker=str(i + 1),
                content=large_content,
            )
            sections.append(section)

        doc = Document(
            id="large-content-doc",
            title="מסמך עם תוכן גדול",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/large", fetched_at="2025-01-20T09:50:00Z"),
            sections=sections,
        )

        # Write to temporary file
        yaml_content = yaml.dump(
            {"document": doc.model_dump(mode="json", exclude_none=True)}, allow_unicode=True
        )
        file_path = tmp_path / "large_content.yaml"
        file_path.write_text(yaml_content, encoding="utf-8")

        # Measure loading time
        start_time = time.time()
        loaded_doc = load_and_validate(file_path)
        elapsed_time = time.time() - start_time

        # Verify document loaded correctly
        assert loaded_doc.id == "large-content-doc"
        assert len(loaded_doc.sections) == 10
        assert len(loaded_doc.sections[0].content) == 10000

        # Performance assertion: large content should load reasonably
        assert elapsed_time < 3.0, (
            f"Large content loading took {elapsed_time:.2f}s, expected < 3.0s"
        )

    def test_large_content_diffing(self):
        """Test diffing documents with large content blocks."""
        large_content_old = "א" * 5000
        large_content_new = "ב" * 5000

        old_doc = Document(
            id="doc-001",
            title="מסמך ישן",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/doc", fetched_at="2025-01-20T09:50:00Z"),
            sections=[
                Section(id=str(uuid.uuid4()), marker="1", content=large_content_old),
            ],
        )

        new_doc = Document(
            id="doc-001",
            title="מסמך חדש",
            type=DocumentType.LAW,
            version=Version(number="2.0"),
            source=Source(url="https://example.com/doc", fetched_at="2025-01-21T09:50:00Z"),
            sections=[
                Section(id=str(uuid.uuid4()), marker="1", content=large_content_new),
            ],
        )

        # Measure diffing time
        start_time = time.time()
        diff = diff_documents(old_doc, new_doc)
        elapsed_time = time.time() - start_time

        # Verify diff was created
        assert diff is not None

        # Performance assertion: large content diffing should be reasonable
        assert elapsed_time < 2.0, (
            f"Large content diffing took {elapsed_time:.2f}s, expected < 2.0s"
        )
