"""Tests for document diffing engine."""

import uuid

import pytest

from yaml_diffs.diff import diff_documents
from yaml_diffs.diff_types import ChangeType, DiffResult, DocumentDiff
from yaml_diffs.models import Document, DocumentType, Section, Source, Version


@pytest.fixture
def sample_id() -> str:
    """Generate a sample ID for testing."""
    return str(uuid.uuid4())


@pytest.fixture
def minimal_document(sample_id: str) -> Document:
    """Create a minimal document with required fields only."""
    return Document(
        id="law-1234",
        title="חוק הדוגמה",
        type=DocumentType.LAW,
        version=Version(number="1.0"),
        source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
    )


class TestDiffAddedSection:
    """Test detecting added sections."""

    def test_diff_added_section_root_level(self, minimal_document: Document):
        """Test detect added section at root level."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[
                Section(id="sec-1", marker="1", content="Section 1"),
            ],
        )
        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[
                Section(id="sec-1", marker="1", content="Section 1"),
                Section(id="sec-2", marker="2", content="Section 2"),  # Added
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        assert diff.added_count == 1
        added_changes = [c for c in diff.changes if c.change_type == ChangeType.ADDED]
        assert len(added_changes) == 1
        assert added_changes[0].marker == "2"
        assert added_changes[0].new_content == "Section 2"

    def test_diff_added_nested_section(self, minimal_document: Document):
        """Test detect added nested section."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[
                Section(
                    id="sec-1",
                    marker="1",
                    content="Parent",
                    sections=[Section(id="sec-1-1", marker="א", content="Child 1")],
                ),
            ],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[
                Section(
                    id="sec-1",
                    marker="1",
                    content="Parent",
                    sections=[
                        Section(id="sec-1-1", marker="א", content="Child 1"),
                        Section(id="sec-1-2", marker="ב", content="Child 2"),  # Added
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        assert diff.added_count == 1
        added_changes = [c for c in diff.changes if c.change_type == ChangeType.ADDED]
        assert len(added_changes) == 1
        assert added_changes[0].marker == "ב"


class TestDiffDeletedSection:
    """Test detecting deleted sections."""

    def test_diff_deleted_section(self, minimal_document: Document):
        """Test detect deleted section."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[
                Section(id="sec-1", marker="1", content="Section 1"),
                Section(id="sec-2", marker="2", content="Section 2"),
            ],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[
                Section(id="sec-1", marker="1", content="Section 1"),
                # sec-2 deleted
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        assert diff.deleted_count == 1
        deleted_changes = [c for c in diff.changes if c.change_type == ChangeType.DELETED]
        assert len(deleted_changes) == 1
        assert deleted_changes[0].marker == "2"
        assert deleted_changes[0].old_content == "Section 2"


class TestDiffContentChange:
    """Test detecting content changes."""

    def test_diff_content_change(self, minimal_document: Document):
        """Test detect content change, same marker+path."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[Section(id="sec-1", marker="1", content="Old content")],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[Section(id="sec-1", marker="1", content="New content")],
        )

        diff = diff_documents(old_doc, new_doc)

        assert diff.modified_count == 1
        content_changes = [c for c in diff.changes if c.change_type == ChangeType.CONTENT_CHANGED]
        assert len(content_changes) == 1
        assert content_changes[0].old_content == "Old content"
        assert content_changes[0].new_content == "New content"


class TestDiffMovement:
    """Test detecting section movements."""

    def test_diff_section_movement(self, minimal_document: Document):
        """Test detect section movement (same marker, different parent path)."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[
                Section(
                    id="chap-1",
                    marker="פרק א'",
                    content="",
                    sections=[
                        Section(id="sec-1", marker="1", content="Section 1"),
                    ],
                ),
            ],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[
                Section(
                    id="chap-2",
                    marker="פרק ב'",
                    content="",
                    sections=[
                        Section(id="sec-1", marker="1", content="Section 1"),  # Moved
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        assert diff.moved_count == 1
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.MOVED]
        assert len(moved_changes) == 1
        assert moved_changes[0].marker == "1"
        assert moved_changes[0].old_marker_path == ("פרק א'", "1")
        assert moved_changes[0].new_marker_path == ("פרק ב'", "1")

    def test_diff_moved_with_content_change(self, minimal_document: Document):
        """Test detect moved section with content change (two entries)."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[
                Section(
                    id="chap-1",
                    marker="פרק א'",
                    content="",
                    sections=[
                        Section(
                            id="sec-1",
                            marker="1",
                            content="Original content text here",
                            title="Original Title",
                        ),
                    ],
                ),
            ],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[
                Section(
                    id="chap-2",
                    marker="פרק ב'",
                    content="",
                    sections=[
                        Section(
                            id="sec-1",
                            marker="1",
                            content="Original content text here modified",
                            title="Original Title",  # Same title
                        ),  # Moved + content changed (>80% similarity)
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        # Should have both MOVED and CONTENT_CHANGED
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.MOVED]
        content_changes = [c for c in diff.changes if c.change_type == ChangeType.CONTENT_CHANGED]

        assert len(moved_changes) == 1
        assert len(content_changes) == 1
        assert diff.moved_count == 1
        assert diff.modified_count == 1


class TestDiffRenamed:
    """Test detecting renamed sections (title changes)."""

    def test_diff_renamed_section(self, minimal_document: Document):
        """Test detect renamed section (title change, same marker+path+content)."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[
                Section(
                    id="sec-1",
                    marker="1",
                    content="Same content",
                    title="Old Title",
                ),
            ],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[
                Section(
                    id="sec-1",
                    marker="1",
                    content="Same content",
                    title="New Title",
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        assert diff.modified_count == 1
        renamed_changes = [c for c in diff.changes if c.change_type == ChangeType.RENAMED]
        assert len(renamed_changes) == 1
        assert renamed_changes[0].old_title == "Old Title"
        assert renamed_changes[0].new_title == "New Title"

    def test_diff_exact_match_with_both_content_and_title_change(self, minimal_document: Document):
        """Test that exact match with both content and title changes records both CONTENT_CHANGED and RENAMED."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[
                Section(
                    id="sec-1",
                    marker="1",
                    content="Original content",
                    title="Old Title",
                ),
            ],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[
                Section(
                    id="sec-1",
                    marker="1",
                    content="Updated content",
                    title="New Title",
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        # Should have both CONTENT_CHANGED and RENAMED
        content_changes = [c for c in diff.changes if c.change_type == ChangeType.CONTENT_CHANGED]
        renamed_changes = [c for c in diff.changes if c.change_type == ChangeType.RENAMED]

        assert len(content_changes) == 1, "Should have 1 CONTENT_CHANGED entry"
        assert len(renamed_changes) == 1, "Should have 1 RENAMED entry"
        assert diff.modified_count == 2, "modified_count should be 2 (both changes)"

        # Verify CONTENT_CHANGED has correct content
        assert content_changes[0].old_content == "Original content"
        assert content_changes[0].new_content == "Updated content"

        # Verify RENAMED has correct title
        assert renamed_changes[0].old_title == "Old Title"
        assert renamed_changes[0].new_title == "New Title"


class TestDiffEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_diff_empty_documents(self, minimal_document: Document):
        """Test diff empty documents."""
        old_doc = minimal_document
        new_doc = minimal_document

        diff = diff_documents(old_doc, new_doc)

        assert len(diff.changes) == 0
        assert diff.added_count == 0
        assert diff.deleted_count == 0
        assert diff.modified_count == 0
        assert diff.moved_count == 0

    def test_diff_no_changes(self, minimal_document: Document):
        """Test diff identical documents."""
        section = Section(id="sec-1", marker="1", content="Content")
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[section],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[Section(id="sec-1", marker="1", content="Content")],
        )

        diff = diff_documents(old_doc, new_doc)

        unchanged = [c for c in diff.changes if c.change_type == ChangeType.UNCHANGED]
        assert len(unchanged) == 1
        assert unchanged[0].marker == "1"

    def test_diff_content_empty_to_nonempty(self, minimal_document: Document):
        """Test edge case: empty to non-empty content."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[Section(id="sec-1", marker="1", content="")],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[Section(id="sec-1", marker="1", content="New content")],
        )

        diff = diff_documents(old_doc, new_doc)

        content_changes = [c for c in diff.changes if c.change_type == ChangeType.CONTENT_CHANGED]
        assert len(content_changes) == 1
        assert content_changes[0].old_content == ""
        assert content_changes[0].new_content == "New content"


class TestDiffPathTracking:
    """Test path tracking functionality."""

    def test_diff_marker_path_tracking(self, minimal_document: Document):
        """Test verify marker path tracking for nested sections."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[
                Section(
                    id="chap-1",
                    marker="פרק א'",
                    content="",
                    sections=[
                        Section(
                            id="sec-1",
                            marker="1",
                            content="",
                            sections=[
                                Section(id="sec-1-1", marker="א", content="Deep"),
                            ],
                        ),
                    ],
                ),
            ],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[
                Section(
                    id="chap-1",
                    marker="פרק א'",
                    content="",
                    sections=[
                        Section(
                            id="sec-1",
                            marker="1",
                            content="",
                            sections=[
                                Section(
                                    id="sec-1-1",
                                    marker="א",
                                    content="Changed",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        content_changes = [c for c in diff.changes if c.change_type == ChangeType.CONTENT_CHANGED]
        assert len(content_changes) == 1
        assert content_changes[0].old_marker_path == ("פרק א'", "1", "א")
        assert content_changes[0].new_marker_path == ("פרק א'", "1", "א")

    def test_diff_id_path_tracking(self, minimal_document: Document):
        """Test verify ID path tracking (hybrid approach)."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[
                Section(
                    id="chap-1",
                    marker="פרק א'",
                    content="",
                    sections=[
                        Section(id="sec-1", marker="1", content="Content"),
                    ],
                ),
            ],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[
                Section(
                    id="chap-1",
                    marker="פרק א'",
                    content="",
                    sections=[
                        Section(id="sec-1", marker="1", content="Changed"),
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        content_changes = [c for c in diff.changes if c.change_type == ChangeType.CONTENT_CHANGED]
        assert len(content_changes) == 1
        assert content_changes[0].old_id_path == ["chap-1", "sec-1"]
        assert content_changes[0].new_id_path == ["chap-1", "sec-1"]


class TestDiffDuplicateMarkers:
    """Test duplicate marker validation."""

    def test_duplicate_markers_raise_error(self, minimal_document: Document):
        """Test duplicate markers at same level should raise ValueError."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[
                Section(id="sec-1", marker="1", content="Section 1"),
                Section(id="sec-2", marker="1", content="Section 2"),  # Duplicate!
            ],
        )

        new_doc = minimal_document

        with pytest.raises(ValueError, match='Duplicate marker "1"'):
            diff_documents(old_doc, new_doc)


class TestDiffContentSimilarity:
    """Test content similarity calculation."""

    def test_content_similarity_calculation(self):
        """Test similarity scoring function."""
        from yaml_diffs.diff import _calculate_content_similarity

        # Identical content
        assert _calculate_content_similarity("hello world", "hello world") == 1.0

        # No similarity
        assert _calculate_content_similarity("hello", "world") == 0.0

        # Partial similarity
        similarity = _calculate_content_similarity("hello world test", "hello world")
        assert 0.5 < similarity < 1.0

        # Empty content
        assert _calculate_content_similarity("", "") == 1.0
        assert _calculate_content_similarity("hello", "") == 0.0


class TestDiffDeeplyNested:
    """Test diffing deeply nested structures."""

    def test_diff_deeply_nested_structures(self, minimal_document: Document):
        """Test diff deeply nested structures (5+ levels)."""
        # Create 6 levels deep
        level6 = Section(id="l6", marker="6", content="Level 6")
        level5 = Section(id="l5", marker="5", content="Level 5", sections=[level6])
        level4 = Section(id="l4", marker="4", content="Level 4", sections=[level5])
        level3 = Section(id="l3", marker="3", content="Level 3", sections=[level4])
        level2 = Section(id="l2", marker="2", content="Level 2", sections=[level3])
        level1 = Section(id="l1", marker="1", content="Level 1", sections=[level2])

        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[level1],
        )

        # Change content at level 6
        new_level6 = Section(id="l6", marker="6", content="Level 6 Changed")
        new_level5 = Section(id="l5", marker="5", content="Level 5", sections=[new_level6])
        new_level4 = Section(id="l4", marker="4", content="Level 4", sections=[new_level5])
        new_level3 = Section(id="l3", marker="3", content="Level 3", sections=[new_level4])
        new_level2 = Section(id="l2", marker="2", content="Level 2", sections=[new_level3])
        new_level1 = Section(id="l1", marker="1", content="Level 1", sections=[new_level2])

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[new_level1],
        )

        diff = diff_documents(old_doc, new_doc)

        content_changes = [c for c in diff.changes if c.change_type == ChangeType.CONTENT_CHANGED]
        assert len(content_changes) == 1
        assert content_changes[0].marker == "6"
        assert len(content_changes[0].old_marker_path) == 6


class TestDiffBugFixes:
    """Test fixes for specific bugs."""

    def test_fix_cartesian_product_moved_sections(self, minimal_document: Document):
        """Test fix for Bug 1: One-to-one matching prevents cartesian product."""
        # Create old doc with two sections having same marker "1" under different parents
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[
                Section(
                    id="chap-1",
                    marker="פרק א'",
                    content="",
                    sections=[
                        Section(id="sec-1", marker="1", content="Section 1"),
                    ],
                ),
                Section(
                    id="chap-2",
                    marker="פרק ב'",
                    content="",
                    sections=[
                        Section(id="sec-2", marker="1", content="Section 2"),  # Same marker!
                    ],
                ),
            ],
        )

        # Create new doc with two sections having same marker "1" under different parents
        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[
                Section(
                    id="chap-3",
                    marker="פרק ג'",
                    content="",
                    sections=[
                        Section(id="sec-1", marker="1", content="Section 1"),  # Moved
                    ],
                ),
                Section(
                    id="chap-4",
                    marker="פרק ד'",
                    content="",
                    sections=[
                        Section(id="sec-2", marker="1", content="Section 2"),  # Moved, same marker!
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        # Should have exactly 2 MOVED entries (one-to-one matching)
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.MOVED]
        assert len(moved_changes) == 2
        assert diff.moved_count == 2

        # Verify markers are correct
        markers = {c.marker for c in moved_changes}
        assert markers == {"1"}

    def test_fix_moved_section_with_title_change(self, minimal_document: Document):
        """Test fix for Bug 2: Moved sections with title change should have both MOVED and RENAMED."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[
                Section(
                    id="chap-1",
                    marker="פרק א'",
                    content="",
                    sections=[
                        Section(
                            id="sec-1",
                            marker="1",
                            content="Same content",
                            title="Old Title",
                        ),
                    ],
                ),
            ],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[
                Section(
                    id="chap-2",
                    marker="פרק ב'",
                    content="",
                    sections=[
                        Section(
                            id="sec-1",
                            marker="1",
                            content="Same content",  # Same content
                            title="New Title",  # Title changed
                        ),  # Moved + Renamed
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        # Should have both MOVED and RENAMED
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.MOVED]
        renamed_changes = [c for c in diff.changes if c.change_type == ChangeType.RENAMED]

        assert len(moved_changes) == 1
        assert len(renamed_changes) == 1
        assert diff.moved_count == 1
        assert diff.modified_count == 1  # RENAMED counts as modified

        # Verify the renamed entry has correct title info
        assert renamed_changes[0].old_title == "Old Title"
        assert renamed_changes[0].new_title == "New Title"
        assert renamed_changes[0].old_content is None  # Not included for rename
        assert renamed_changes[0].new_content is None


class TestDiffIntegration:
    """Integration tests with example documents."""

    def test_diff_example_documents(self):
        """Test diff two versions of example document."""
        from yaml_diffs.loader import load_document

        doc1 = load_document("examples/document_v1.yaml")
        doc2 = load_document("examples/document_v2.yaml")

        diff = diff_documents(doc1, doc2)

        # Should detect various changes
        assert len(diff.changes) > 0

        # Check for expected change types
        change_types = {c.change_type for c in diff.changes}
        assert ChangeType.ADDED in change_types
        assert ChangeType.CONTENT_CHANGED in change_types
        assert ChangeType.RENAMED in change_types

    def test_diff_format_matches_expected(self, minimal_document: Document):
        """Test verify diff output format matches expected structure."""
        old_doc = Document(
            id=minimal_document.id,
            title=minimal_document.title,
            type=minimal_document.type,
            version=minimal_document.version,
            source=minimal_document.source,
            sections=[Section(id="sec-1", marker="1", content="Content")],
        )

        new_doc = Document(
            id=old_doc.id,
            title=old_doc.title,
            type=old_doc.type,
            version=old_doc.version,
            source=old_doc.source,
            sections=[Section(id="sec-1", marker="1", content="Changed")],
        )

        diff = diff_documents(old_doc, new_doc)

        # Verify DocumentDiff structure
        assert isinstance(diff, DocumentDiff)
        assert isinstance(diff.changes, list)
        assert isinstance(diff.added_count, int)
        assert isinstance(diff.deleted_count, int)
        assert isinstance(diff.modified_count, int)
        assert isinstance(diff.moved_count, int)

        # Verify DiffResult structure
        if diff.changes:
            change = diff.changes[0]
            assert isinstance(change, DiffResult)
            assert isinstance(change.section_id, str)
            assert isinstance(change.change_type, ChangeType)
            assert isinstance(change.marker, str)
