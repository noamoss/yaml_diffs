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
- Tests on Python 3.9, 3.10, 3.11, and 3.12 using matrix strategy
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

**Purpose**: Automatically deploy to Railway when changes are pushed to main.

**Triggers**:
- Push to `main` branch
- Manual trigger via `workflow_dispatch`

**Features**:
- Deploys to Railway using Railway CLI
- Verifies deployment with health check
- Only runs on main branch

**Required Secrets**:
- `RAILWAY_TOKEN`: Railway authentication token
- `RAILWAY_SERVICE_ID`: Railway service ID
- `RAILWAY_DOMAIN`: Railway deployment domain (for health check)

**Steps**:
1. Checkout code
2. Deploy to Railway
3. Verify deployment health check

**View Results**: [Deploy Workflow](https://github.com/noamoss/yaml_diffs/actions/workflows/deploy.yml)

**Note**: This workflow is optional and can be disabled if manual deployment is preferred.

## Dependabot

Dependabot is configured to automatically update dependencies.

**Configuration**: `.github/dependabot.yml`

**Features**:
- Weekly checks for Python dependencies
- Weekly checks for GitHub Actions
- Opens up to 10 pull requests at a time
- Labels PRs with `dependencies` and ecosystem-specific labels

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

1. **Check secrets**: Ensure `RAILWAY_TOKEN`, `RAILWAY_SERVICE_ID`, and `RAILWAY_DOMAIN` are set
2. **Verify Railway service**: Ensure the service exists and is accessible
3. **Check health endpoint**: Verify `/health` endpoint is available

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

- **Test Workflow**: Requires comprehensive test suite (Task 5.1)
- **Deploy Workflow**: Requires REST API service (Task 3.3)

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [act - Local GitHub Actions Testing](https://github.com/nektos/act)
- [Railway Documentation](https://docs.railway.app/)
- [Codecov Documentation](https://docs.codecov.com/)


