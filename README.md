# yaml-diffs

Python service for representing Hebrew legal and regulatory documents in a flexible, nested YAML format.

## Overview

**yaml-diffs** provides a comprehensive solution for working with Hebrew legal documents in YAML format, offering:

- **Schema Layer**: OpenSpec definition (language-agnostic contract) for document structure
- **Model Layer**: Pydantic models for Python runtime validation
- **Core Logic**: Document diffing, validation, and transformation utilities
- **Interface Layer**: Python library API, CLI tool, and REST API (FastAPI)
- **Deployment**: Railway-hosted REST API service

The project supports unlimited nesting, flexible structural markers, Hebrew content, and provides foundation for RAG integration with exact citation tracking.

## Key Features

- **Recursive Structure**: Documents use recursive sections with unlimited nesting depth
- **Marker-Based Diffing**: Sections are matched by markers (not IDs) for reliable diffing across versions. All sections must have unique markers at each nesting level.
- **Hebrew Support**: Full UTF-8 support for Hebrew legal text throughout
- **Multiple Interfaces**: Library (Python), CLI (`yaml-diffs`), REST API (`/api/v1/*`), and MCP Server
- **Schema Validation**: Dual validation via OpenSpec (contract) and Pydantic (runtime)

## CI/CD Status

[![Tests](https://github.com/noamoss/yaml_diffs/actions/workflows/test.yml/badge.svg)](https://github.com/noamoss/yaml_diffs/actions/workflows/test.yml)
[![Lint](https://github.com/noamoss/yaml_diffs/actions/workflows/lint.yml/badge.svg)](https://github.com/noamoss/yaml_diffs/actions/workflows/lint.yml)
[![Build](https://github.com/noamoss/yaml_diffs/actions/workflows/build.yml/badge.svg)](https://github.com/noamoss/yaml_diffs/actions/workflows/build.yml)

## Installation

### Prerequisites

- Python 3.10 or higher (required for MCP server support)
- uv (install via: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/noamoss/yaml_diffs.git
cd yaml_diffs

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv sync --extra dev

# Install pre-commit hooks
pre-commit install
```

## Project Structure

```
yaml-diffs/
├── src/
│   └── yaml_diffs/          # Main package
│       ├── __init__.py
│       ├── api.py           # Main library API
│       ├── loader.py        # YAML loading utilities
│       ├── validator.py     # Validation logic
│       ├── diff.py          # Document diffing engine
│       ├── models/          # Pydantic models
│       ├── schema/          # OpenSpec schema
│       ├── formatters/      # Diff output formatters
│       ├── cli/             # CLI tool
│       ├── api_server/      # FastAPI REST API
│       └── mcp_server/      # MCP server for AI assistants
├── tests/                   # Test suite
├── examples/                # Example YAML documents
│   ├── minimal_document.yaml
│   ├── complex_document.yaml
│   ├── document_v1.yaml
│   ├── document_v2.yaml
│   └── template.yaml
├── docs/                    # Documentation
│   ├── user/                # User-facing documentation
│   ├── developer/           # Developer documentation
│   ├── api/                 # API documentation
│   └── operations/          # Operations documentation
├── pyproject.toml           # Project configuration
└── README.md               # This file
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/yaml_diffs --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run tests in watch mode
pytest-watch
```

### Code Quality

```bash
# Linting
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Type checking
mypy src/
```

### Building

```bash
# Build package
python -m build

# Install from built package
uv pip install dist/yaml_diffs-*.whl
```

## Quick Start

### Python Library

```python
from yaml_diffs import load_document, diff_documents, format_diff

# Load a document
doc = load_document("examples/minimal_document.yaml")
print(f"Document: {doc.title}")

# Diff two documents
old_doc = load_document("examples/document_v1.yaml")
new_doc = load_document("examples/document_v2.yaml")
diff = diff_documents(old_doc, new_doc)

# Format the results
json_output = format_diff(diff, output_format="json")
print(json_output)
```

### CLI

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

```bash
# Start API server
uvicorn src.yaml_diffs.api_server.main:app --reload --port 8000

# Validate a document
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{"yaml": "document:\n  id: \"test\"\n  ..."}'

# Diff two documents
curl -X POST http://localhost:8000/api/v1/diff \
  -H "Content-Type: application/json" \
  -d '{"old_yaml": "...", "new_yaml": "..."}'

# Health check
curl http://localhost:8000/health
```

The API also provides interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### MCP Server

The MCP (Model Context Protocol) server exposes the REST API endpoints as MCP tools, enabling AI assistants to interact with the yaml-diffs service.

**Quick Start:**

```bash
# Run MCP server (connects to local API by default)
yaml-diffs mcp-server

# Or with custom configuration
yaml-diffs mcp-server --api-url http://api.example.com:8000 --api-key your-key
```

**Available Tools:**
- `validate_document`: Validate a YAML document
- `diff_documents`: Compare two YAML documents
- `health_check`: Check API health status

**Configuration:**
- `YAML_DIFFS_API_URL`: API base URL (default: `http://localhost:8000`)
- `YAML_DIFFS_API_KEY`: Optional API key for authentication
- `YAML_DIFFS_API_TIMEOUT`: Request timeout in seconds (default: `30`)

For detailed MCP server documentation, see [docs/api/mcp_server.md](docs/api/mcp_server.md).

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Getting Started](docs/user/getting_started.md)** - Quick start guide with installation and basic usage
- **[Schema Reference](docs/user/schema_reference.md)** - Complete OpenSpec schema documentation
- **[Examples Guide](docs/user/examples.md)** - How to use example documents and templates
- **[API Reference](docs/developer/api_reference.md)** - Complete Python library API reference
- **[Architecture](docs/developer/architecture.md)** - System architecture and design decisions
- **[Contributing](docs/developer/contributing.md)** - How to contribute to the project
- **[REST API](docs/api/api_server.md)** - REST API documentation
- **[MCP Server](docs/api/mcp_server.md)** - MCP server for AI assistants
- **[CI/CD](docs/operations/ci_cd.md)** - Continuous integration and deployment workflows

See the [Documentation Index](docs/README.md) for a complete overview.

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/developer/contributing.md) for details.

**Quick Start:**
1. Create a feature branch from `main`
2. Write tests first (TDD approach)
3. Implement feature following code style
4. Ensure all tests pass (`pytest`, `ruff check`, `mypy`)
5. Update documentation if needed
6. Create pull request

For AI coding agents, see [AGENTS.md](AGENTS.md) for specific guidelines.

## License

MIT License

## Examples

The `examples/` directory contains example documents:

- **`minimal_document.yaml`** - Minimal valid document with all required fields
- **`complex_document.yaml`** - Complex document with deep nesting (5+ levels)
- **`document_v1.yaml`** and **`document_v2.yaml`** - Example versions for diffing
- **`template.yaml`** - Template for creating new documents

See the [Examples Guide](docs/user/examples.md) and [Examples README](examples/README.md) for details.

## References

- **OpenSpec**: Schema definition standard
- **Pydantic**: Python data validation library
- **FastAPI**: Modern Python web framework
- **Railway**: Deployment platform
- **GitHub Actions**: CI/CD workflow automation

## Project Status

This project is in active development. See [GitHub Issues](https://github.com/noamoss/yaml_diffs/issues) for current tasks and progress.

## Getting Help

- **Documentation**: [Documentation Index](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/noamoss/yaml_diffs/issues)
- **Project Board**: [GitHub Project Board](https://github.com/users/noamoss/projects/4)
