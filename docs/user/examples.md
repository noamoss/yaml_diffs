# Examples Guide

This guide explains how to use the example documents provided with yaml-diffs and how to create new documents from templates.

## Example Files

The `examples/` directory contains several example documents demonstrating different use cases:

### Available Examples

1. **`minimal_document.yaml`** - Minimal valid document with all required fields
2. **`complex_document.yaml`** - Complex document with deep nesting (5+ levels)
3. **`document_v1.yaml`** - Version 1 of a document for diffing
4. **`document_v2.yaml`** - Version 2 of the same document (shows various change types)
5. **`template.yaml`** - Template for creating new documents

## Using Examples

### Validate an Example

```bash
# Using CLI
yaml-diffs validate examples/minimal_document.yaml

# Using Python
from yaml_diffs import validate_document
doc = validate_document("examples/minimal_document.yaml")
print(f"Valid document: {doc.title}")
```

### Diff Example Versions

```bash
# Using CLI
yaml-diffs diff examples/document_v1.yaml examples/document_v2.yaml

# Using Python
from yaml_diffs import diff_files
diff = diff_files("examples/document_v1.yaml", "examples/document_v2.yaml")
print(f"Changes detected: {len(diff.changes)}")
```

### Load and Inspect Examples

```python
from yaml_diffs import load_document

# Load minimal example
minimal = load_document("examples/minimal_document.yaml")
print(f"Title: {minimal.title}")
print(f"Sections: {len(minimal.sections)}")

# Load complex example
complex_doc = load_document("examples/complex_document.yaml")
print(f"Deep nesting example with {len(complex_doc.sections)} top-level sections")
```

## Example Use Cases

### Use Case 1: Learning the Schema

Start with `minimal_document.yaml` to understand the basic structure:

```yaml
document:
  id: "law-1234"
  title: "חוק הדוגמה לרגולציה"
  type: "law"
  language: "hebrew"
  version:
    number: "2024-01-01"
  source:
    url: "https://example.gov.il/law1234"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: "1"
      title: "הגדרות"
      content: "תוכן הסעיף"
      sections: []
```

### Use Case 2: Understanding Deep Nesting

Use `complex_document.yaml` to see how sections can be nested to unlimited depth:

```yaml
sections:
  - id: "chap-1"
    marker: "פרק א'"
    sections:
      - id: "sec-1-1"
        marker: "1"
        sections:
          - id: "sec-1-1-a"
            marker: "(א)"
            sections:
              - id: "sec-1-1-a-1"
                marker: "1"
                sections:
                  - id: "sec-1-1-a-1-i"
                    marker: "א"
                    sections: []
```

### Use Case 3: Testing Diff Functionality

Use `document_v1.yaml` and `document_v2.yaml` to test diffing:

```python
from yaml_diffs import diff_files, ChangeType

diff = diff_files("examples/document_v1.yaml", "examples/document_v2.yaml")

# Check for different change types
for change in diff.changes:
    if change.change_type == ChangeType.SECTION_ADDED:
        print(f"Added section: {change.marker}")
    elif change.change_type == ChangeType.CONTENT_CHANGED:
        print(f"Content changed in: {change.marker}")
    elif change.change_type == ChangeType.SECTION_MOVED:
        print(f"Moved section: {change.marker}")
```

## Creating New Documents

### Using the Template

1. **Copy the template:**
   ```bash
   cp examples/template.yaml my_document.yaml
   ```

2. **Edit the document:**
   - Replace placeholder values with your document information
   - Add sections as needed
   - Ensure all required fields are filled

3. **Validate your document:**
   ```bash
   yaml-diffs validate my_document.yaml
   ```

### Template Structure

The template includes:
- All required fields with comments
- Example section structure
- Placeholder values
- Comments explaining each field

```yaml
# Template for creating new legal documents
document:
  id: "your-document-id"  # Required: Stable identifier (UUID or canonical ID)
  title: "כותרת המסמך"     # Required: Document title in Hebrew
  type: "law"              # Required: law, regulation, directive, circular, policy, other
  language: "hebrew"       # Required: Must be "hebrew"
  version:
    number: "2024-01-01"   # Required: Version identifier or date
    description: ""        # Optional: Version description
  source:
    url: "https://..."     # Required: Source URL
    fetched_at: "2025-01-20T09:50:00Z"  # Required: ISO 8601 timestamp
  sections: []             # Required: Array of sections (can be empty)
  # Optional fields:
  # authors: []
  # published_date: ""
  # updated_date: ""
```

## Example Workflows

### Workflow 1: Create a New Document

```python
from yaml_diffs import validate_document
from pathlib import Path

# Create document from template
template = Path("examples/template.yaml")
new_doc = Path("my_new_document.yaml")

# Copy and edit template (manual step)
# Then validate
try:
    doc = validate_document(new_doc)
    print(f"Document created successfully: {doc.title}")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Workflow 2: Compare Document Versions

```python
from yaml_diffs import diff_and_format

# Compare versions
diff_json = diff_and_format(
    "examples/document_v1.yaml",
    "examples/document_v2.yaml",
    output_format="json"
)

# Save diff report
with open("diff_report.json", "w") as f:
    f.write(diff_json)
```

### Workflow 3: Process Multiple Documents

```python
from pathlib import Path
from yaml_diffs import load_document

# Process all YAML files in a directory
examples_dir = Path("examples")
for yaml_file in examples_dir.glob("*.yaml"):
    if yaml_file.name == "template.yaml":
        continue  # Skip template

    try:
        doc = load_document(yaml_file)
        print(f"✓ {yaml_file.name}: {doc.title}")
    except Exception as e:
        print(f"✗ {yaml_file.name}: {e}")
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

Include actual Hebrew content in examples to test UTF-8 handling:

```yaml
content: |
  בחוק זה—
  "מוסד" – גוף הפועל לפי הוראות החוק.
```

## Example File Locations

All examples are located in the `examples/` directory:

- `examples/minimal_document.yaml`
- `examples/complex_document.yaml`
- `examples/document_v1.yaml`
- `examples/document_v2.yaml`
- `examples/template.yaml`
- `examples/README.md` - Examples directory guide

## Related Documentation

- [Getting Started](getting_started.md) - Quick start guide
- [Schema Reference](schema_reference.md) - Complete schema documentation
- [API Reference](../developer/api_reference.md) - Python API documentation
- [Examples README](../../examples/README.md) - Examples directory guide
