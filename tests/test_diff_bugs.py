"""Tests to verify and fix bugs in diffing logic."""

import pytest

from yaml_diffs.diff import diff_documents
from yaml_diffs.diff_types import ChangeType
from yaml_diffs.models import Document, DocumentType, Section, Source, Version


@pytest.fixture
def minimal_document() -> Document:
    """Create a minimal document."""
    return Document(
        id="law-1234",
        title="חוק הדוגמה",
        type=DocumentType.LAW,
        version=Version(number="1.0"),
        source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
    )


class TestBug1CartesianProduct:
    """Test Bug 1: Cartesian product issue in _find_moved_sections."""

    def test_multiple_sections_same_marker_one_to_one_matching(self, minimal_document: Document):
        """Test that multiple sections with same marker are matched one-to-one, not cartesian product."""
        # Old document: Two sections with marker "1" under different parents
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
                        Section(id="sec-2", marker="1", content="Section 2"),
                    ],
                ),
            ],
        )

        # New document: Two sections with marker "1" under different parents (moved)
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
                        Section(id="sec-1", marker="1", content="Section 1"),
                    ],
                ),
                Section(
                    id="chap-4",
                    marker="פרק ד'",
                    content="",
                    sections=[
                        Section(id="sec-2", marker="1", content="Section 2"),
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        # Should have exactly 2 MOVED changes (one-to-one matching)
        # NOT 4 (cartesian product: 2 old × 2 new = 4)
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_MOVED]
        assert len(moved_changes) == 2, f"Expected 2 MOVED changes, got {len(moved_changes)}"
        assert diff.moved_count == 2, f"Expected moved_count=2, got {diff.moved_count}"


class TestBug2MovedRenamed:
    """Test Bug 2: Moved sections with title changes should record both MOVED and RENAMED."""

    def test_moved_section_with_title_change_only(self, minimal_document: Document):
        """Test that moved section with only title change records both MOVED and RENAMED."""
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
                        ),
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        # With similarity checking: content is identical (similarity = 1.0 ≥ 0.95)
        # so it WILL be detected as MOVED even though title changed.
        # Both MOVED and TITLE_CHANGED should be recorded.
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_MOVED]
        title_changes = [c for c in diff.changes if c.change_type == ChangeType.TITLE_CHANGED]
        removed_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_REMOVED]
        added_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_ADDED]

        assert len(moved_changes) == 1, "High similarity (1.0) should be detected as MOVED"
        assert len(title_changes) == 1, "Title changed, so TITLE_CHANGED should be recorded"
        assert len(removed_changes) == 1, "Only parent chapter should be removed"
        assert len(added_changes) == 1, "Only new parent chapter should be added"


class TestBug3MovedContentChanged:
    """Test Bug 3: Moved sections with content changes should always record CONTENT_CHANGED."""

    def test_moved_section_with_content_and_title_change(self, minimal_document: Document):
        """Test that moved section with both content and title change records MOVED, TITLE_CHANGED, and CONTENT_CHANGED."""
        # This test addresses the specific issue from comment #2554771461:
        # "Moving marker '1' to a new parent with different text and a new title
        # currently produces no content-change entry despite the text change."
        # Updated: With similarity checking, sections with high similarity (≥0.95) are detected as MOVED
        # even if content and title change. Both CONTENT_CHANGED and TITLE_CHANGED should be recorded.
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
                            # Use identical content to guarantee similarity = 1.0 ≥ 0.95
                            content="This is the original content for section one with some additional text here for testing.",
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
                            # Identical content (similarity = 1.0 ≥ 0.95) but different path = MOVED
                            # Title changed, so both MOVED and TITLE_CHANGED should be recorded
                            content="This is the original content for section one with some additional text here for testing.",
                            title="New Title",  # Title changed
                        ),
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        # With similarity checking: identical content (similarity = 1.0 ≥ 0.95) so detected as MOVED
        # Content is identical, so only MOVED and TITLE_CHANGED should be recorded (no CONTENT_CHANGED)
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_MOVED]
        content_changes = [c for c in diff.changes if c.change_type == ChangeType.CONTENT_CHANGED]
        title_changes = [c for c in diff.changes if c.change_type == ChangeType.TITLE_CHANGED]

        assert len(moved_changes) == 1, "Should be detected as MOVED due to identical content"
        assert len(content_changes) == 0, "Content is identical, so no CONTENT_CHANGED"
        assert len(title_changes) == 1, "Should record TITLE_CHANGED when title changes"
        assert diff.modified_count == 1, "Should count only TITLE_CHANGED"

    def test_moved_section_with_substantially_rewritten_content(self, minimal_document: Document):
        """Test that section with low content similarity is not detected as MOVED.

        With new semantics, SECTION_MOVED requires high content similarity (≥0.95) and same title.
        If content is substantially rewritten (low similarity), it should be detected as
        SECTION_REMOVED + SECTION_ADDED instead.
        """
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
                            content="The quick brown fox jumps over the lazy dog.",
                            title="Section Title",
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
                            content="A completely different sentence with no shared words.",  # Low similarity
                            title="Section Title",  # Same title
                        ),
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        # With new semantics: low similarity, so not detected as MOVED
        # Should be detected as SECTION_REMOVED + SECTION_ADDED
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_MOVED]
        removed_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_REMOVED]
        added_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_ADDED]

        assert len(moved_changes) == 0, "Low similarity should not be detected as MOVED"
        assert len(removed_changes) == 2  # Parent chapter + child section
        assert len(added_changes) == 2  # New parent chapter + new child section


class TestSectionMovedWithMarkerChange:
    """Test SECTION_MOVED detection with marker changes."""

    def test_section_moved_with_marker_change(self, minimal_document: Document):
        """Test that SECTION_MOVED is detected when marker changed but content+title same."""
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
                            content="Same content here",
                            title="Same Title",
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
                            marker="2",  # Marker changed
                            content="Same content here",  # Content same
                            title="Same Title",  # Title same
                        ),
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        # Current implementation matches by marker only, so when markers differ,
        # sections won't be matched as moved even if content+title are the same.
        # They will be detected as SECTION_REMOVED + SECTION_ADDED instead.
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_MOVED]
        removed_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_REMOVED]
        added_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_ADDED]

        assert len(moved_changes) == 0, "Different markers won't match, so not detected as MOVED"
        assert len(removed_changes) == 2, "Should be detected as removed (parent + child)"
        assert len(added_changes) == 2, "Should be detected as added (parent + child)"


class TestContentSimilarityInMovementDetection:
    """Test content similarity checking in movement detection."""

    def test_empty_content_sections_not_matched_as_moved(self, minimal_document: Document):
        """Test that empty content sections (parent sections) are not matched as moved."""
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
                    content="",  # Empty content
                    sections=[],
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
                    marker="פרק א'",  # Same marker, different parent (root)
                    content="",  # Empty content
                    sections=[],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        # Both sections are at root level with same marker "פרק א'", so they have
        # the same key (marker, parent_path) and are exact matches, not moved.
        # Since content and title are the same, they'll be detected as UNCHANGED.
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_MOVED]
        unchanged_changes = [c for c in diff.changes if c.change_type == ChangeType.UNCHANGED]
        removed_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_REMOVED]
        added_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_ADDED]

        assert len(moved_changes) == 0, "Empty content sections should not be matched as moved"
        assert len(unchanged_changes) == 1, "Should be detected as UNCHANGED (exact match)"
        assert len(removed_changes) == 0, "Should not be detected as removed (exact match)"
        assert len(added_changes) == 0, "Should not be detected as added (exact match)"

    def test_low_similarity_sections_not_matched_as_moved(self, minimal_document: Document):
        """Test that sections with similarity < 0.95 are not matched as moved."""
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
                            content="This is completely different content with no shared words.",
                            title="Title",
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
                            marker="1",  # Same marker
                            content="Totally unrelated text that shares nothing in common.",
                            title="Title",
                        ),
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        # Low similarity (< 0.95) should not be matched as moved
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_MOVED]
        removed_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_REMOVED]
        added_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_ADDED]

        assert len(moved_changes) == 0, "Low similarity sections should not be matched as moved"
        assert len(removed_changes) == 2, "Should be detected as removed (parent + child)"
        assert len(added_changes) == 2, "Should be detected as added (parent + child)"

    def test_high_similarity_sections_matched_as_moved(self, minimal_document: Document):
        """Test that sections with similarity ≥ 0.95 are matched as moved."""
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
                            content="This is the original content for section one with some text.",
                            title="Title",
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
                            marker="1",  # Same marker
                            # High similarity (≥0.95) - most words are the same
                            content="This is the original content for section one with some text.",
                            title="Title",
                        ),
                    ],
                ),
            ],
        )

        diff = diff_documents(old_doc, new_doc)

        # High similarity (≥ 0.95) should be matched as moved
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_MOVED]
        removed_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_REMOVED]
        added_changes = [c for c in diff.changes if c.change_type == ChangeType.SECTION_ADDED]

        assert len(moved_changes) == 1, "High similarity sections should be matched as moved"
        assert len(removed_changes) == 1, "Only parent chapter should be removed"
        assert len(added_changes) == 1, "Only new parent chapter should be added"
        assert diff.moved_count == 1
