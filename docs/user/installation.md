# Installation Guide

This guide covers all methods for installing the yaml-diffs package, from PyPI, source, or for development.

## Prerequisites

- **Python 3.10 or higher** (required)
- **pip** or **uv** for package management
- **Git** (for source installation)

## Installation Methods

### Install from PyPI (Recommended)

Once the package is published to PyPI, you can install it using pip:

```bash
pip install yaml-diffs
```

Or using uv (faster):

```bash
uv pip install yaml-diffs
```

### Install from Source

If you want to install from the latest source code:

```bash
# Clone the repository
git clone https://github.com/noamoss/yaml_diffs.git
cd yaml_diffs

# Install the package
pip install .
```

Or using uv:

```bash
uv pip install .
```

### Install for Development

For development work, install in editable mode with development dependencies:

```bash
# Clone the repository
git clone https://github.com/noamoss/yaml_diffs.git
cd yaml_diffs

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

Or using uv:

```bash
# Clone the repository
git clone https://github.com/noamoss/yaml_diffs.git
cd yaml_diffs

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync --extra dev
```

## Verification

After installation, verify that the package is installed correctly:

### 1. Verify Package Installation

Check that the package can be imported:

```bash
python -c "import yaml_diffs; print(f'yaml-diffs version: {yaml_diffs.__version__}')"
```

Expected output:
```
yaml-diffs version: 0.1.0
```

### 2. Verify CLI Installation

Check that the CLI command is available:

```bash
yaml-diffs --version
```

Expected output:
```
yaml-diffs, version 0.1.0
```

### 3. Test CLI Functionality

Test the validate command:

```bash
# Create a minimal test file
cat > test_doc.yaml << 'EOF'
document:
  id: "test-123"
  title: "Test Document"
  sections:
    - id: "sec-1"
      marker: "1"
      content: "Test content"
EOF

# Validate it
yaml-diffs validate test_doc.yaml
```

If validation passes, you should see no errors.

### 4. Test Library Imports

Verify that all main components can be imported:

```python
python -c "
from yaml_diffs import (
    load_document,
    validate_document,
    diff_documents,
    format_diff,
    Document,
    Section,
    __version__
)
print('All imports successful!')
print(f'Version: {__version__}')
"
```

### 5. Verify Schema File Access

Check that the schema file is accessible:

```python
python -c "
from yaml_diffs.schema import load_schema
schema = load_schema()
assert schema is not None
assert 'version' in schema or 'info' in schema
print('Schema file accessible!')
"
```

## Building from Source

If you want to build the package yourself:

```bash
# Install build tools
pip install build

# Build the package
python -m build

# This creates:
# - dist/yaml_diffs-*.whl (wheel distribution)
# - dist/yaml_diffs-*.tar.gz (source distribution)
```

### Install from Built Package

After building, you can install from the built wheel:

```bash
pip install dist/yaml_diffs-*.whl
```

Or test installation in a clean environment:

```bash
# Create a temporary virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install the built package
pip install dist/yaml_diffs-*.whl

# Test it
yaml-diffs --version
python -c "import yaml_diffs; print(yaml_diffs.__version__)"
```

## Troubleshooting

### CLI Command Not Found

If `yaml-diffs` command is not found after installation:

1. **Check installation location:**
   ```bash
   pip show yaml-diffs
   ```

2. **Verify Python scripts directory is in PATH:**
   ```bash
   python -m site --user-base
   ```
   Add the `bin` (or `Scripts` on Windows) directory to your PATH.

3. **Reinstall the package:**
   ```bash
   pip uninstall yaml-diffs
   pip install yaml-diffs
   ```

### Import Errors

If you get import errors:

1. **Verify Python version:**
   ```bash
   python --version  # Should be 3.10 or higher
   ```

2. **Check if package is installed:**
   ```bash
   pip list | grep yaml-diffs
   ```

3. **Reinstall in a clean environment:**
   ```bash
   python -m venv clean_env
   source clean_env/bin/activate
   pip install yaml-diffs
   ```

### Schema File Not Found

If you get errors about missing schema files:

1. **Verify MANIFEST.in includes schema files:**
   The schema files should be included in the package distribution.

2. **Check package contents:**
   ```bash
   pip show -f yaml-diffs | grep schema
   ```

3. **Reinstall from source:**
   ```bash
   pip uninstall yaml-diffs
   pip install .
   ```

### Version Mismatch

If the version doesn't match expectations:

1. **Check installed version:**
   ```bash
   pip show yaml-diffs
   ```

2. **Check version in code:**
   ```python
   python -c "import yaml_diffs; print(yaml_diffs.__version__)"
   ```

3. **Reinstall latest version:**
   ```bash
   pip install --upgrade yaml-diffs
   ```

## Uninstallation

To uninstall the package:

```bash
pip uninstall yaml-diffs
```

## Next Steps

After successful installation:

- Read the [Getting Started Guide](getting_started.md) for basic usage
- Check out the [Examples Guide](examples.md) for usage examples
- Review the [Schema Reference](schema_reference.md) for document structure
- See the [API Reference](../developer/api_reference.md) for detailed API documentation

## Additional Resources

- **GitHub Repository**: https://github.com/noamoss/yaml_diffs
- **Issue Tracker**: https://github.com/noamoss/yaml_diffs/issues
- **Documentation**: https://github.com/noamoss/yaml_diffs/tree/main/docs
