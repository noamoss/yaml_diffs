"""yaml-diffs: Python service for Hebrew legal documents in YAML format."""

from yaml_diffs.__version__ import __version__
from yaml_diffs.diff import diff_documents
from yaml_diffs.diff_types import ChangeType, DiffResult, DocumentDiff
from yaml_diffs.exceptions import (
    OpenSpecValidationError,
    PydanticValidationError,
    ValidationError,
    YAMLLoadError,
    format_pydantic_errors,
)
from yaml_diffs.loader import load_document, load_yaml, load_yaml_file
from yaml_diffs.validator import (
    validate_against_openspec,
    validate_against_pydantic,
    validate_document,
)

__all__ = [
    "__version__",
    # Exceptions
    "YAMLLoadError",
    "ValidationError",
    "OpenSpecValidationError",
    "PydanticValidationError",
    # Utilities
    "format_pydantic_errors",
    # Loader functions
    "load_yaml_file",
    "load_yaml",
    "load_document",
    # Validator functions
    "validate_against_openspec",
    "validate_against_pydantic",
    "validate_document",
    # Diff functions
    "diff_documents",
    # Diff types
    "ChangeType",
    "DiffResult",
    "DocumentDiff",
]
