# Contributing

Thank you for your interest in contributing to yaml-diffs! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- uv (recommended) or pip
- Git

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/noamoss/yaml_diffs.git
cd yaml_diffs

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv sync --extra dev

# Install pre-commit hooks
pre-commit install
```

### Verify Setup

```bash
# Run tests
pytest

# Run linting
ruff check src/ tests/

# Run type checking
mypy src/
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following the style guidelines
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/yaml_diffs --cov-report=html

# Run specific test file
pytest tests/test_your_feature.py

# Run linting
ruff check src/ tests/

# Run type checking
mypy src/

# Format code
ruff format src/ tests/
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

**Commit Message Guidelines:**
- Use conventional commits format: `type: description`
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`
- Keep descriptions clear and concise

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style

### Python Style

- **Python Version**: 3.10+
- **Code Style**: Follow PEP 8
- **Type Hints**: Use type hints throughout
- **Docstrings**: Use Google-style docstrings
- **Line Length**: 100 characters maximum

### Naming Conventions

- **Modules**: `snake_case` (e.g., `document_diff.py`)
- **Classes**: `PascalCase` (e.g., `Document`, `Section`)
- **Functions/Methods**: `snake_case` (e.g., `load_document()`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_ENCODING`)
- **Private**: Prefix with `_` (e.g., `_internal_helper()`)

### Code Formatting

We use `ruff` for formatting and linting:

```bash
# Format code
ruff format src/ tests/

# Check formatting
ruff format --check src/ tests/

# Lint code
ruff check src/ tests/
```

### Type Hints

Always use type hints for function signatures:

```python
def load_document(file_path: str | Path | TextIO) -> Document:
    """Load a YAML document."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def diff_documents(old: Document, new: Document) -> DocumentDiff:
    """Compare two Document versions and detect changes.

    Args:
        old: Old document version
        new: New document version

    Returns:
        DocumentDiff containing all detected changes

    Raises:
        ValueError: If duplicate markers found at same level

    Example:
        >>> old_doc = load_document("v1.yaml")
        >>> new_doc = load_document("v2.yaml")
        >>> diff = diff_documents(old_doc, new_doc)
        >>> print(f"Changes: {len(diff.changes)}")
    """
    ...
```

## Testing

### Test Organization

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Acceptance Tests**: Test end-to-end workflows

### Writing Tests

```python
def test_load_valid_document():
    """Test loading a valid YAML document."""
    doc = load_document("examples/minimal_document.yaml")
    assert doc.id == "law-1234"
    assert doc.title == "חוק הדוגמה לרגולציה"
    assert len(doc.sections) > 0
```

### Test Conventions

- **Test Names**: Descriptive, no "should" prefix
- **Arrange-Act-Assert**: Follow AAA pattern
- **Fixtures**: Use pytest fixtures for test data
- **Hebrew Content**: Include tests with actual Hebrew text

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_models.py::test_create_section

# Run with coverage
pytest --cov=src/yaml_diffs --cov-report=term-missing

# Run only fast tests
pytest -m "not slow"
```

## Documentation

### When to Update Documentation

Update documentation when:
- Adding new features
- Changing existing behavior
- Fixing bugs that affect user-facing behavior
- Adding new examples or use cases

### Documentation Standards

- **Markdown format** with clear structure
- **Code examples** must be valid and tested
- **Hebrew content** examples where relevant
- **Cross-references** to related documentation
- **Table of contents** for long documents

### Documentation Structure

Documentation is organized by audience:

- `docs/user/` - User-facing documentation
- `docs/developer/` - Developer documentation
- `docs/api/` - API documentation
- `docs/operations/` - Operations documentation

See [Documentation Maintenance](#documentation) section below for details.

### Updating Documentation

1. **Identify the right location** based on audience
2. **Update or create** the documentation file
3. **Test code examples** in the documentation
4. **Update cross-references** if files moved
5. **Verify links** work correctly

## Pull Request Process

### Before Submitting

1. **Run all checks locally:**
   ```bash
   pytest
   ruff check src/ tests/
   ruff format --check src/ tests/
   mypy src/
   ```

2. **Ensure tests pass** on all supported Python versions (3.10, 3.11, 3.12)

3. **Update documentation** if needed

4. **Add changelog entry** if applicable

### PR Requirements

- All tests must pass
- Code must be linted and formatted
- Type checking must pass
- Documentation must be updated
- PR description should explain changes

### Review Process

1. **Automated checks** run on every PR
2. **Code review** by maintainers
3. **Address feedback** and update PR
4. **Merge** when approved

## AI Agent Development

If you're an AI coding agent working on this project, see [AGENTS.md](../../AGENTS.md) for specific guidelines and best practices.

## Common Tasks

### Adding a New Feature

1. Create feature branch
2. Write tests first (TDD approach)
3. Implement feature
4. Update documentation
5. Run all checks
6. Create PR

### Fixing a Bug

1. Reproduce the bug with a test
2. Fix the bug
3. Ensure test passes
4. Run full test suite
5. Update documentation if behavior changed
6. Create PR

### Adding a New Formatter

1. Create formatter in `src/yaml_diffs/formatters/`
2. Implement formatter interface
3. Register in `__init__.py`
4. Add to `format_diff()` function
5. Write tests
6. Update documentation

## Questions?

- **Issues**: [GitHub Issues](https://github.com/noamoss/yaml_diffs/issues)
- **Documentation**: [Documentation Index](../README.md)
- **AI Agents**: [AGENTS.md](../../AGENTS.md)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).
