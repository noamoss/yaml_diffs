# CI/CD Documentation

This document describes the continuous integration and continuous deployment (CI/CD) workflows for the yaml-diffs project.

## Overview

The project uses GitHub Actions to automate testing, linting, building, and deployment. All workflows run automatically on push and pull request events to ensure code quality and compatibility.

## Workflows

### Test Workflow (`.github/workflows/test.yml`)

**Purpose**: Run the test suite across multiple Python versions to ensure compatibility.

**Triggers**:
- Push to `main` branch
- Pull requests to `main` branch

**Features**:
- Tests on Python 3.10, 3.11, and 3.12 using matrix strategy
- Generates coverage reports (XML and terminal output)
- Uploads coverage to Codecov (optional, requires `CODECOV_TOKEN` secret)
- Fails fast on first error

**Steps**:
1. Checkout code
2. Set up Python with version from matrix
3. Install dependencies (`pip install -e ".[dev]"`)
4. Run pytest with coverage
5. Upload coverage reports (Python 3.11 only)

**View Results**: [Tests Workflow](https://github.com/noamoss/yaml_diffs/actions/workflows/test.yml)

### Lint Workflow (`.github/workflows/lint.yml`)

**Purpose**: Ensure code quality through linting, formatting checks, and type checking.

**Triggers**:
- Push to `main` branch
- Pull requests to `main` branch

**Features**:
- Runs ruff for linting
- Checks code formatting with ruff format
- Runs mypy for type checking
- Uses Python 3.11

**Steps**:
1. Checkout code
2. Set up Python 3.11
3. Install linting tools (ruff, mypy)
4. Run ruff check
5. Run ruff format check
6. Install project dependencies
7. Run mypy type checking

**View Results**: [Lint Workflow](https://github.com/noamoss/yaml_diffs/actions/workflows/lint.yml)

### Build Workflow (`.github/workflows/build.yml`)

**Purpose**: Build the package and verify it can be installed correctly.

**Triggers**:
- Push to `main` branch
- Tags matching `v*` pattern
- Pull requests to `main` branch

**Features**:
- Builds package using `python -m build`
- Tests package installation
- Uploads build artifacts (on push to main only)
- Artifacts retained for 30 days

**Steps**:
1. Checkout code
2. Set up Python 3.11
3. Install build tools
4. Build package (wheel and source distribution)
5. Test package installation
6. Upload artifacts (if push to main)

**View Results**: [Build Workflow](https://github.com/noamoss/yaml_diffs/actions/workflows/build.yml)

### Deploy Workflow (`.github/workflows/deploy.yml`)

**Purpose**: Verify Railway deployment health check after automatic deployment.

**Triggers**:
- Push to `main` branch
- Manual trigger via `workflow_dispatch`

**Features**:
- Railway automatically deploys via git integration when code is pushed to main
- Verifies deployment with configurable health check and retry logic
- Only runs on main branch

**Required Secrets**:
- `RAILWAY_DOMAIN`: Railway deployment domain (for health check)

**Optional Variables** (can be set in repository variables):
- `HEALTH_CHECK_TIMEOUT`: Total timeout in seconds (default: 30)
- `HEALTH_CHECK_RETRY_DELAY`: Delay between retries in seconds (default: 5)

**Steps**:
1. Checkout code
2. Wait for Railway auto-deployment (via git integration)
3. Verify deployment health check with retry logic

**View Results**: [Deploy Workflow](https://github.com/noamoss/yaml_diffs/actions/workflows/deploy.yml)

**Note**: This workflow is optional and can be disabled if manual deployment is preferred.

## Dependabot

Dependabot is configured to automatically update dependencies.

**Configuration**: `.github/dependabot.yml`

**Features**:
- Weekly checks for Python dependencies (via `pyproject.toml`)
- Weekly checks for GitHub Actions
- Opens up to 10 pull requests at a time
- Labels PRs with `dependencies` and ecosystem-specific labels

**Note**: This project uses `uv` for dependency management with a `uv.lock` file. Dependabot updates `pyproject.toml` dependencies via the `pip` ecosystem. After merging a Dependabot PR, run `uv lock` locally to update the `uv.lock` file, or configure a workflow to do this automatically.

## Testing Workflows Locally

You can test GitHub Actions workflows locally using [act](https://github.com/nektos/act).

### Installation

```bash
# macOS
brew install act

# Linux (using Homebrew on Linux)
# Or download from: https://github.com/nektos/act/releases
```

### Usage

```bash
# Test the test workflow
act -j test

# Test the lint workflow
act -j lint

# Test the build workflow
act -j build

# List all available jobs
act -l

# Run a specific workflow
act -W .github/workflows/test.yml
```

**Note**: Some workflows may require secrets or environment variables. You can provide these using act's `-s` flag for secrets or `-e` for environment variables.

## Workflow Status Badges

Status badges are displayed in the README to show the current status of each workflow:

```markdown
[![Tests](https://github.com/noamoss/yaml_diffs/actions/workflows/test.yml/badge.svg)](https://github.com/noamoss/yaml_diffs/actions/workflows/test.yml)
[![Lint](https://github.com/noamoss/yaml_diffs/actions/workflows/lint.yml/badge.svg)](https://github.com/noamoss/yaml_diffs/actions/workflows/lint.yml)
[![Build](https://github.com/noamoss/yaml_diffs/actions/workflows/build.yml/badge.svg)](https://github.com/noamoss/yaml_diffs/actions/workflows/build.yml)
```

## Pre-commit and CI/CD Consistency

To ensure consistency between local pre-commit hooks and CI/CD checks:

### Configuration Alignment

- **mypy**: Both pre-commit and CI/CD read configuration from `pyproject.toml`
  - Pre-commit hook explicitly uses `--config-file=pyproject.toml`
  - CI/CD uses `uv run mypy src/` which automatically reads `pyproject.toml`
  - Both use compatible mypy versions (pre-commit v1.8.0+, CI uses mypy>=1.5.0 from dependencies)

- **ruff**: Both use the same configuration from `pyproject.toml`
  - Pre-commit uses ruff-pre-commit v0.14.6
  - CI/CD uses ruff from dependencies (ruff>=0.1.0)

### Version Management

- Pre-commit hook versions are kept compatible with CI/CD dependencies
- When updating dependencies in `pyproject.toml`, consider updating pre-commit hook versions
- Run `pre-commit run --all-files` locally to catch issues before pushing

### Why Pre-commit Might Pass But CI Fails

If pre-commit passes locally but CI fails, check:

1. **Version differences**: Pre-commit hooks may use different tool versions than CI
2. **Configuration**: Ensure both read from the same config files (`pyproject.toml`)
3. **Scope**: Pre-commit runs on staged files, CI runs on entire codebase
4. **Environment**: Different Python/dependency versions between local and CI

To verify consistency:
```bash
# Run the same commands CI uses
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/
```

## Troubleshooting

### Workflow Fails on Tests

1. **Check Python version compatibility**: Ensure your code works on Python 3.9, 3.10, 3.11, and 3.12
2. **Run tests locally**: `pytest` should pass before pushing
3. **Check test output**: View the workflow logs in GitHub Actions

### Workflow Fails on Lint

1. **Run linting locally**: `ruff check src/ tests/`
2. **Check formatting**: `ruff format --check src/ tests/`
3. **Fix formatting**: `ruff format src/ tests/`
4. **Check types**: `mypy src/`

### Workflow Fails on Build

1. **Test build locally**: `python -m build`
2. **Test installation**: `pip install dist/yaml_diffs-*.whl`
3. **Check pyproject.toml**: Ensure build configuration is correct

### Deployment Fails

1. **Check Railway git integration**: Ensure Railway is connected to the repository and auto-deploys on push to main
2. **Check secrets**: Ensure `RAILWAY_DOMAIN` is set in repository secrets
3. **Check variables**: Optionally set `HEALTH_CHECK_TIMEOUT` and `HEALTH_CHECK_RETRY_DELAY` in repository variables
4. **Verify Railway service**: Ensure the service exists and is accessible
5. **Check health endpoint**: Verify `/health` endpoint is available and responding

### Coverage Not Uploading

1. **Codecov token**: Set `CODECOV_TOKEN` secret (optional, workflow will continue without it)
2. **Coverage file**: Ensure `coverage.xml` is generated (only on Python 3.11)

## Best Practices

1. **Run checks locally first**: Always run `pytest`, `ruff check`, and `mypy` before pushing
2. **Keep workflows fast**: Use caching and fail-fast strategies
3. **Test on multiple Python versions**: Ensure compatibility across supported versions
4. **Monitor workflow status**: Check badges in README to see current status
5. **Review Dependabot PRs**: Regularly review and merge dependency updates

## Workflow Dependencies

- **Test Workflow**: Requires comprehensive test suite
- **Deploy Workflow**: Requires REST API service

## Related Documentation

- [REST API Documentation](../api/api_server.md) - API deployment details
- [Contributing Guide](../developer/contributing.md) - Development workflow
- [AGENTS.md](../../AGENTS.md) - AI agent development guide

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [act - Local GitHub Actions Testing](https://github.com/nektos/act)
- [Railway Documentation](https://docs.railway.app/)
- [Codecov Documentation](https://docs.codecov.com/)
