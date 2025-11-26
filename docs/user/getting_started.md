# Getting Started

This guide will help you get started with yaml-diffs quickly. You'll learn how to install the library and use it through different interfaces.

## Installation

### Prerequisites

- Python 3.10 or higher (required for MCP server support)
- uv (recommended) or pip for package management

### Install with uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install yaml-diffs
uv pip install yaml-diffs
```

### Install with pip

```bash
pip install yaml-diffs
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/noamoss/yaml_diffs.git
cd yaml_diffs

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv sync --extra dev
```

## Quick Start Examples

### Python Library

The simplest way to use yaml-diffs is through the Python library:

```python
from yaml_diffs import load_document, diff_documents, format_diff

# Load a document
doc = load_document("document.yaml")
print(f"Document: {doc.title}")

# Diff two documents
old_doc = load_document("document_v1.yaml")
new_doc = load_document("document_v2.yaml")
diff = diff_documents(old_doc, new_doc)

# Format the results
json_output = format_diff(diff, output_format="json")
print(json_output)
```

### CLI Tool

Use the command-line interface for quick operations:

```bash
# Validate a document
yaml-diffs validate examples/minimal_document.yaml

# Diff two documents
yaml-diffs diff examples/document_v1.yaml examples/document_v2.yaml

# Diff with text output
yaml-diffs diff old.yaml new.yaml --format text

# Save diff to file
yaml-diffs diff old.yaml new.yaml --output diff.json
```

### REST API

Start the API server and use HTTP endpoints:

```bash
# Start the server
uvicorn src.yaml_diffs.api_server.main:app --reload --port 8000

# Validate a document (using curl)
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{"yaml": "document:\n  id: \"test\"\n  ..."}'

# Diff two documents
curl -X POST http://localhost:8000/api/v1/diff \
  -H "Content-Type: application/json" \
  -d '{"old_yaml": "...", "new_yaml": "..."}'
```

The API also provides interactive documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### MCP Server

For AI assistants, use the MCP server:

```bash
# Run MCP server (connects to local API by default)
yaml-diffs mcp-server

# Or with custom configuration
yaml-diffs mcp-server --api-url http://api.example.com:8000
```

## Basic Usage Patterns

### 1. Load and Validate a Document

```python
from yaml_diffs import validate_document

try:
    doc = validate_document("document.yaml")
    print(f"Document is valid: {doc.title}")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### 2. Compare Document Versions

```python
from yaml_diffs import diff_files

diff = diff_files("document_v1.yaml", "document_v2.yaml")
print(f"Added: {diff.added_count}")
print(f"Removed: {diff.deleted_count}")
print(f"Modified: {diff.modified_count}")
print(f"Moved: {diff.moved_count}")
```

### 3. Get Formatted Diff Output

```python
from yaml_diffs import diff_and_format, ChangeType

# Get JSON diff
json_diff = diff_and_format("old.yaml", "new.yaml", output_format="json")

# Get filtered diff (only content changes)
filtered_diff = diff_and_format(
    "old.yaml",
    "new.yaml",
    output_format="text",
    filter_change_types=[ChangeType.CONTENT_CHANGED],
)
```

### 4. Complete Workflow

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

# Save to files
with open("diff.json", "w") as f:
    f.write(json_output)
```

## Common Workflows

### Workflow 1: Validate New Documents

When receiving a new legal document in YAML format:

```python
from yaml_diffs import validate_document

doc = validate_document("new_document.yaml")
# Document is valid, proceed with processing
```

### Workflow 2: Track Document Changes

Compare versions of a document over time:

```python
from yaml_diffs import diff_files

# Compare current version with previous
diff = diff_files("document_2024-01.yaml", "document_2024-02.yaml")

# Analyze changes
for change in diff.changes:
    if change.change_type == ChangeType.CONTENT_CHANGED:
        print(f"Content changed in section {change.marker}")
        print(f"Old: {change.old_content[:50]}...")
        print(f"New: {change.new_content[:50]}...")
```

### Workflow 3: Generate Change Reports

Create formatted reports of document changes:

```python
from yaml_diffs import diff_and_format

# Generate JSON report
json_report = diff_and_format("old.yaml", "new.yaml", output_format="json")

# Generate human-readable text report
text_report = diff_and_format("old.yaml", "new.yaml", output_format="text")

# Save reports
with open("change_report.json", "w") as f:
    f.write(json_report)
with open("change_report.txt", "w") as f:
    f.write(text_report)
```

## Next Steps

- **[Schema Reference](schema_reference.md)** - Learn about the document structure and schema
- **[Examples Guide](examples.md)** - Explore example documents and templates
- **[API Reference](../developer/api_reference.md)** - Complete API documentation
- **[REST API](../api/api_server.md)** - REST API documentation
- **[MCP Server](../api/mcp_server.md)** - MCP server for AI assistants

## Getting Help

- **Documentation**: See the [Documentation Index](../README.md)
- **Issues**: [GitHub Issues](https://github.com/noamoss/yaml_diffs/issues)
- **Project Board**: [GitHub Project Board](https://github.com/users/noamoss/projects/4)
