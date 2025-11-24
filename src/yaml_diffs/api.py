"""Main library API for yaml-diffs.

This module provides a clean, intuitive interface to the yaml-diffs library.
It re-exports core functions and provides convenience functions for common workflows.

Quick Start:
    >>> from yaml_diffs import api
    >>>
    >>> # Load and validate a document
    >>> doc = api.load_and_validate("examples/minimal_document.yaml")
    >>>
    >>> # Diff two documents
    >>> diff = api.diff_files("old.yaml", "new.yaml")
    >>>
    >>> # Diff and format in one call
    >>> json_diff = api.diff_and_format("old.yaml", "new.yaml", output_format="json")

Common Use Cases:
    1. Load a document: `load_document(file_path)`
    2. Validate a document: `validate_document(file_path)`
    3. Diff two documents: `diff_documents(old_doc, new_doc)`
    4. Format diff results: `format_diff(diff, output_format="json")`
    5. Complete workflow: `diff_and_format(old_file, new_file)`

For more details, see the individual function docstrings or the full API documentation.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional, TextIO

# Re-export main functions from existing modules
from yaml_diffs.diff import diff_documents

# Re-export types
from yaml_diffs.diff_types import ChangeType, DiffResult, DocumentDiff
from yaml_diffs.exceptions import (
    OpenSpecValidationError,
    PydanticValidationError,
    ValidationError,
    YAMLLoadError,
)
from yaml_diffs.formatters import format_diff
from yaml_diffs.loader import load_document
from yaml_diffs.models import Document, Section
from yaml_diffs.validator import validate_document

if TYPE_CHECKING:
    from collections.abc import Sequence


def load_and_validate(file_path: str | Path | TextIO) -> Document:
    """Load and validate a document in one call.

    This is a convenience function that simply calls `validate_document()`.
    It provides a more intuitive name for the common workflow of loading and
    validating a document in a single step.

    Note: This function is functionally identical to `validate_document()`.
    It loads a YAML file and validates it against both the OpenSpec schema
    and Pydantic models.

    Args:
        file_path: Path to YAML file (str or Path) or file-like object (TextIO).

    Returns:
        Document instance created from the validated YAML data.

    Raises:
        YAMLLoadError: If the file cannot be read or parsed.
        ImportError: If jsonschema is not available.
        OpenSpecValidationError: If OpenSpec validation fails.
        PydanticValidationError: If Pydantic validation fails.

    Examples:
        >>> doc = load_and_validate("examples/minimal_document.yaml")
        >>> assert isinstance(doc, Document)
        >>> assert doc.id == "test-123"

        >>> with open("document.yaml") as f:
        ...     doc = load_and_validate(f)
    """
    return validate_document(file_path)


def diff_files(
    old_file: str | Path | TextIO,
    new_file: str | Path | TextIO,
) -> DocumentDiff:
    """Load and diff two document files.

    This is a convenience function that loads two YAML files and compares them.
    It combines `load_document()` and `diff_documents()` into a single call.

    Args:
        old_file: Path to old document version (str or Path) or file-like object (TextIO).
        new_file: Path to new document version (str or Path) or file-like object (TextIO).

    Returns:
        DocumentDiff containing all detected changes between the two documents.

    Raises:
        YAMLLoadError: If either file cannot be read or parsed.
        PydanticValidationError: If either document fails Pydantic validation.
        ValueError: If duplicate markers found at same level in either document.

    Examples:
        >>> diff = diff_files("examples/document_v1.yaml", "examples/document_v2.yaml")
        >>> assert isinstance(diff, DocumentDiff)
        >>> print(f"Added: {diff.added_count}, Removed: {diff.deleted_count}")

        >>> with open("old.yaml") as old_f, open("new.yaml") as new_f:
        ...     diff = diff_files(old_f, new_f)
    """
    old_doc = load_document(old_file)
    new_doc = load_document(new_file)
    return diff_documents(old_doc, new_doc)


def diff_and_format(
    old_file: str | Path | TextIO,
    new_file: str | Path | TextIO,
    output_format: str = "json",
    filter_change_types: Optional[Sequence[ChangeType]] = None,
    filter_section_path: Optional[str] = None,
    **kwargs,
) -> str:
    """Load, diff, and format two documents in one call.

    This is a convenience function that combines `diff_files()` and `format_diff()`
    into a single call. It loads two YAML files, compares them, and returns the
    formatted diff result.

    Args:
        old_file: Path to old document version (str or Path) or file-like object (TextIO).
        new_file: Path to new document version (str or Path) or file-like object (TextIO).
        output_format: Output format ("json", "text", or "yaml", default: "json").
        filter_change_types: Optional sequence of change types to include in output.
            Accepts both `list` and `tuple` (any `Sequence[ChangeType]`).
        filter_section_path: Optional marker path to filter by (exact match).
        **kwargs: Additional formatter-specific options (e.g., `indent` for JSON formatter).

    Returns:
        Formatted string representation of the diff.

    Raises:
        YAMLLoadError: If either file cannot be read or parsed.
        PydanticValidationError: If either document fails Pydantic validation.
        ValueError: If duplicate markers found at same level in either document,
            or if output_format is not one of "json", "text", or "yaml".

    Examples:
        >>> json_diff = diff_and_format("old.yaml", "new.yaml", output_format="json")
        >>> print(json_diff)

        >>> text_diff = diff_and_format(
        ...     "old.yaml",
        ...     "new.yaml",
        ...     output_format="text",
        ...     filter_change_types=[ChangeType.CONTENT_CHANGED],
        ... )
        >>> print(text_diff)

        >>> yaml_diff = diff_and_format(
        ...     "old.yaml",
        ...     "new.yaml",
        ...     output_format="yaml",
        ...     indent=2,
        ... )
    """
    diff = diff_files(old_file, new_file)
    return format_diff(
        diff,
        output_format=output_format,
        filter_change_types=filter_change_types,
        filter_section_path=filter_section_path,
        **kwargs,
    )


__all__ = [
    # Main functions
    "load_document",
    "validate_document",
    "diff_documents",
    "format_diff",
    # Convenience functions
    "load_and_validate",
    "diff_files",
    "diff_and_format",
    # Exceptions
    "YAMLLoadError",
    "ValidationError",
    "OpenSpecValidationError",
    "PydanticValidationError",
    # Types
    "Document",
    "Section",
    "DocumentDiff",
    "DiffResult",
    "ChangeType",
]
