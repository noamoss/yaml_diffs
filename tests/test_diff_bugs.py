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
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.MOVED]
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

        # Should have both MOVED and RENAMED
        moved_changes = [c for c in diff.changes if c.change_type == ChangeType.MOVED]
        renamed_changes = [c for c in diff.changes if c.change_type == ChangeType.RENAMED]

        assert len(moved_changes) == 1, f"Expected 1 MOVED change, got {len(moved_changes)}"
        assert len(renamed_changes) == 1, f"Expected 1 RENAMED change, got {len(renamed_changes)}"
        assert diff.moved_count == 1
        assert diff.modified_count == 1  # RENAMED counts as modified

        # Verify the RENAMED change has correct title info
        assert renamed_changes[0].old_title == "Old Title"
        assert renamed_changes[0].new_title == "New Title"
