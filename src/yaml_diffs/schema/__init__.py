"""OpenSpec schema definitions for legal documents."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


def _get_schema_path() -> Path:
    """Get the path to the OpenSpec schema file."""
    return Path(__file__).parent / "legal_document_spec.yaml"


@lru_cache(maxsize=1)
def load_schema() -> dict[str, Any]:
    """Load and return the OpenSpec schema definition.

    Returns:
        Dictionary containing the JSON Schema definition.

    Raises:
        FileNotFoundError: If the schema file does not exist.
        yaml.YAMLError: If the schema file is invalid YAML.
    """
    schema_path = _get_schema_path()
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    return schema  # type: ignore[no-any-return]


def get_schema_version() -> str:
    """Get the version of the OpenSpec schema.

    Returns:
        Schema version string.

    Raises:
        KeyError: If schema version is not defined.
        FileNotFoundError: If the schema file does not exist.
        yaml.YAMLError: If the schema file is invalid YAML.
    """
    schema = load_schema()
    if "version" not in schema:
        raise KeyError("Schema version not defined")
    return schema["version"]  # type: ignore[no-any-return]


__all__ = ["load_schema", "get_schema_version"]
