"""Document diffing engine using marker-based matching."""

from __future__ import annotations

from typing import Optional

from yaml_diffs.diff_types import ChangeType, DiffResult, DocumentDiff
from yaml_diffs.models import Document, Section


def _validate_unique_markers(
    sections: list[Section],
    parent_path: tuple[str, ...] = (),
) -> None:
    """Validate no duplicate markers at same nesting level.

    Recursively validates that no two sections at the same nesting level
    have the same marker. Raises ValueError if duplicates are found.

    Args:
        sections: List of sections to validate
        parent_path: Tuple of parent markers from root (for error messages)

    Raises:
        ValueError: If duplicate markers found at same level

    Examples:
        >>> section1 = Section(id="1", marker="1", content="")
        >>> section2 = Section(id="2", marker="1", content="")  # Duplicate!
        >>> _validate_unique_markers([section1, section2])
        ValueError: Duplicate marker "1" found at path ()
    """
    seen_markers: set[str] = set()
    for section in sections:
        if section.marker in seen_markers:
            path_str = " -> ".join(parent_path) if parent_path else "root"
            raise ValueError(f'Duplicate marker "{section.marker}" found at path: {path_str}')
        seen_markers.add(section.marker)

        # Recursively validate nested sections
        if section.sections:
            new_path = parent_path + (section.marker,)
            _validate_unique_markers(section.sections, new_path)


def _build_marker_map(
    sections: list[Section],
    parent_marker_path: tuple[str, ...] = (),
    parent_id_path: Optional[list[str]] = None,
) -> dict:
    """Build marker+path -> section mapping.

    Recursively traverses sections and builds a mapping from
    (marker, parent_marker_path) to (Section, marker_path, id_path).

    Args:
        sections: List of sections to map
        parent_marker_path: Tuple of parent markers from root
        parent_id_path: List of parent IDs from root (for tracking)

    Returns:
        Dictionary mapping (marker, parent_marker_path) to
        (Section, marker_path_tuple, id_path_list)

    Examples:
        >>> section = Section(id="sec-1", marker="1", content="")
        >>> mapping = _build_marker_map([section])
        >>> key = ("1", ())
        >>> assert key in mapping
    """
    if parent_id_path is None:
        parent_id_path = []

    mapping: dict = {}

    for section in sections:
        # Create key: (marker, parent_marker_path)
        key = (section.marker, parent_marker_path)

        # Create paths
        marker_path = parent_marker_path + (section.marker,)
        id_path = parent_id_path + [section.id]

        # Store mapping
        mapping[key] = (section, marker_path, id_path)

        # Recursively process nested sections
        if section.sections:
            nested_mapping = _build_marker_map(section.sections, marker_path, id_path)
            mapping.update(nested_mapping)

    return mapping


def _calculate_content_similarity(content1: str, content2: str) -> float:
    """Calculate similarity score between two content strings.

    Uses simple word overlap to calculate similarity.
    Returns a value between 0.0 (no similarity) and 1.0 (identical).

    Args:
        content1: First content string
        content2: Second content string

    Returns:
        Similarity score between 0.0 and 1.0

    Examples:
        >>> _calculate_content_similarity("hello world", "hello world")
        1.0
        >>> _calculate_content_similarity("hello", "world")
        0.0
    """
    if not content1 and not content2:
        return 1.0
    if not content1 or not content2:
        return 0.0

    # Simple word-based similarity
    words1 = set(content1.split())
    words2 = set(content2.split())

    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    if not union:
        return 1.0

    return len(intersection) / len(union)


def _find_moved_sections(
    unmatched_old: dict,
    unmatched_new: dict,
) -> list:
    """Find sections that moved (same marker, different path).

    Matches sections by marker only (ignoring path) to detect movements.
    Uses one-to-one matching to avoid cartesian product issues when multiple
    sections share the same marker.

    Args:
        unmatched_old: Dictionary of unmatched sections from old document
        unmatched_new: Dictionary of unmatched sections from new document

    Returns:
        List of (old_key, new_key) pairs for moved sections

    Examples:
        >>> old_key = ("1", ("פרק א'",))
        >>> new_key = ("1", ("פרק ב'",))
        >>> matches = _find_moved_sections({old_key: ...}, {new_key: ...})
        >>> assert (old_key, new_key) in matches
    """
    matches: list = []

    # Build marker -> keys mapping for new document
    marker_to_new_keys: dict = {}
    for new_key in unmatched_new.keys():
        marker = new_key[0]
        if marker not in marker_to_new_keys:
            marker_to_new_keys[marker] = []
        marker_to_new_keys[marker].append(new_key)

    # Find matches by marker (one-to-one matching)
    # BUG FIX: Use .pop(0) to ensure one-to-one matching and prevent cartesian product
    # when multiple old sections share the same marker with multiple new sections.
    # Without this fix, if 2 old sections with marker "1" match 2 new sections with
    # marker "1", all 4 pairings would be created instead of 2 one-to-one matches.
    for old_key in list(unmatched_old.keys()):
        old_marker = old_key[0]
        if old_marker in marker_to_new_keys and marker_to_new_keys[old_marker]:
            # Found a match by marker (different path = moved)
            # Take the first available new_key with this marker (one-to-one)
            # Using .pop(0) removes it from the list, preventing duplicate matches
            new_key = marker_to_new_keys[old_marker].pop(0)
            matches.append((old_key, new_key))

            # Remove from unmatched_new to avoid duplicate matches
            if new_key in unmatched_new:
                del unmatched_new[new_key]

            # Remove from unmatched_old
            if old_key in unmatched_old:
                del unmatched_old[old_key]

            # Clean up empty lists
            if not marker_to_new_keys[old_marker]:
                del marker_to_new_keys[old_marker]

    return matches


def diff_documents(old: Document, new: Document) -> DocumentDiff:
    """Compare two Document versions and detect changes.

    Uses marker-based matching to detect additions, deletions, content changes,
    movements, and renames. Validates that markers are unique at each level.

    Args:
        old: Old document version
        new: New document version

    Returns:
        DocumentDiff containing all detected changes

    Raises:
        ValueError: If duplicate markers found at same level in either document

    Examples:
        >>> old_doc = Document(...)
        >>> new_doc = Document(...)
        >>> diff = diff_documents(old_doc, new_doc)
        >>> assert isinstance(diff, DocumentDiff)
    """
    # Validate unique markers in both documents
    _validate_unique_markers(old.sections)
    _validate_unique_markers(new.sections)

    # Build marker maps for both documents
    old_map = _build_marker_map(old.sections)
    new_map = _build_marker_map(new.sections)

    changes: list[DiffResult] = []

    # Find exact matches (same marker + same parent path)
    exact_matches: set[tuple[str, tuple[str, ...]]] = set()
    for key in old_map.keys() & new_map.keys():
        exact_matches.add(key)
        old_section, old_marker_path, old_id_path = old_map[key]
        new_section, new_marker_path, new_id_path = new_map[key]

        # Check for content change
        if old_section.content != new_section.content:
            changes.append(
                DiffResult(
                    section_id=old_section.id,
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker=old_section.marker,
                    old_marker_path=old_marker_path,
                    new_marker_path=new_marker_path,
                    old_id_path=old_id_path,
                    new_id_path=new_id_path,
                    old_content=old_section.content,
                    new_content=new_section.content,
                )
            )

        # Check for title change (rename)
        if old_section.title != new_section.title:
            # Only mark as renamed if content is the same
            if old_section.content == new_section.content:
                changes.append(
                    DiffResult(
                        section_id=old_section.id,
                        change_type=ChangeType.RENAMED,
                        marker=old_section.marker,
                        old_marker_path=old_marker_path,
                        new_marker_path=new_marker_path,
                        old_id_path=old_id_path,
                        new_id_path=new_id_path,
                        old_title=old_section.title,
                        new_title=new_section.title,
                    )
                )
            # If content also changed, title change is part of content change
            # (already handled above)

        # No changes detected
        if old_section.content == new_section.content and old_section.title == new_section.title:
            changes.append(
                DiffResult(
                    section_id=old_section.id,
                    change_type=ChangeType.UNCHANGED,
                    marker=old_section.marker,
                    old_marker_path=old_marker_path,
                    new_marker_path=new_marker_path,
                    old_id_path=old_id_path,
                    new_id_path=new_id_path,
                )
            )

    # Find unmatched sections (for movement detection)
    unmatched_old = {k: v for k, v in old_map.items() if k not in exact_matches}
    unmatched_new = {k: v for k, v in new_map.items() if k not in exact_matches}

    # Find moved sections (same marker, different path)
    moved_matches = _find_moved_sections(unmatched_old, unmatched_new)

    for old_key, new_key in moved_matches:
        old_section, old_marker_path, old_id_path = old_map[old_key]
        new_section, new_marker_path, new_id_path = new_map[new_key]

        # Check if content also changed
        content_similarity = _calculate_content_similarity(old_section.content, new_section.content)
        content_changed = old_section.content != new_section.content

        # Add MOVED change
        changes.append(
            DiffResult(
                section_id=old_section.id,
                change_type=ChangeType.MOVED,
                marker=old_section.marker,
                old_marker_path=old_marker_path,
                new_marker_path=new_marker_path,
                old_id_path=old_id_path,
                new_id_path=new_id_path,
            )
        )

        # BUG FIX: Check for title change (rename) when content is unchanged.
        # Moved sections with title changes should record both MOVED and RENAMED
        # to be consistent with non-moved sections. This ensures title change
        # information is not lost when a section moves.
        title_changed = old_section.title != new_section.title
        if title_changed and old_section.content == new_section.content:
            changes.append(
                DiffResult(
                    section_id=old_section.id,
                    change_type=ChangeType.RENAMED,
                    marker=old_section.marker,
                    old_marker_path=old_marker_path,
                    new_marker_path=new_marker_path,
                    old_id_path=old_id_path,
                    new_id_path=new_id_path,
                    old_title=old_section.title,
                    new_title=new_section.title,
                )
            )

        # If content changed and similarity is high (>80%) with same title,
        # also add CONTENT_CHANGED
        if content_changed and content_similarity >= 0.8 and old_section.title == new_section.title:
            changes.append(
                DiffResult(
                    section_id=old_section.id,
                    change_type=ChangeType.CONTENT_CHANGED,
                    marker=old_section.marker,
                    old_marker_path=old_marker_path,
                    new_marker_path=new_marker_path,
                    old_id_path=old_id_path,
                    new_id_path=new_id_path,
                    old_content=old_section.content,
                    new_content=new_section.content,
                )
            )

    # Remaining unmatched sections
    # Old only -> DELETED
    for _old_key, (old_section, old_marker_path, old_id_path) in unmatched_old.items():
        changes.append(
            DiffResult(
                section_id=old_section.id,
                change_type=ChangeType.DELETED,
                marker=old_section.marker,
                old_marker_path=old_marker_path,
                old_id_path=old_id_path,
                old_content=old_section.content,
                old_title=old_section.title,
            )
        )

    # New only -> ADDED
    for _new_key, (new_section, new_marker_path, new_id_path) in unmatched_new.items():
        changes.append(
            DiffResult(
                section_id=new_section.id,
                change_type=ChangeType.ADDED,
                marker=new_section.marker,
                new_marker_path=new_marker_path,
                new_id_path=new_id_path,
                new_content=new_section.content,
                new_title=new_section.title,
            )
        )

    # Calculate counts
    added_count = sum(1 for c in changes if c.change_type == ChangeType.ADDED)
    deleted_count = sum(1 for c in changes if c.change_type == ChangeType.DELETED)
    modified_count = sum(
        1 for c in changes if c.change_type in (ChangeType.CONTENT_CHANGED, ChangeType.RENAMED)
    )
    moved_count = sum(1 for c in changes if c.change_type == ChangeType.MOVED)

    return DocumentDiff(
        changes=changes,
        added_count=added_count,
        deleted_count=deleted_count,
        modified_count=modified_count,
        moved_count=moved_count,
    )
