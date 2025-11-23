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
- **Stable IDs**: All sections must have stable UUIDs for reliable diffing across versions
- **Hebrew Support**: Full UTF-8 support for Hebrew legal text throughout
- **Multiple Interfaces**: Library (Python), CLI (`yaml-diffs`), and REST API (`/api/v1/*`)
- **Schema Validation**: Dual validation via OpenSpec (contract) and Pydantic (runtime)

## CI/CD Status

[![Tests](https://github.com/noamoss/yaml_diffs/actions/workflows/test.yml/badge.svg)](https://github.com/noamoss/yaml_diffs/actions/workflows/test.yml)
[![Lint](https://github.com/noamoss/yaml_diffs/actions/workflows/lint.yml/badge.svg)](https://github.com/noamoss/yaml_diffs/actions/workflows/lint.yml)
[![Build](https://github.com/noamoss/yaml_diffs/actions/workflows/build.yml/badge.svg)](https://github.com/noamoss/yaml_diffs/actions/workflows/build.yml)

## Installation

### Prerequisites

- Python 3.9 or higher
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

> **Note**: The structure below shows the planned/expected project layout. Some files and directories are not yet implemented and will be added in future phases.

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
│       └── api_server/      # FastAPI REST API
├── tests/                   # Test suite
├── examples/                # Example YAML documents
├── docs/                    # Documentation
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

## Usage

### CLI (Coming Soon)

```bash
# Validate a document
yaml-diffs validate examples/minimal_document.yaml

# Diff two documents
yaml-diffs diff examples/document_v1.yaml examples/document_v2.yaml
```

### Python Library (Coming Soon)

```python
from yaml_diffs import load_document, diff_documents

# Load and validate a document
doc = load_document("document.yaml")

# Diff two documents
diff = diff_documents(old_doc, new_doc)
```

### REST API (Coming Soon)

```bash
# Start API server
uvicorn src.yaml_diffs.api_server.main:app --reload --port 8000

# Health check
curl http://localhost:8000/health
```

## Contributing

1. Create a feature branch from `main`
2. Write tests first (TDD approach)
3. Implement feature following code style
4. Ensure all tests pass
5. Update documentation if needed
6. Create pull request

## License

MIT License

## References

- **OpenSpec**: Schema definition standard
- **Pydantic**: Python data validation library
- **FastAPI**: Modern Python web framework
- **Railway**: Deployment platform

## Project Status

This project is in active development. See [GitHub Issues](https://github.com/noamoss/yaml_diffs/issues) for current tasks and progress.
