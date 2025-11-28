# API Reference

This document provides a comprehensive reference for the yaml-diffs Python library API.

## Overview

The yaml-diffs library provides a clean, intuitive interface for working with Hebrew legal documents in YAML format. The API supports loading, validating, and diffing documents with full support for Hebrew content and nested document structures.

## Quick Start

```python
from yaml_diffs import api

# Load and validate a document
doc = api.load_and_validate("examples/minimal_document.yaml")

# Diff two documents
diff = api.diff_files("old.yaml", "new.yaml")

# Diff and format in one call
json_diff = api.diff_and_format("old.yaml", "new.yaml", output_format="json")
```

## Main Functions

### `load_document(file_path)`

Load a YAML file and return a `Document` instance.

**Parameters:**
- `file_path` (str | Path | TextIO): Path to YAML file or file-like object

**Returns:**
- `Document`: Pydantic Document instance

**Raises:**
- `YAMLLoadError`: If the file cannot be read or parsed
- `PydanticValidationError`: If the document data does not conform to the Pydantic Document model

**Example:**
```python
from yaml_diffs import load_document

# Load from file path
doc = load_document("examples/minimal_document.yaml")

# Load from file-like object
with open("document.yaml") as f:
    doc = load_document(f)
```

### `validate_document(file_path)`

Load and validate a YAML file against both OpenSpec schema and Pydantic models.

**Parameters:**
- `file_path` (str | Path | TextIO): Path to YAML file or file-like object

**Returns:**
- `Document`: Pydantic Document instance

**Raises:**
- `YAMLLoadError`: If the file cannot be read or parsed
- `OpenSpecValidationError`: If OpenSpec validation fails
- `PydanticValidationError`: If Pydantic validation fails

**Example:**
```python
from yaml_diffs import validate_document

doc = validate_document("examples/minimal_document.yaml")
assert doc.id == "test-123"
```

### `diff_documents(old, new)`

Compare two Document versions and detect changes.

**Parameters:**
- `old` (Document): Old document version
- `new` (Document): New document version

**Returns:**
- `DocumentDiff`: DocumentDiff containing all detected changes

**Raises:**
- `ValueError`: If duplicate markers found at same level in either document

**Example:**
```python
from yaml_diffs import load_document, diff_documents

old_doc = load_document("examples/document_v1.yaml")
new_doc = load_document("examples/document_v2.yaml")
diff = diff_documents(old_doc, new_doc)

print(f"Added: {diff.added_count}, Removed: {diff.deleted_count}")
print(f"Modified: {diff.modified_count}, Moved: {diff.moved_count}")
```

### `format_diff(diff, output_format="json", **kwargs)`

Format a DocumentDiff using the specified formatter.

**Parameters:**
- `diff` (DocumentDiff): DocumentDiff to format
- `output_format` (str): Output format ("json", "text", or "yaml", default: "json")
- `filter_change_types` (Optional[Sequence[ChangeType]]): Optional sequence of change types to include (accepts both `list` and `tuple`)
- `filter_section_path` (Optional[str]): Optional marker path to filter by (exact match)
- `**kwargs`: Additional formatter-specific options (e.g., `indent` for JSON formatter)

**Returns:**
- `str`: Formatted string representation of the diff

**Raises:**
- `ValueError`: If output_format is not one of "json", "text", or "yaml"

**Example:**
```python
from yaml_diffs import diff_documents, format_diff, ChangeType

diff = diff_documents(old_doc, new_doc)

# Format as JSON
json_output = format_diff(diff, output_format="json")

# Format as text
text_output = format_diff(diff, output_format="text")

# Format with filters
filtered_output = format_diff(
    diff,
    output_format="json",
    filter_change_types=[ChangeType.CONTENT_CHANGED],
)
```

## Convenience Functions

### `load_and_validate(file_path)`

Load and validate a document in one call. This is equivalent to calling `validate_document()`.

**Parameters:**
- `file_path` (str | Path | TextIO): Path to YAML file or file-like object

**Returns:**
- `Document`: Pydantic Document instance

**Raises:**
- `YAMLLoadError`: If the file cannot be read or parsed
- `OpenSpecValidationError`: If OpenSpec validation fails
- `PydanticValidationError`: If Pydantic validation fails

**Example:**
```python
from yaml_diffs import load_and_validate

doc = load_and_validate("examples/minimal_document.yaml")
```

### `diff_files(old_file, new_file)`

Load and diff two document files. This combines `load_document()` and `diff_documents()` into a single call.

**Parameters:**
- `old_file` (str | Path | TextIO): Path to old document version or file-like object
- `new_file` (str | Path | TextIO): Path to new document version or file-like object

**Returns:**
- `DocumentDiff`: DocumentDiff containing all detected changes

**Raises:**
- `YAMLLoadError`: If either file cannot be read or parsed
- `PydanticValidationError`: If either document fails Pydantic validation
- `ValueError`: If duplicate markers found at same level in either document

**Example:**
```python
from yaml_diffs import diff_files

diff = diff_files("examples/document_v1.yaml", "examples/document_v2.yaml")
print(f"Changes: {len(diff.changes)}")
```

### `diff_and_format(old_file, new_file, output_format="json", **kwargs)`

Load, diff, and format two documents in one call. This combines `diff_files()` and `format_diff()` into a single call.

**Parameters:**
- `old_file` (str | Path | TextIO): Path to old document version or file-like object
- `new_file` (str | Path | TextIO): Path to new document version or file-like object
- `output_format` (str): Output format ("json", "text", or "yaml", default: "json")
- `filter_change_types` (Optional[Sequence[ChangeType]]): Optional sequence of change types to include (accepts both `list` and `tuple`)
- `filter_section_path` (Optional[str]): Optional marker path to filter by (exact match)
- `**kwargs`: Additional formatter-specific options

**Returns:**
- `str`: Formatted string representation of the diff

**Raises:**
- `YAMLLoadError`: If either file cannot be read or parsed
- `PydanticValidationError`: If either document fails Pydantic validation
- `ValueError`: If duplicate markers found or invalid output_format

**Example:**
```python
from yaml_diffs import diff_and_format, ChangeType

# Get JSON diff
json_diff = diff_and_format("old.yaml", "new.yaml", output_format="json")

# Get filtered text diff
text_diff = diff_and_format(
    "old.yaml",
    "new.yaml",
    output_format="text",
    filter_change_types=[ChangeType.CONTENT_CHANGED],
)
```

## Common Use Cases

### 1. Load and Inspect a Document

```python
from yaml_diffs import load_document

doc = load_document("examples/minimal_document.yaml")
print(f"Document ID: {doc.id}")
print(f"Title: {doc.title}")
print(f"Number of sections: {len(doc.sections)}")
```

### 2. Validate a Document

```python
from yaml_diffs import validate_document, ValidationError

try:
    doc = validate_document("document.yaml")
    print("Document is valid!")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### 3. Compare Two Document Versions

```python
from yaml_diffs import diff_files

diff = diff_files("document_v1.yaml", "document_v2.yaml")
print(f"Added sections: {diff.added_count}")
print(f"Removed sections: {diff.deleted_count}")
print(f"Modified sections: {diff.modified_count}")

for change in diff.changes:
    print(f"{change.change_type}: {change.marker}")
```

### 4. Get Formatted Diff Output

```python
from yaml_diffs import diff_and_format

# Get JSON diff
json_output = diff_and_format("old.yaml", "new.yaml", output_format="json")
print(json_output)

# Save to file
with open("diff.json", "w") as f:
    f.write(json_output)
```

### 5. Complete Workflow

```python
from yaml_diffs import load_and_validate, diff_documents, format_diff

# Load and validate both documents
old_doc = load_and_validate("document_v1.yaml")
new_doc = load_and_validate("document_v2.yaml")

# Diff them
diff = diff_documents(old_doc, new_doc)

# Format the results
json_output = format_diff(diff, output_format="json")
text_output = format_diff(diff, output_format="text")

print("JSON Output:")
print(json_output)
print("\nText Output:")
print(text_output)
```

## Error Handling

The API uses custom exceptions for clear error handling:

### `YAMLLoadError`

Raised when a YAML file cannot be loaded or parsed.

```python
from yaml_diffs import load_document, YAMLLoadError

try:
    doc = load_document("nonexistent.yaml")
except YAMLLoadError as e:
    print(f"Failed to load file: {e.message}")
    if e.file_path:
        print(f"File: {e.file_path}")
```

### `ValidationError`

Base exception for all validation errors.

### `OpenSpecValidationError`

Raised when validation against OpenSpec schema fails.

```python
from yaml_diffs import validate_document, OpenSpecValidationError

try:
    doc = validate_document("invalid_schema.yaml")
except OpenSpecValidationError as e:
    print(f"Schema validation failed: {e.message}")
    for field_path in e.field_paths:
        print(f"  - {field_path}")
```

### `PydanticValidationError`

Raised when validation against Pydantic models fails.

```python
from yaml_diffs import load_document, PydanticValidationError

try:
    doc = load_document("invalid_data.yaml")
except PydanticValidationError as e:
    print(f"Validation failed: {e.message}")
    for error in e.errors:
        print(f"  - {error['field']}: {error['message']}")
```

## Types

### `Document`

Pydantic model representing a legal document.

**Attributes:**
- `id` (str): Document identifier
- `title` (str): Document title
- `type` (DocumentType): Document type (law, regulation, etc.)
- `language` (str): Document language (typically "hebrew")
- `version` (Version): Document version information
- `source` (Source): Document source information
- `sections` (list[Section]): List of document sections

### `Section`

Pydantic model representing a document section.

**Attributes:**
- `id` (str): Section identifier
- `marker` (str): Section marker (primary identifier for diffing)
- `title` (Optional[str]): Section title
- `content` (str): Section content
- `sections` (list[Section]): Nested sections (recursive structure)

### `DocumentDiff`

Result of comparing two document versions.

**Attributes:**
- `changes` (list[DiffResult]): List of all changes detected
- `added_count` (int): Count of added sections
- `deleted_count` (int): Count of deleted sections
- `modified_count` (int): Count of modified sections
- `moved_count` (int): Count of moved sections

### `DiffResult`

Represents a single change detected in document diffing.

**Attributes:**
- `id` (str): Unique identifier for this change (UUID)
- `section_id` (str): The section ID (for tracking, from old or new version)
- `change_type` (ChangeType): Type of change detected
- `marker` (str): The section marker (primary identifier)
- `old_marker_path` (Optional[tuple[str, ...]]): Marker path in old version (markers from root)
- `new_marker_path` (Optional[tuple[str, ...]]): Marker path in new version
- `old_id_path` (Optional[list[str]]): ID path in old version (for tracking)
- `new_id_path` (Optional[list[str]]): ID path in new version (for tracking)
- `old_content` (Optional[str]): Content in old version
- `new_content` (Optional[str]): Content in new version
- `old_title` (Optional[str]): Title in old version
- `new_title` (Optional[str]): Title in new version
- `old_section_yaml` (Optional[str]): Full YAML representation of section in old version
- `new_section_yaml` (Optional[str]): Full YAML representation of section in new version
- `old_line_number` (Optional[int]): Starting line number in old document (1-indexed)
- `new_line_number` (Optional[int]): Starting line number in new document (1-indexed)

**Note:** The `old_section_yaml`, `new_section_yaml`, `old_line_number`, and `new_line_number` fields are populated when using the REST API's `/api/v1/diff` endpoint. They provide extracted section data and line locations to enable UI clients to display section context without client-side YAML parsing.

### `ChangeType`

Enumeration of change types.

**Values:**
- `SECTION_ADDED`: New section added in new version
- `SECTION_REMOVED`: Section removed from old version
- `CONTENT_CHANGED`: Content changed (same marker+path)
- `SECTION_MOVED`: Path changed but title+content same
- `TITLE_CHANGED`: Title changed (same marker+path+content)
- `UNCHANGED`: No changes detected

## Additional Utilities

The API also exports additional utility functions:

- `load_yaml_file(file_path)`: Load raw YAML data from file
- `load_yaml(file_like)`: Load raw YAML data from file-like object or string
- `validate_against_openspec(data, schema=None)`: Validate data against OpenSpec schema
- `validate_against_pydantic(data)`: Validate data against Pydantic models
- `format_pydantic_errors(error, prefix="Validation failed")`: Format Pydantic validation errors

## Import Patterns

### Recommended: Import from main module

```python
from yaml_diffs import (
    load_document,
    validate_document,
    diff_documents,
    diff_files,
    diff_and_format,
)
```

### Alternative: Import from api module

```python
from yaml_diffs.api import (
    load_document,
    validate_document,
    diff_documents,
    diff_files,
    diff_and_format,
)
```

### Backward Compatible: Direct imports still work

```python
from yaml_diffs.loader import load_document
from yaml_diffs.validator import validate_document
from yaml_diffs.diff import diff_documents
```

## See Also

- [README.md](../../README.md) - Project overview and installation
- [AGENTS.md](../../AGENTS.md) - Development guide for AI agents
- [Schema Reference](../user/schema_reference.md) - OpenSpec schema documentation
- [Getting Started](../user/getting_started.md) - Quick start guide
