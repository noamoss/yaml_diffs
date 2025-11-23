"""YAML loading utilities for legal documents."""

from __future__ import annotations

from pathlib import Path
from typing import Any, TextIO

import yaml  # type: ignore[import-untyped]
from pydantic import ValidationError as PydanticValidationErrorBase

from yaml_diffs.exceptions import (
    PydanticValidationError,
    YAMLLoadError,
    format_pydantic_errors,
)
from yaml_diffs.models import Document


def load_yaml_file(file_path: str | Path) -> dict[str, Any]:
    """Load YAML file from file path.

    Opens the file with UTF-8 encoding and parses it using yaml.safe_load().
    This function handles file I/O errors and YAML parsing errors.

    Args:
        file_path: Path to the YAML file (string or Path object).

    Returns:
        Dictionary containing the parsed YAML data.

    Raises:
        YAMLLoadError: If the file cannot be read or parsed. This includes:
            - FileNotFoundError: File does not exist
            - PermissionError: Insufficient permissions to read file
            - yaml.YAMLError: Invalid YAML syntax
            - UnicodeDecodeError: Encoding issues

    Examples:
        >>> data = load_yaml_file("examples/minimal_document.yaml")
        >>> assert "document" in data
    """
    file_path_obj = Path(file_path) if isinstance(file_path, str) else file_path

    try:
        with open(file_path_obj, encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                if data is None:
                    raise YAMLLoadError(
                        f"YAML file is empty or contains only null: {file_path_obj}",
                        file_path=str(file_path_obj),
                    )
                if not isinstance(data, dict):
                    raise YAMLLoadError(
                        f"YAML file must contain a dictionary, got {type(data).__name__}: {file_path_obj}",
                        file_path=str(file_path_obj),
                    )
                return data
            except yaml.YAMLError as e:
                raise YAMLLoadError(
                    f"Failed to parse YAML file: {file_path_obj}. Error: {str(e)}",
                    original_error=e,
                    file_path=str(file_path_obj),
                ) from e
    except FileNotFoundError as e:
        raise YAMLLoadError(
            f"YAML file not found: {file_path_obj}",
            original_error=e,
            file_path=str(file_path_obj),
        ) from e
    except PermissionError as e:
        raise YAMLLoadError(
            f"Permission denied reading YAML file: {file_path_obj}",
            original_error=e,
            file_path=str(file_path_obj),
        ) from e
    except UnicodeDecodeError as e:
        raise YAMLLoadError(
            f"Failed to decode YAML file (expected UTF-8): {file_path_obj}. Error: {str(e)}",
            original_error=e,
            file_path=str(file_path_obj),
        ) from e


def load_yaml(file_like: TextIO | str) -> dict[str, Any]:
    """Load YAML from file-like object or string.

    Parses YAML content from either a file-like object (any object with a `read()`
    method) or a string. Uses yaml.safe_load() for secure parsing.

    Args:
        file_like: File-like object (any object with a `read()` method) or string
            containing YAML content.

    Returns:
        Dictionary containing the parsed YAML data.

    Raises:
        YAMLLoadError: If the YAML cannot be parsed. This includes:
            - yaml.YAMLError: Invalid YAML syntax
            - ValueError: If file_like is neither TextIO nor str

    Examples:
        >>> yaml_str = "document:\\n  id: test"
        >>> data = load_yaml(yaml_str)
        >>> assert "document" in data

        >>> with open("file.yaml") as f:
        ...     data = load_yaml(f)
    """
    # Check type first, then parse YAML
    raw_data = None  # Initialize for clarity and static analysis
    try:
        if isinstance(file_like, str):
            raw_data = yaml.safe_load(file_like)
        elif hasattr(file_like, "read"):
            # File-like object - yaml.safe_load can handle it directly
            raw_data = yaml.safe_load(file_like)
        else:
            raise ValueError(f"file_like must be str or TextIO, got {type(file_like).__name__}")
    except yaml.YAMLError as e:
        raise YAMLLoadError(
            f"Failed to parse YAML content. Error: {str(e)}",
            original_error=e,
        ) from e

    if raw_data is None:
        raise YAMLLoadError(
            "YAML content is empty or contains only null",
        )

    if not isinstance(raw_data, dict):
        raise YAMLLoadError(
            f"YAML content must be a dictionary, got {type(raw_data).__name__}",
        )

    return raw_data


def load_document(file_path: str | Path | TextIO) -> Document:
    """Load YAML file and return Pydantic Document instance.

    Loads a YAML file (from path or file-like object), extracts the document
    data, and creates a Pydantic Document instance. The YAML file should have
    a top-level 'document' key containing the document structure.

    Args:
        file_path: Path to YAML file (str or Path) or file-like object (TextIO).

    Returns:
        Document instance created from the YAML data.

    Raises:
        YAMLLoadError: If the file cannot be read or parsed.
        PydanticValidationError: If the document data does not conform to the
            Pydantic Document model.

    Examples:
        >>> doc = load_document("examples/minimal_document.yaml")
        >>> assert isinstance(doc, Document)
        >>> assert doc.id == "law-1234"
    """
    # Load YAML data
    if isinstance(file_path, (str, Path)):
        yaml_data = load_yaml_file(file_path)
    elif hasattr(file_path, "read"):
        yaml_data = load_yaml(file_path)
    else:
        raise ValueError(f"file_path must be str, Path, or TextIO, got {type(file_path).__name__}")

    # Extract document data
    if "document" not in yaml_data:
        raise YAMLLoadError(
            "YAML file must contain a top-level 'document' key",
        )

    document_data = yaml_data["document"]

    # Create Pydantic Document
    try:
        return Document.model_validate(document_data)  # type: ignore[no-any-return]
    except PydanticValidationErrorBase as e:
        # Convert Pydantic errors to our custom exception
        message, error_details = format_pydantic_errors(e, prefix="Document validation failed")
        raise PydanticValidationError(
            message,
            errors=error_details,
            original_error=e,
        ) from e
