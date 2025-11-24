"""yaml-diffs: Python service for Hebrew legal documents in YAML format."""

from yaml_diffs.__version__ import __version__

# Import main API functions from api.py for unified interface
from yaml_diffs.api import (
    ChangeType,
    DiffResult,
    Document,
    DocumentDiff,
    OpenSpecValidationError,
    PydanticValidationError,
    Section,
    ValidationError,
    YAMLLoadError,
    diff_and_format,
    diff_documents,
    diff_files,
    format_diff,
    load_and_validate,
    load_document,
    validate_document,
)

# Import additional utilities and formatters directly (not in api.py)
from yaml_diffs.exceptions import format_pydantic_errors
from yaml_diffs.formatters import JsonFormatter, TextFormatter, YamlFormatter
from yaml_diffs.loader import load_yaml, load_yaml_file
from yaml_diffs.validator import validate_against_openspec, validate_against_pydantic

__all__ = [
    "__version__",
    # Main API functions (from api.py)
    "load_document",
    "validate_document",
    "diff_documents",
    "format_diff",
    # Convenience functions (from api.py)
    "load_and_validate",
    "diff_files",
    "diff_and_format",
    # Exceptions (from api.py)
    "YAMLLoadError",
    "ValidationError",
    "OpenSpecValidationError",
    "PydanticValidationError",
    # Utilities
    "format_pydantic_errors",
    # Loader functions (additional utilities)
    "load_yaml_file",
    "load_yaml",
    # Validator functions (additional utilities)
    "validate_against_openspec",
    "validate_against_pydantic",
    # Diff types (from api.py)
    "ChangeType",
    "DiffResult",
    "DocumentDiff",
    # Model types (from api.py)
    "Document",
    "Section",
    # Formatters (additional utilities)
    "JsonFormatter",
    "TextFormatter",
    "YamlFormatter",
]
