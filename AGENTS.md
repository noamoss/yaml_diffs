# AGENTS.md

This file provides essential context and instructions for AI coding agents working on this codebase. It complements the `README.md` which is intended for human developers.

## Project Overview

**yaml-diffs** is a Python service for representing Hebrew legal and regulatory documents in a flexible, nested YAML format. The service provides:

- **Schema Layer**: OpenSpec definition (language-agnostic contract) for document structure
- **Model Layer**: Pydantic models for Python runtime validation
- **Core Logic**: Document diffing, validation, and transformation utilities
- **Interface Layer**: Python library API, CLI tool, and REST API (FastAPI)
- **Deployment**: Railway-hosted REST API service

The project supports unlimited nesting, flexible structural markers, Hebrew content, and provides foundation for RAG integration with exact citation tracking.

### Key Architecture Points

- **Recursive Structure**: Documents use recursive sections with unlimited nesting depth
- **Stable IDs**: All sections must have stable UUIDs for reliable diffing across versions
- **Hebrew Support**: Full UTF-8 support for Hebrew legal text throughout
- **Multiple Interfaces**: Library (Python), CLI (`yaml-diffs`), and REST API (`/api/v1/*`)
- **Schema Validation**: Dual validation via OpenSpec (contract) and Pydantic (runtime)

## Development Environment Setup

### Prerequisites

- Python 3.9 or higher
- uv (install via: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Git

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/noamoss/yaml_diffs.git
cd yaml_diffs

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode (includes dev dependencies)
uv sync --extra dev

# Or install without dev dependencies
uv sync
```

### Environment Variables

For local development of the API server:

```bash
# Copy example environment file (when created)
cp .env.example .env

# Required for Railway deployment
PORT=8000  # Railway sets this automatically
```

## Project Structure

```
yaml-diffs/
├── src/
│   └── yaml_diffs/
│       ├── __init__.py
│       ├── api.py              # Main library API
│       ├── loader.py           # YAML loading utilities
│       ├── validator.py        # Validation logic
│       ├── diff.py              # Document diffing engine
│       ├── diff_types.py        # Diff result types
│       ├── exceptions.py        # Custom exceptions
│       ├── models/              # Pydantic models
│       │   ├── document.py
│       │   └── section.py
│       ├── schema/              # OpenSpec schema
│       │   └── legal_document_spec.yaml
│       ├── formatters/          # Diff output formatters
│       │   ├── json_formatter.py
│       │   ├── text_formatter.py
│       │   └── yaml_formatter.py
│       ├── cli/                 # CLI tool
│       │   ├── main.py
│       │   └── commands.py
│       └── api_server/          # FastAPI REST API
│           ├── main.py
│           ├── config.py
│           ├── routers/
│           │   ├── validate.py
│           │   ├── diff.py
│           │   └── health.py
│           └── schemas.py
├── tests/                       # Test suite
│   ├── test_models.py
│   ├── test_loader.py
│   ├── test_validator.py
│   ├── test_diff.py
│   ├── test_formatters.py
│   ├── test_api.py
│   ├── test_cli.py
│   └── test_api_server.py
├── examples/                    # Example YAML documents
├── docs/                         # Documentation
├── .github/                      # GitHub configuration
│   └── workflows/                # GitHub Actions workflows
│       ├── test.yml              # Test workflow
│       ├── lint.yml              # Linting workflow
│       ├── build.yml             # Build workflow
│       └── deploy.yml            # Deployment workflow (optional)
├── pyproject.toml               # Project configuration
└── README.md                    # Human-facing documentation
```

## Build and Test Commands

### Development Commands

```bash
# Install in development mode
uv sync --extra dev

# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/yaml_diffs --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run tests in watch mode (if configured)
pytest-watch

# Type checking (if mypy is configured)
mypy src/

# Linting
ruff check src/ tests/

# Format code
ruff format src/ tests/
```

### CI/CD Workflows

**GitHub Actions automatically runs these checks on every push and pull request:**

- **Test Workflow** (`.github/workflows/test.yml`): Runs tests on Python 3.9, 3.10, 3.11, 3.12
- **Lint Workflow** (`.github/workflows/lint.yml`): Runs ruff linting, formatting checks, and mypy type checking
- **Build Workflow** (`.github/workflows/build.yml`): Builds package and tests installation (runs on push to main)
- **Deploy Workflow** (`.github/workflows/deploy.yml`): Optional automated deployment to Railway

**Testing workflows locally (optional):**
```bash
# Install act (GitHub Actions local runner)
# macOS: brew install act
# Then test a workflow:
act -j test        # Test the test workflow
act -j lint        # Test the lint workflow
```

**Important for AI Agents:**
- All PRs must pass CI checks before merging
- Run `pytest`, `ruff check`, and `mypy` locally before pushing
- CI runs on multiple Python versions - ensure compatibility

### Build Commands

```bash
# Build package
python -m build

# Install from built package
uv pip install dist/yaml_diffs-*.whl
```

### CLI Usage

```bash
# Validate a document
yaml-diffs validate examples/minimal_document.yaml

# Diff two documents
yaml-diffs diff examples/document_v1.yaml examples/document_v2.yaml

# Diff with JSON output
yaml-diffs diff --format json old.yaml new.yaml

# Save diff to file
yaml-diffs diff --output diff.json old.yaml new.yaml
```

### API Server Commands

```bash
# Run API server locally
uvicorn src.yaml_diffs.api_server.main:app --reload --port 8000

# Run with Railway port (production)
uvicorn src.yaml_diffs.api_server.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## Code Style and Conventions

### Python Style

- **Python Version**: 3.9+
- **Code Style**: Follow PEP 8
- **Type Hints**: Use type hints throughout (Pydantic models, function signatures)
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Line Length**: 100 characters maximum
- **Imports**: Use absolute imports, organize with `isort` or similar

### Naming Conventions

- **Modules**: `snake_case` (e.g., `document_diff.py`)
- **Classes**: `PascalCase` (e.g., `Document`, `Section`)
- **Functions/Methods**: `snake_case` (e.g., `load_document()`, `diff_documents()`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_ENCODING`)
- **Private**: Prefix with `_` (e.g., `_internal_helper()`)

### File Organization

- **One class per file** for models (e.g., `document.py`, `section.py`)
- **Group related functions** in modules (e.g., `loader.py`, `validator.py`)
- **Keep modules focused** - each module should have a single responsibility

### YAML Handling

- **Encoding**: Always use UTF-8 for YAML files
- **Hebrew Content**: Ensure proper UTF-8 encoding when reading/writing Hebrew text
- **YAML Library**: Use `pyyaml` with `safe_load()` for parsing
- **Preserve Structure**: Maintain document structure when loading/validating

### Error Handling

- **Custom Exceptions**: Use custom exceptions from `exceptions.py`
- **Clear Messages**: Provide actionable error messages
- **Validation Errors**: Include field paths and expected values in validation errors

## Testing Guidelines

### Testing Framework

- **Framework**: pytest
- **Coverage Target**: >80% code coverage
- **Test Location**: All tests in `tests/` directory
- **Fixtures**: Use `conftest.py` for shared fixtures

### Test Organization

- **Unit Tests**: Test individual functions and classes in isolation
- **Integration Tests**: Test workflows and component interactions
- **Acceptance Tests**: Test end-to-end user scenarios
- **Performance Tests**: Test with large documents (in `tests/performance/`)

### Testing Conventions

- **Test Names**: Descriptive, no "should" prefix (e.g., `test_load_valid_yaml_document`)
- **Arrange-Act-Assert**: Follow AAA pattern in tests
- **Fixtures**: Use pytest fixtures for test data and setup
- **Mocking**: Mock external dependencies (file I/O, network calls)
- **Hebrew Content**: Include tests with actual Hebrew text
- **CI Validation**: All tests must pass in CI before PR can be merged

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_models.py::test_create_section_with_all_fields

# Run with coverage
pytest --cov=src/yaml_diffs --cov-report=term-missing

# Run only fast tests (exclude performance)
pytest -m "not slow"
```

## Security Considerations

### Data Handling

- **Input Validation**: Always validate YAML input before processing
- **File Paths**: Sanitize file paths to prevent directory traversal
- **YAML Safety**: Use `yaml.safe_load()` to prevent code execution
- **Size Limits**: Consider file size limits for API endpoints

### Secrets Management

- **No Secrets in Code**: Never commit API keys, tokens, or passwords
- **Environment Variables**: Use environment variables for configuration
- **`.env.example`**: Provide example file without actual secrets
- **Railway Secrets**: Use Railway's environment variable management
- **GitHub Secrets**: Store sensitive values (e.g., `RAILWAY_TOKEN`) in GitHub repository secrets for CI/CD workflows

### API Security

- **CORS**: Configure CORS appropriately for production
- **Rate Limiting**: Consider rate limiting for public API endpoints
- **Input Validation**: Validate all API request payloads
- **Error Messages**: Don't expose internal details in error responses

## Configuration Management

### Environment Configuration

- **Development**: Use `.env` file (not committed)
- **Production**: Use Railway environment variables
- **Example**: Provide `.env.example` with required variables

### Configuration Files

- **`pyproject.toml`**: Project metadata, dependencies, build config
- **`railway.json`**: Railway deployment configuration
- **`.env.example`**: Example environment variables
- **`.github/workflows/`**: GitHub Actions workflow definitions
- **`.github/dependabot.yml`**: Dependabot configuration for dependency updates

### Railway Deployment

- **Port Binding**: Read `PORT` from environment variable
- **Host Binding**: Bind to `0.0.0.0` for Railway
- **Health Check**: Implement `/health` endpoint for Railway monitoring
- **Logging**: Configure production logging for Railway

## Key Implementation Details

### Document Schema

- **Stable IDs**: All sections must have stable UUIDs (auto-generated if not provided). IDs are used for tracking but not for matching.
- **Markers Required**: All sections must have a marker (required field). Markers are the primary identifiers for diffing.
- **Recursive Structure**: Sections can contain nested sections to unlimited depth
- **Optional Fields**: `title` is optional; `id`, `marker`, and `content` are required
- **Content Field**: Contains only text for this section level (not children)

### Diffing Logic

- **Marker-Based**: Diffing is based on section markers (not IDs). Markers are the primary identifiers used for matching sections across document versions.
- **Marker Requirement**: All sections must have a marker (required field). Markers must be unique within the same nesting level.
- **Change Types**:
  - `SECTION_ADDED`: New section added in new version
  - `SECTION_REMOVED`: Section removed from old version
  - `CONTENT_CHANGED`: Content changed (same marker+path)
  - `SECTION_MOVED`: Path changed (and possibly marker changed) but title+content same
  - `TITLE_CHANGED`: Title changed (same marker+path+content)
  - `UNCHANGED`: No changes detected
- **Path Tracking**: Hybrid approach - uses marker paths for matching, ID paths for tracking
- **Movement Detection**: Sections are detected as moved when path changed (and possibly marker changed) but title+content are the same. Matching is done by content similarity (≥0.95 threshold), not marker. Empty content sections (parent sections) are not matched to avoid false positives.
- **Content Similarity**: Uses content similarity scoring (≥0.95 threshold) to detect moved sections. Only sections with non-empty content are matched.
- **Multiple Changes**: A single section can have multiple change types (e.g., SECTION_MOVED + CONTENT_CHANGED as separate entries)
- **Nested Handling**: Handle deeply nested structures correctly (5+ levels)

### API Design

- **RESTful**: Follow REST conventions for API endpoints
- **Versioning**: Use `/api/v1/` prefix for API versioning
- **OpenAPI**: FastAPI auto-generates OpenAPI/Swagger documentation
- **Error Responses**: Consistent error response format

## Common Tasks for AI Agents

### Adding a New Feature

1. Create feature branch from `main`
2. Write tests first (TDD approach)
3. Implement feature following code style
4. Ensure all tests pass locally (`pytest`, `ruff check`, `mypy`)
5. Update documentation if needed
6. Create pull request
7. **CI will automatically validate**: Tests, linting, type checking must pass before merge

### Fixing a Bug

1. Reproduce the bug with a test case
2. Fix the bug
3. Ensure test passes
4. Run full test suite locally
5. Verify linting and type checking pass
6. Update documentation if behavior changed
7. **CI will validate**: All checks must pass before PR can be merged

### Working with Hebrew Content

- Always use UTF-8 encoding
- Test with actual Hebrew text, not placeholders
- Ensure YAML files are saved with UTF-8 encoding
- Verify Hebrew text displays correctly in outputs

### Modifying the Schema

1. Update OpenSpec schema first (`schema/legal_document_spec.yaml`)
2. Update Pydantic models to match
3. Update validation logic
4. Update tests
5. Update examples
6. Update documentation

## References

- **OpenSpec**: Schema definition standard
- **Pydantic**: Python data validation library
- **FastAPI**: Modern Python web framework
- **Railway**: Deployment platform
- **GitHub Actions**: CI/CD workflow automation
- **Project Issues**: See GitHub issues for task tracking
- **Project Board**: https://github.com/users/noamoss/projects/4
- **CI/CD Documentation**: See `docs/operations/ci_cd.md` for workflow details
- **Documentation Index**: See `docs/README.md` for complete documentation overview

## Documentation Maintenance

### Documentation Organization

Documentation is organized hierarchically by audience:

```
docs/
├── user/                    # User-facing documentation
│   ├── getting_started.md
│   ├── examples.md
│   └── schema_reference.md
├── developer/               # Developer documentation
│   ├── architecture.md
│   ├── contributing.md
│   └── api_reference.md
├── api/                     # API documentation
│   ├── api_server.md
│   └── mcp_server.md
└── operations/              # Operations documentation
    └── ci_cd.md
```

### When to Update Documentation

Update documentation when:
- **Adding new features** - Document new functionality
- **Changing existing behavior** - Update affected documentation
- **Fixing bugs** - Update if behavior changes
- **Adding examples** - Update examples guide
- **Changing API** - Update API reference
- **Moving files** - Update all cross-references

### Documentation Standards

#### Structure Standards
- Use hierarchical organization by audience (user/developer/api/operations)
- Each doc should have clear purpose and audience
- Include table of contents for long documents
- Use consistent heading structure

#### Content Standards
- All code examples must be valid and tested
- Include Hebrew content examples where relevant
- Link to related documentation
- Keep examples up-to-date with code
- Use clear, concise language

#### Cross-Reference Maintenance
- Use relative paths for internal links
- Update links when files are moved
- Test all links after reorganization
- Use consistent link format: `[text](path/to/file.md)`

### Documentation Testing

Before committing documentation changes:

1. **Test code examples:**
   ```bash
   # Verify Python examples are valid
   python -c "from yaml_diffs import ..."

   # Verify YAML examples validate
   yaml-diffs validate examples/your_example.yaml
   ```

2. **Check links:**
   - Verify all internal links work
   - Check external links are accessible
   - Ensure cross-references are correct

3. **Validate markdown:**
   - Ensure markdown renders correctly
   - Check formatting is consistent
   - Verify code blocks have proper syntax highlighting

### Documentation File Locations

- **User docs**: `docs/user/`
- **Developer docs**: `docs/developer/`
- **API docs**: `docs/api/`
- **Operations docs**: `docs/operations/`
- **Documentation index**: `docs/README.md`
- **Main README**: `README.md`
- **AI agent guide**: `AGENTS.md`

### Updating Cross-References

When moving or renaming documentation files:

1. **Update all references** in:
   - Other documentation files
   - `README.md`
   - `AGENTS.md`
   - Code docstrings (if they reference docs)

2. **Use relative paths:**
   ```markdown
   # From docs/user/getting_started.md
   [Schema Reference](schema_reference.md)
   [API Reference](../developer/api_reference.md)
   [Main README](../../README.md)
   ```

3. **Test all links** after changes

### Documentation Maintenance Checklist

When making code changes, check:

- [ ] Is documentation needed for this change?
- [ ] Are code examples in docs still valid?
- [ ] Do links still work?
- [ ] Are cross-references correct?
- [ ] Is the documentation index updated?
- [ ] Are examples synchronized with code?

## Notes for AI Agents

- **Always validate** YAML documents before processing
- **Preserve structure** when loading/transforming documents
- **Handle Hebrew text** correctly (UTF-8 encoding)
- **Use stable IDs** for all sections to enable reliable diffing
- **Test thoroughly** with both minimal and complex examples
- **Follow dependencies** - check task dependencies before starting work
- **Update tests** when modifying functionality
- **Update documentation** when code changes (see Documentation Maintenance section above)
- **Check existing issues** before creating new ones
- **CI/CD Validation**: Always run `pytest`, `ruff check`, and `mypy` locally before pushing - CI will fail if these don't pass
- **Python Version Compatibility**: Ensure code works on Python 3.10, 3.11, 3.12 (CI tests all versions)
- **Pre-commit Consistency**: Pre-commit hooks are configured to match CI/CD checks. Both use the same configuration from `pyproject.toml`. If pre-commit passes but CI fails, check version differences or run `uv run mypy src/` locally to match CI exactly.
