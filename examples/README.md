# Examples Directory

This directory contains example YAML documents demonstrating various features and use cases of yaml-diffs.

## Example Files

### `minimal_document.yaml`

A minimal valid document demonstrating the basic structure with all required fields. This is a good starting point for understanding the schema.

**Features:**
- All required fields
- Single section with Hebrew content
- Demonstrates basic structure

**Use Case:** Learning the schema, quick reference

### `complex_document.yaml`

A complex document with deep nesting (5+ levels) demonstrating the recursive section structure capabilities.

**Features:**
- Deep nesting (6 levels)
- Various marker types (Hebrew, numeric, parentheses)
- Multiple chapters and sections
- Demonstrates unlimited nesting depth

**Use Case:** Understanding deep nesting, testing recursive structures

### `document_v1.yaml` and `document_v2.yaml`

Two versions of the same document demonstrating various change types that can be detected by the diff engine.

**Features:**
- Version 1: Base document
- Version 2: Modified document showing:
  - Added sections
  - Content changes
  - Section movements
  - Title changes
  - Combined changes

**Use Case:** Testing diff functionality, understanding change detection

### `template.yaml`

A template file for creating new documents. Copy this file and replace placeholder values with your document information.

**Features:**
- All required fields with comments
- Optional fields shown with examples
- Clear instructions for each field

**Use Case:** Creating new documents, quick start

## Using Examples

### Validate an Example

```bash
# Using CLI
yaml-diffs validate examples/minimal_document.yaml

# Using Python
from yaml_diffs import validate_document
doc = validate_document("examples/minimal_document.yaml")
```

### Diff Example Versions

```bash
# Using CLI
yaml-diffs diff examples/document_v1.yaml examples/document_v2.yaml

# Using Python
from yaml_diffs import diff_files
diff = diff_files("examples/document_v1.yaml", "examples/document_v2.yaml")
```

### Create a New Document from Template

```bash
# Copy template
cp examples/template.yaml my_document.yaml

# Edit my_document.yaml with your content

# Validate
yaml-diffs validate my_document.yaml
```

## Example Use Cases

### Use Case 1: Learning the Schema

Start with `minimal_document.yaml` to understand the basic structure:

```python
from yaml_diffs import load_document

doc = load_document("examples/minimal_document.yaml")
print(f"Document: {doc.title}")
print(f"Sections: {len(doc.sections)}")
```

### Use Case 2: Understanding Deep Nesting

Use `complex_document.yaml` to see how sections can be nested:

```python
from yaml_diffs import load_document

doc = load_document("examples/complex_document.yaml")
# Explore the nested structure
for section in doc.sections:
    print(f"Section: {section.marker} - {section.title}")
    # Recursively explore nested sections
```

### Use Case 3: Testing Diff Functionality

Use `document_v1.yaml` and `document_v2.yaml` to test diffing:

```python
from yaml_diffs import diff_files, ChangeType

diff = diff_files("examples/document_v1.yaml", "examples/document_v2.yaml")

# Analyze different change types
print(f"Added: {diff.added_count}")
print(f"Removed: {diff.deleted_count}")
print(f"Modified: {diff.modified_count}")
print(f"Moved: {diff.moved_count}")

# Inspect individual changes
for change in diff.changes:
    print(f"{change.change_type}: {change.marker}")
```

## Best Practices

### 1. Start with the Template

Always start new documents from `template.yaml` to ensure you include all required fields.

### 2. Validate Frequently

Validate your document as you build it:

```bash
yaml-diffs validate my_document.yaml
```

### 3. Use Meaningful IDs

Use stable, meaningful IDs for documents and sections:

```yaml
# Good
id: "law-cyber-security-2024"
id: "sec-definitions"

# Avoid
id: "doc1"
id: "section1"
```

### 4. Ensure Marker Uniqueness

Markers must be unique within each nesting level:

```yaml
sections:
  - marker: "1"  # OK
  - marker: "2"  # OK
  - marker: "1"  # ERROR: Duplicate at same level
```

### 5. Use Hebrew Content

Include actual Hebrew content in your documents:

```yaml
content: |
  בחוק זה—
  "מוסד" – גוף הפועל לפי הוראות החוק.
```

## Related Documentation

- [Examples Guide](../docs/user/examples.md) - Detailed examples guide
- [Schema Reference](../docs/user/schema_reference.md) - Complete schema documentation
- [Getting Started](../docs/user/getting_started.md) - Quick start guide
- [API Reference](../docs/developer/api_reference.md) - Python API documentation

## File Structure

```
examples/
├── minimal_document.yaml      # Minimal valid document
├── complex_document.yaml      # Complex nested document
├── document_v1.yaml           # Version 1 for diffing
├── document_v2.yaml           # Version 2 for diffing
├── template.yaml              # Template for new documents
└── README.md                  # This file
```
