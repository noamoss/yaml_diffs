# Schema Reference

This document provides a comprehensive reference for the OpenSpec schema used by yaml-diffs. The schema defines the structure for Hebrew legal and regulatory documents in YAML format.

## Overview

The yaml-diffs schema is defined using OpenSpec (JSON Schema Draft 2020-12) and supports:

- **Recursive sections** with unlimited nesting depth
- **Flexible structural markers** (e.g., "1", "א", "(a)", "Chapter I")
- **Hebrew content** with full UTF-8 support
- **Stable IDs** for reliable change tracking
- **Version information** for document versioning

The schema file is located at: `src/yaml_diffs/schema/legal_document_spec.yaml`

## Document Structure

A valid document must have the following top-level structure:

```yaml
document:
  id: string              # Required: Stable document identifier
  title: string           # Required: Document title in Hebrew
  type: string            # Required: Document type (law, regulation, etc.)
  language: string        # Required: Must be "hebrew"
  version: object         # Required: Version information
  source: object          # Required: Source information
  sections: array         # Required: Array of sections (can be empty)
  authors: array          # Optional: List of authors
  published_date: string  # Optional: Publication date (ISO 8601)
  updated_date: string    # Optional: Last update date (ISO 8601)
```

## Document Fields

### Required Fields

#### `id` (string)

Stable document identifier. Recommended formats:
- UUID: `"550e8400-e29b-41d4-a716-446655440000"`
- Canonical ID: `"law-1234"`

**Example:**
```yaml
id: "law-1234"
```

#### `title` (string)

Document title in Hebrew. Must be at least 1 character.

**Example:**
```yaml
title: "חוק הדוגמה לרגולציה"
```

#### `type` (string)

Type of legal document. Must be one of:
- `"law"` - Law
- `"regulation"` - Regulation
- `"directive"` - Directive
- `"circular"` - Circular
- `"policy"` - Policy
- `"other"` - Other

**Example:**
```yaml
type: "law"
```

#### `language` (string)

Document language. Must be `"hebrew"`.

**Example:**
```yaml
language: "hebrew"
```

#### `version` (object)

Version information object with required `number` field.

**Fields:**
- `number` (string, required): Version identifier or date (e.g., `"2024-01-01"` or `"v1.0"`)
- `description` (string, optional): Version description

**Example:**
```yaml
version:
  number: "2024-01-01"
  description: "גרסה ראשונית"
```

#### `source` (object)

Source information object with required fields.

**Fields:**
- `url` (string, required): Original source URL (must be valid URI)
- `fetched_at` (string, required): ISO 8601 timestamp when document was fetched

**Example:**
```yaml
source:
  url: "https://example.gov.il/law1234"
  fetched_at: "2025-01-20T09:50:00Z"
```

#### `sections` (array)

Array of section objects. Can be empty. Each section follows the recursive Section schema (see below).

**Example:**
```yaml
sections:
  - id: "sec-1"
    marker: "1"
    title: "הגדרות"
    content: "תוכן הסעיף"
    sections: []
```

### Optional Fields

#### `authors` (array of strings)

List of authors, entities, or organizations.

**Example:**
```yaml
authors:
  - "הכנסת"
  - "משרד המשפטים"
```

#### `published_date` (string)

Publication date in ISO 8601 format.

**Example:**
```yaml
published_date: "1992-03-17"
# or
published_date: "1992-03-17T00:00:00Z"
```

#### `updated_date` (string)

Last update date in ISO 8601 format.

**Example:**
```yaml
updated_date: "2024-01-15"
# or
updated_date: "2024-01-15T10:30:00Z"
```

## Section Structure

Sections are recursive and can be nested to unlimited depth. Each section must have:

```yaml
id: string              # Required: Stable section identifier
marker: string          # Required: Structural marker (e.g., "1", "א", "(a)")
sections: array         # Required: Array of nested sections (can be empty)
title: string           # Optional: Section title in Hebrew
content: string         # Optional: Section content (defaults to empty string)
```

### Section Fields

#### `id` (string, required)

Stable section identifier. Must match pattern: `^[a-zA-Z0-9_-]+$`

**Examples:**
- `"sec-1"`
- `"sec-1-a"`
- `"550e8400-e29b-41d4-a716-446655440000"`

#### `marker` (string, required)

Structural marker used for diffing. This is the primary identifier for matching sections across document versions. Must be unique within the same nesting level.

**Examples:**
- `"1"` - Numeric marker
- `"1.א"` - Numeric with Hebrew letter
- `"(א)"` - Hebrew letter in parentheses
- `"II"` - Roman numeral
- `"פרק א'"` - Hebrew chapter marker

**Important:** Markers are preserved verbatim for citation purposes and are used as the primary identifier for diffing (not IDs).

#### `title` (string, optional)

Section title in Hebrew.

**Example:**
```yaml
title: "הגדרות"
```

#### `content` (string, optional)

Text content of this section only (excluding subsections). Defaults to empty string if not provided.

**Example:**
```yaml
content: |
  בחוק זה—
  "מוסד" – גוף הפועל לפי הוראות החוק.
```

#### `sections` (array, required)

Recursive array of nested sections. Can be empty. Each nested section follows the same Section schema.

**Example:**
```yaml
sections:
  - id: "sec-1-1"
    marker: "1"
    title: "תת-סעיף"
    content: "תוכן"
    sections: []
```

## Validation Rules

### Document-Level Rules

1. **All required fields** must be present
2. **`language`** must be exactly `"hebrew"`
3. **`type`** must be one of the allowed values
4. **`source.url`** must be a valid URI
5. **`source.fetched_at`** must be a valid ISO 8601 date-time
6. **`version.number`** must be at least 1 character

### Section-Level Rules

1. **All required fields** (`id`, `marker`, `sections`) must be present
2. **`id`** must match pattern `^[a-zA-Z0-9_-]+$`
3. **`marker`** must be at least 1 character
4. **Markers must be unique** within the same nesting level
5. **`sections`** must be an array (can be empty)

### Recursive Structure

Sections can be nested to unlimited depth:

```yaml
sections:
  - id: "level1"
    marker: "1"
    sections:
      - id: "level2"
        marker: "א"
        sections:
          - id: "level3"
            marker: "(1)"
            sections:
              # ... and so on
```

## Example Documents

### Minimal Valid Document

```yaml
document:
  id: "law-1234"
  title: "חוק הדוגמה"
  type: "law"
  language: "hebrew"
  version:
    number: "2024-01-01"
  source:
    url: "https://example.gov.il/law1234"
    fetched_at: "2025-01-20T09:50:00Z"
  sections: []
```

### Document with Sections

```yaml
document:
  id: "law-1234"
  title: "חוק הדוגמה"
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
      content: |
        בחוק זה—
        "מוסד" – גוף הפועל לפי הוראות החוק.
      sections:
        - id: "sec-1-1"
          marker: "(א)"
          content: "מוסד כולל גם חברות ממשלתיות."
          sections: []
```

## Common Validation Errors

### Missing Required Field

**Error:** `Field required: document.id`

**Solution:** Ensure all required fields are present in the document.

### Invalid Marker

**Error:** `Duplicate marker "1" at same nesting level`

**Solution:** Ensure markers are unique within each nesting level.

### Invalid ID Pattern

**Error:** `Section ID must match pattern ^[a-zA-Z0-9_-]+$`

**Solution:** Use only alphanumeric characters, hyphens, and underscores in section IDs.

### Invalid Language

**Error:** `Language must be "hebrew"`

**Solution:** Set `language: "hebrew"` in the document.

## Schema File Location

The complete OpenSpec schema is located at:
- **File:** `src/yaml_diffs/schema/legal_document_spec.yaml`
- **Version:** 1.0.0
- **Format:** JSON Schema Draft 2020-12 (in YAML format)

## Related Documentation

- [Getting Started](getting_started.md) - Quick start guide
- [Examples Guide](examples.md) - Example documents and templates
- [API Reference](../developer/api_reference.md) - Python API documentation
- [Architecture](../developer/architecture.md) - System architecture
