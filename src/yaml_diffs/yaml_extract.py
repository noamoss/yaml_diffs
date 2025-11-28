"""YAML extraction utilities for finding sections and line numbers."""

from __future__ import annotations

import yaml  # type: ignore[import-untyped]

from yaml_diffs.models import Section


def find_section_by_marker_path(
    sections: list[Section],
    marker_path: tuple[str, ...],
) -> Section | None:
    """Find a section by following a marker path.

    Args:
        sections: List of sections to search in
        marker_path: Tuple of markers representing the path from root

    Returns:
        The found section, or None if not found

    Examples:
        >>> section = Section(id="1", marker="1", content="")
        >>> found = find_section_by_marker_path([section], ("1",))
        >>> assert found == section
    """
    if not marker_path:
        return None

    current_sections = sections
    current_path = list(marker_path)

    while current_path:
        target_marker = current_path.pop(0)
        found_section = None

        for section in current_sections:
            if section.marker == target_marker:
                found_section = section
                break

        if not found_section:
            return None

        # If we've reached the end of the path, return this section
        if not current_path:
            return found_section

        # Otherwise, continue navigating into nested sections
        if not found_section.sections:
            return None  # Path continues but no nested sections

        current_sections = found_section.sections

    return None


def section_to_yaml_dict(section: Section) -> dict:
    """Convert a Section to a dictionary suitable for YAML serialization.

    Args:
        section: The section to convert

    Returns:
        Dictionary representation of the section
    """
    result: dict = {
        "id": section.id,
        "marker": section.marker,
    }

    if section.title is not None:
        result["title"] = section.title

    if section.content:
        result["content"] = section.content

    if section.sections:
        result["sections"] = [section_to_yaml_dict(s) for s in section.sections]
    else:
        result["sections"] = []

    return result


def find_section_line_number(
    yaml_text: str,
    marker_path: tuple[str, ...],
) -> int | None:
    """Find the starting line number of a section in YAML text by marker path.

    Args:
        yaml_text: The full YAML document as a string
        marker_path: Tuple of markers representing the path to the section

    Returns:
        The line number (1-indexed) where the section starts, or None if not found
    """
    if not marker_path or not yaml_text:
        return None

    try:
        lines = yaml_text.split("\n")
        current_path: list[str] = []
        section_stack: list[tuple[str, int, int]] = []  # (marker, indent, line_number)
        document_indent = -1
        sections_indent = -1

        for i, line in enumerate(lines):
            trimmed = line.strip()

            # Skip empty lines and comments
            if not trimmed or trimmed.startswith("#"):
                continue

            indent = len(line) - len(line.lstrip())

            # Find document: entry
            if trimmed.startswith("document:") or trimmed == "document:":
                document_indent = indent
                continue

            # Find the TOP-LEVEL sections: entry point (only directly under document, set once)
            if (
                sections_indent < 0
                and document_indent >= 0
                and (trimmed == "sections:" or trimmed.startswith("sections:"))
            ):
                if indent > document_indent:
                    sections_indent = indent
                    continue

            # Process sections
            if sections_indent >= 0 and indent > sections_indent:
                # Look for marker field
                if trimmed.startswith("marker:"):
                    # Extract marker value - handle both quoted and unquoted
                    marker_part = trimmed[7:].strip()  # "marker:" is 7 chars

                    if marker_part:
                        # Remove quotes if present
                        marker = marker_part
                        if (marker.startswith('"') and marker.endswith('"')) or (
                            marker.startswith("'") and marker.endswith("'")
                        ):
                            marker = marker[1:-1]
                            # Handle escaped quotes
                            if marker_part[0] == '"':
                                marker = (
                                    marker.replace('\\"', '"')
                                    .replace("\\n", "\n")
                                    .replace("\\\\", "\\")
                                )
                            elif marker_part[0] == "'":
                                marker = marker.replace("''", "'")

                        # Pop stack until we find the right parent level
                        while section_stack and indent <= section_stack[-1][1]:
                            section_stack.pop()
                            if current_path:
                                current_path.pop()

                        # Add this section to the path
                        section_stack.append((marker, indent, i + 1))
                        current_path.append(marker)

                        # Check if this matches our target path
                        if len(current_path) == len(marker_path):
                            matches = True
                            for j, target_marker in enumerate(marker_path):
                                current_marker = current_path[j]
                                if current_marker != target_marker:
                                    matches = False
                                    break

                            if matches:
                                # Found it! Look backwards for the section start (the "-" line)
                                max_lookback = max(0, i - 20)
                                for k in range(i, max_lookback - 1, -1):
                                    prev_line = lines[k]
                                    prev_trimmed = prev_line.strip()

                                    if prev_trimmed.startswith("-"):
                                        prev_indent = len(prev_line) - len(prev_line.lstrip())
                                        # The "-" line should be less indented than the marker line
                                        if prev_indent < indent and prev_indent >= sections_indent:
                                            return k + 1  # 1-indexed

                                    if prev_trimmed and not prev_trimmed.startswith("#"):
                                        prev_indent = len(prev_line) - len(prev_line.lstrip())
                                        if k < i and prev_indent < indent - 2:
                                            break

                                # Fallback: return the marker line
                                return i + 1

    except Exception:
        # If anything goes wrong, return None
        return None

    return None


def extract_section_yaml(
    yaml_text: str,
    marker_path: tuple[str, ...],
    parsed_doc: dict | None = None,
) -> str | None:
    """Extract full YAML representation of a section by marker path.

    Handles both regular sections and metadata fields.

    Args:
        yaml_text: The full YAML document as a string
        marker_path: Tuple of markers representing the path to the section
        parsed_doc: Optional pre-parsed document dict (to avoid re-parsing)

    Returns:
        YAML string representation of the section, or None if not found
    """
    if not marker_path or not yaml_text:
        return None

    try:
        # Parse YAML if not provided
        if parsed_doc is None:
            parsed_doc = yaml.safe_load(yaml_text)
            if not parsed_doc or "document" not in parsed_doc:
                return None

        # Handle metadata paths (e.g., ("__metadata__", "version", "number"))
        if marker_path[0] == "__metadata__":
            doc = parsed_doc.get("document", {})
            if len(marker_path) == 1:
                # Just "__metadata__" - return all metadata
                metadata = {
                    "version": doc.get("version", {}),
                    "source": doc.get("source", {}),
                    "authors": doc.get("authors", []),
                    "published_date": doc.get("published_date"),
                    "updated_date": doc.get("updated_date"),
                }
                result: str = yaml.dump(
                    metadata,
                    indent=2,
                    width=1000,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )
                return result.rstrip()
            elif len(marker_path) == 2:
                # e.g., ("__metadata__", "authors")
                field_name = marker_path[1]
                value = doc.get(field_name)
                if value is not None:
                    return str(
                        yaml.dump(
                            {field_name: value},
                            indent=2,
                            width=1000,
                            allow_unicode=True,
                            default_flow_style=False,
                            sort_keys=False,
                        )
                    ).rstrip()
            elif len(marker_path) == 3:
                # e.g., ("__metadata__", "version", "number")
                parent_name = marker_path[1]
                field_name = marker_path[2]
                parent = doc.get(parent_name)
                if parent and isinstance(parent, dict):
                    value = parent.get(field_name)
                    if value is not None:
                        return str(
                            yaml.dump(
                                {parent_name: {field_name: value}},
                                indent=2,
                                width=1000,
                                allow_unicode=True,
                                default_flow_style=False,
                                sort_keys=False,
                            )
                        ).rstrip()
            return None

        # Handle regular sections
        # Navigate to the section
        doc_sections = parsed_doc.get("document", {}).get("sections", [])
        if not doc_sections:
            return None

        # Find section by path
        current_sections = doc_sections
        current_path = list(marker_path)

        while current_path:
            target_marker = current_path.pop(0)
            found_section_dict = None

            for section_dict in current_sections:
                if section_dict.get("marker") == target_marker:
                    found_section_dict = section_dict
                    break

            if not found_section_dict:
                return None

            # If we've reached the end of the path, serialize this section
            if not current_path:
                # Serialize to YAML
                return str(
                    yaml.dump(
                        found_section_dict,
                        indent=2,
                        width=1000,  # Large width to prevent wrapping
                        allow_unicode=True,
                        default_flow_style=False,
                        sort_keys=False,
                    )
                ).rstrip()

            # Otherwise, continue navigating
            current_sections = found_section_dict.get("sections", [])

    except Exception:
        return None

    return None


def find_metadata_line_number(
    yaml_text: str,
    marker_path: tuple[str, ...],
) -> int | None:
    """Find the starting line number of a metadata field in YAML text.

    Args:
        yaml_text: The full YAML document as a string
        marker_path: Tuple representing the metadata path (e.g., ("__metadata__", "version", "number"))

    Returns:
        The line number (1-indexed) where the metadata field starts, or None if not found
    """
    if not marker_path or marker_path[0] != "__metadata__" or not yaml_text:
        return None

    try:
        lines = yaml_text.split("\n")
        document_indent = -1

        # Find document: entry
        for _i, line in enumerate(lines):
            trimmed = line.strip()
            if trimmed.startswith("document:") or trimmed == "document:":
                document_indent = len(line) - len(line.lstrip())
                break

        if document_indent < 0:
            return None

        # Handle different metadata path lengths
        if len(marker_path) == 2:
            # e.g., ("__metadata__", "authors")
            field_name = marker_path[1]
            for i, line in enumerate(lines):
                trimmed = line.strip()
                indent = len(line) - len(line.lstrip())
                # Look for the field at document level
                if indent == document_indent + 2 and trimmed.startswith(f"{field_name}:"):
                    return i + 1  # 1-indexed
        elif len(marker_path) == 3:
            # e.g., ("__metadata__", "version", "number")
            parent_name = marker_path[1]
            field_name = marker_path[2]
            in_parent = False
            for i, line in enumerate(lines):
                trimmed = line.strip()
                indent = len(line) - len(line.lstrip())
                # Check if we're in the parent section
                if indent == document_indent + 2 and trimmed.startswith(f"{parent_name}:"):
                    in_parent = True
                    continue
                # Check if we're still in the parent (indented more)
                if in_parent and indent > document_indent + 2:
                    if trimmed.startswith(f"{field_name}:"):
                        return i + 1  # 1-indexed
                # If we've left the parent, stop looking
                if (
                    in_parent
                    and indent <= document_indent + 2
                    and not trimmed.startswith(f"{parent_name}:")
                ):
                    break

    except Exception:
        return None

    return None
