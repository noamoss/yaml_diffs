"""Validation utilities for legal documents."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO
from urllib.parse import urlparse

try:
    from jsonschema import FormatChecker
    from jsonschema.validators import Draft202012Validator

    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    # These are only used when JSONSCHEMA_AVAILABLE is True
    # Type ignore needed because we assign None to imported types
    FormatChecker = None  # type: ignore[assignment, misc]
    Draft202012Validator = None  # type: ignore[assignment, misc]

from pydantic import ValidationError as PydanticValidationErrorBase

from yaml_diffs.exceptions import (
    OpenSpecValidationError,
    PydanticValidationError,
    format_pydantic_errors,
)
from yaml_diffs.loader import load_yaml, load_yaml_file
from yaml_diffs.models import Document
from yaml_diffs.schema import load_schema


def _validate_uri(instance: str) -> bool:
    """Validate URI format.

    Args:
        instance: String to validate as URI.

    Returns:
        True if valid URI, False otherwise.
    """
    try:
        result = urlparse(instance)
        # Basic URI validation: must have scheme and netloc for absolute URIs
        return bool(result.scheme and result.netloc)
    except (ValueError, AttributeError, TypeError):
        # urlparse can raise these for invalid input types
        return False


def _validate_date_time(instance: str) -> bool:
    """Validate ISO 8601 date-time format.

    Args:
        instance: String to validate as ISO 8601 date-time.

    Returns:
        True if valid ISO 8601 date-time, False otherwise.
    """
    # Handle timezone with colon separator (e.g., +05:30)
    # Python's strptime only supports +HHMM or -HHMM, not +HH:MM
    # Use regex to check for timezone pattern before normalizing
    match = re.search(r"([+-]\d{2}):(\d{2})$", instance)
    if match:
        # Replace +HH:MM or -HH:MM with +HHMM or -HHMM
        normalized_instance = re.sub(r"([+-])(\d{2}):(\d{2})$", r"\1\2\3", instance)
    else:
        normalized_instance = instance

    # Try common ISO 8601 formats
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d",  # Date only format
    ]
    for fmt in formats:
        try:
            datetime.strptime(normalized_instance, fmt)
            return True
        except ValueError:
            continue
    return False


def _get_format_checker() -> FormatChecker:
    """Get format checker with custom validators.

    Returns:
        FormatChecker instance with URI and date-time validators.

    Raises:
        ImportError: If jsonschema is not available.
    """
    if not JSONSCHEMA_AVAILABLE:
        raise ImportError(
            "jsonschema is required for OpenSpec validation. "
            "Install it with: pip install jsonschema"
        )

    format_checker = FormatChecker()
    # Type ignore needed for FormatChecker.checks() type variable limitation
    format_checker.checks("uri")(_validate_uri)  # type: ignore[type-var, misc]
    format_checker.checks("date-time")(_validate_date_time)  # type: ignore[type-var, misc]
    return format_checker


def validate_against_openspec(
    data: dict[str, Any],
    schema: dict[str, Any] | None = None,
) -> None:
    """Validate data against OpenSpec schema.

    Validates the provided data dictionary against the OpenSpec JSON Schema
    definition. Uses Draft202012Validator with custom format checkers for
    URI and date-time validation.

    Args:
        data: Dictionary containing document data to validate. Should have
            a top-level 'document' key matching the schema structure.
        schema: Optional schema dictionary. If not provided, loads the default
            schema using load_schema().

    Raises:
        ImportError: If jsonschema is not available.
        OpenSpecValidationError: If validation fails. The exception includes:
            - Aggregated error messages
            - Field paths for each error
            - Detailed error information

    Examples:
        >>> data = {"document": {"id": "test", ...}}
        >>> validate_against_openspec(data)  # Raises if invalid
    """
    if not JSONSCHEMA_AVAILABLE:
        raise ImportError(
            "jsonschema is required for OpenSpec validation. "
            "Install it with: pip install jsonschema"
        )

    if schema is None:
        schema = load_schema()

    format_checker = _get_format_checker()
    validator = Draft202012Validator(schema, format_checker=format_checker)

    # Collect all validation errors
    errors = []
    field_paths = []

    for error in validator.iter_errors(data):
        # Build field path from error path
        field_path = " -> ".join(str(part) for part in error.path)
        if not field_path:
            field_path = "root"

        error_info = {
            "field": field_path,
            "message": error.message,
            "validator": error.validator,
            "validator_value": error.validator_value,
            "instance": error.instance,
        }
        errors.append(error_info)
        field_paths.append(field_path)

    if errors:
        # Build error message
        error_messages = []
        for error_info in errors:
            field = error_info["field"]
            message = error_info["message"]
            error_messages.append(f"{field}: {message}")

        message = "OpenSpec validation failed:\n" + "\n".join(
            f"  - {msg}" for msg in error_messages
        )

        raise OpenSpecValidationError(
            message,
            errors=errors,
            field_paths=field_paths,
        )


def validate_against_pydantic(data: dict[str, Any]) -> Document:
    """Validate data against Pydantic models and return Document instance.

    Validates the provided data dictionary against the Pydantic Document model.
    If the data has a top-level 'document' key, it extracts that first.

    Args:
        data: Dictionary containing document data. Can have a top-level
            'document' key or be the document data directly.

    Returns:
        Document instance created from the validated data.

    Raises:
        PydanticValidationError: If validation fails. The exception includes:
            - Aggregated error messages
            - Field paths for each error
            - Detailed error information from Pydantic

    Examples:
        >>> data = {"id": "test", "title": "Test", ...}
        >>> doc = validate_against_pydantic(data)
        >>> assert isinstance(doc, Document)
    """
    # Extract document data if wrapped in 'document' key
    if "document" in data:
        document_data = data["document"]
    else:
        document_data = data

    try:
        return Document.model_validate(document_data)  # type: ignore[no-any-return]
    except PydanticValidationErrorBase as e:
        # Convert Pydantic errors to our custom exception
        message, error_details = format_pydantic_errors(e, prefix="Pydantic validation failed")
        raise PydanticValidationError(
            message,
            errors=error_details,
            original_error=e,
        ) from e


def validate_document(file_path: str | Path | TextIO) -> Document:
    """Validate document with full validation (OpenSpec + Pydantic).

    Loads a YAML file, validates it against the OpenSpec schema, and then
    validates it against Pydantic models. Returns a Document instance if
    all validations pass.

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
        >>> doc = validate_document("examples/minimal_document.yaml")
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

    # Validate against OpenSpec schema
    validate_against_openspec(yaml_data)

    # Validate against Pydantic models
    return validate_against_pydantic(yaml_data)
