"""Custom exceptions for YAML loading and validation."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError as PydanticValidationErrorBase


class YAMLLoadError(Exception):
    """Exception raised when YAML file cannot be loaded or parsed.

    This exception is raised for:
    - File not found errors
    - Permission errors
    - YAML syntax errors
    - Encoding errors

    Attributes:
        message: Human-readable error message.
        original_error: The original exception that caused this error (if any).
        file_path: Path to the file that caused the error (if applicable).
    """

    def __init__(
        self,
        message: str,
        original_error: Exception | None = None,
        file_path: str | None = None,
    ) -> None:
        """Initialize YAMLLoadError.

        Args:
            message: Human-readable error message.
            original_error: The original exception that caused this error.
            file_path: Path to the file that caused the error.
        """
        super().__init__(message)
        self.message = message
        self.original_error = original_error
        self.file_path = file_path


class ValidationError(Exception):
    """Base exception for validation errors.

    This is the base class for all validation-related exceptions.
    Subclasses should provide more specific error information.

    Attributes:
        message: Human-readable error message.
        errors: List of validation error details (if any).
    """

    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None) -> None:
        """Initialize ValidationError.

        Args:
            message: Human-readable error message.
            errors: List of validation error details.
        """
        super().__init__(message)
        self.message = message
        self.errors = errors or []


class OpenSpecValidationError(ValidationError):
    """Exception raised when validation against OpenSpec schema fails.

    This exception is raised when a document does not conform to the
    OpenSpec schema definition.

    Attributes:
        message: Human-readable error message.
        errors: List of validation errors from jsonschema validator.
        field_paths: List of field paths that failed validation.
    """

    def __init__(
        self,
        message: str,
        errors: list[dict[str, Any]] | None = None,
        field_paths: list[str] | None = None,
    ) -> None:
        """Initialize OpenSpecValidationError.

        Args:
            message: Human-readable error message.
            errors: List of validation errors from jsonschema validator.
            field_paths: List of field paths that failed validation.
        """
        super().__init__(message, errors)
        self.field_paths = field_paths or []


class PydanticValidationError(ValidationError):
    """Exception raised when validation against Pydantic models fails.

    This exception wraps Pydantic's ValidationError to provide a consistent
    interface and clearer error messages.

    Attributes:
        message: Human-readable error message.
        errors: List of validation errors from Pydantic.
        original_error: The original Pydantic ValidationError.
    """

    def __init__(
        self,
        message: str,
        errors: list[dict[str, Any]] | None = None,
        original_error: Exception | None = None,
    ) -> None:
        """Initialize PydanticValidationError.

        Args:
            message: Human-readable error message.
            errors: List of validation errors from Pydantic.
            original_error: The original Pydantic ValidationError.
        """
        super().__init__(message, errors)
        self.original_error = original_error


def format_pydantic_errors(
    error: PydanticValidationErrorBase, prefix: str = "Validation failed"
) -> tuple[str, list[dict[str, Any]]]:
    """Format Pydantic validation errors into a readable message and error details.

    Args:
        error: Pydantic ValidationError instance.
        prefix: Prefix for the error message (default: "Validation failed").

    Returns:
        Tuple of (formatted_message, error_details_list).
    """
    error_messages = []
    error_details = []

    for err in error.errors():
        field_path = " -> ".join(str(loc) for loc in err["loc"])
        error_msg = f"{field_path}: {err['msg']}"
        error_messages.append(error_msg)
        error_details.append(
            {
                "field": field_path,
                "message": err["msg"],
                "type": err["type"],
                "input": err.get("input"),
            }
        )

    message = f"{prefix}:\n" + "\n".join(f"  - {msg}" for msg in error_messages)
    return message, error_details
