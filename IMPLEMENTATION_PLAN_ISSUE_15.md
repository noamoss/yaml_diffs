# Implementation Plan for Issue #15: CI/CD Setup with GitHub Actions

## Summary
Set up comprehensive CI/CD pipeline using GitHub Actions for automated testing, linting, type checking, building, and optional deployment. The pipeline will run on multiple Python versions (3.9-3.12) and provide clear feedback through status badges.

## Environment
- **Project Type**: Python
- **Python Version**: 3.9.6 (virtual env at `/Users/noam/Projects/yaml-diffs/.venv`)
- **Virtual Environment**: ✅ Active
- **Dependencies**: ✅ Installed (pydantic, pyyaml, fastapi, uvicorn, pytest, ruff, mypy, etc.)

## Files to Create

### Workflow Files
1. **`.github/workflows/test.yml`** - Main test workflow
   - Run on: `push`, `pull_request`
   - Python versions: 3.9, 3.10, 3.11, 3.12 (matrix strategy)
   - Steps: checkout → setup Python → install deps → run tests → coverage report

2. **`.github/workflows/lint.yml`** - Code quality checks
   - Run on: `push`, `pull_request`
   - Steps: checkout → setup Python → install lint tools → ruff check → ruff format check → mypy

3. **`.github/workflows/build.yml`** - Package build and distribution test
   - Run on: `push` to `main`, tags
   - Steps: checkout → setup Python → install build tools → build package → test installation

4. **`.github/workflows/deploy.yml`** - Railway deployment (optional)
   - Run on: `push` to `main` (or manual trigger)
   - Steps: checkout → deploy to Railway → verify health check

5. **`.github/dependabot.yml`** - Dependency updates (optional)
   - Configure dependabot for Python dependencies

### Documentation
6. **`docs/ci_cd.md`** - CI/CD documentation
   - Workflow descriptions
   - How to test workflows locally
   - Troubleshooting guide

### Updates
7. **`README.md`** - Add workflow status badges
   - Test status badge
   - Lint status badge
   - Build status badge

8. **`AGENTS.md`** - Update with CI/CD information
   - Add `.github/workflows/` to project structure
   - Add CI/CD workflow section
   - Update testing guidelines with CI validation notes
   - Update common tasks to mention CI checks
   - Add GitHub Actions to references

## Implementation Steps

### 1. Setup (10 min)
**Create directory structure:**
```bash
mkdir -p .github/workflows
```

**Verify environment:**
```bash
source .venv/bin/activate
which python  # Should show .venv/bin/python
```

### 2. Test Workflow (30 min)
**File**: `.github/workflows/test.yml`

**Key features:**
- Matrix strategy for Python 3.9, 3.10, 3.11, 3.12
- Cache pip dependencies for faster runs
- Run pytest with coverage
- Upload coverage reports (optional: codecov)
- Fail fast on errors

**Implementation details:**
- Use `actions/setup-python@v5` with matrix
- Cache pip dependencies using `actions/cache@v3`
- Install with: `pip install -e ".[dev]"`
- Run: `pytest --cov=src/yaml_diffs --cov-report=xml --cov-report=term`
- Upload coverage artifact

**Test locally:**
```bash
# Install act (optional, for local testing)
# brew install act  # macOS
# Then: act -j test
```

### 3. Lint Workflow (20 min)
**File**: `.github/workflows/lint.yml`

**Key features:**
- Run ruff check (linting)
- Run ruff format check (formatting)
- Run mypy (type checking)
- Fail if any check fails

**Implementation details:**
- Single Python version (3.11)
- Install: `pip install ruff mypy`
- Run: `ruff check src/ tests/`
- Run: `ruff format --check src/ tests/`
- Run: `mypy src/`

### 4. Build Workflow (20 min)
**File**: `.github/workflows/build.yml`

**Key features:**
- Build package using `python -m build`
- Test package installation
- Upload build artifacts (optional)

**Implementation details:**
- Run on: push to main, tags
- Install: `pip install build`
- Build: `python -m build`
- Test install: `pip install dist/yaml_diffs-*.whl`
- Upload artifacts: `actions/upload-artifact@v3`

### 5. Deploy Workflow (Optional, 15 min)
**File**: `.github/workflows/deploy.yml`

**Key features:**
- Deploy to Railway on push to main
- Verify deployment with health check
- Manual trigger option

**Implementation details:**
- Use Railway CLI or API
- Set Railway token as secret: `RAILWAY_TOKEN`
- Deploy and verify: `curl https://<app>.railway.app/health`

**Note**: Can be skipped if manual deployment preferred

### 6. Dependabot Configuration (Optional, 10 min)
**File**: `.github/dependabot.yml`

**Key features:**
- Auto-update Python dependencies
- Weekly checks
- Group updates for dev dependencies

### 7. Documentation (30 min)
**File**: `docs/ci_cd.md`

**Content:**
- Overview of CI/CD workflows
- Workflow descriptions
- How to test workflows locally (using `act`)
- Troubleshooting common issues
- Status badge URLs

### 8. README Updates (10 min)
**File**: `README.md`

**Add badges section:**
```markdown
## CI/CD Status

[![Tests](https://github.com/noamoss/yaml_diffs/workflows/Tests/badge.svg)](https://github.com/noamoss/yaml_diffs/actions/workflows/test.yml)
[![Lint](https://github.com/noamoss/yaml_diffs/workflows/Lint/badge.svg)](https://github.com/noamoss/yaml_diffs/actions/workflows/lint.yml)
[![Build](https://github.com/noamoss/yaml_diffs/workflows/Build/badge.svg)](https://github.com/noamoss/yaml_diffs/actions/workflows/build.yml)
```

### 9. AGENTS.md Updates (15 min)
**File**: `AGENTS.md`

**Updates completed:**
- ✅ Added `.github/workflows/` to project structure
- ✅ Added CI/CD Workflows section with workflow descriptions
- ✅ Updated Testing Guidelines with CI validation notes
- ✅ Updated Configuration Files section
- ✅ Updated Secrets Management with GitHub Secrets
- ✅ Updated Common Tasks (Adding Feature, Fixing Bug) with CI validation steps
- ✅ Added GitHub Actions to References
- ✅ Updated Notes for AI Agents with CI/CD reminders

**Key additions:**
- Information about CI running automatically on PRs
- Instructions for testing workflows locally with `act`
- Reminders that all CI checks must pass before merge
- Python version compatibility requirements (3.9-3.12)

## Testing Strategy

### Unit Tests
- Workflows themselves don't need unit tests (they're YAML configs)
- But we should verify workflows run correctly

### Integration Tests
1. **Test PR workflow**: Create a test PR to verify workflows trigger
2. **Verify all workflows pass**: Ensure test, lint, build all succeed
3. **Verify badges update**: Check that status badges reflect workflow status

### Acceptance Tests
- ✅ All workflows run on test PR
- ✅ All workflows pass on test PR
- ✅ Workflows run on actual push/PR events
- ✅ Status badges display correctly in README
- ✅ Coverage reports are generated
- ✅ Build artifacts are created

## Time Estimates

| Task | Estimated Time |
|------|---------------|
| Setup directory structure | 5 min |
| Test workflow | 30 min |
| Lint workflow | 20 min |
| Build workflow | 20 min |
| Deploy workflow (optional) | 15 min |
| Dependabot config (optional) | 10 min |
| Documentation | 30 min |
| README badges | 10 min |
| AGENTS.md updates | 15 min |
| Testing & verification | 30 min |
| **Total** | **2.75-3.25 hours** |

**Complexity**: Medium

## Risks & Mitigations

⚠️ **Risk 1**: Workflows fail due to dependency issues
   - **Mitigation**: Test locally first, use exact version pins in pyproject.toml

⚠️ **Risk 2**: Coverage reporting fails
   - **Mitigation**: Start with basic coverage, add codecov later if needed

⚠️ **Risk 3**: Railway deployment requires secrets setup
   - **Mitigation**: Make deploy workflow optional, document manual deployment

⚠️ **Risk 4**: Multiple Python versions have compatibility issues
   - **Mitigation**: Test on all versions locally first, use matrix strategy

⚠️ **Risk 5**: Workflow badges don't update
   - **Mitigation**: Verify badge URLs match workflow names exactly

## Dependencies

### Required
- Task 5.1: Comprehensive Test Suite (for running tests in CI)
- Task 3.3: REST API Service (for deployment workflows)

### Python Packages
- All dependencies already in `pyproject.toml`
- No new dependencies needed for workflows

### GitHub Secrets (for deployment)
- `RAILWAY_TOKEN` (if automated deployment enabled)

## Environment Reminders

**Python:**
- Always work in virtual environment: `source .venv/bin/activate`
- Verify before each session: `which python` should show `.venv/bin/python`
- All workflow files use GitHub Actions Python setup (no venv needed in CI)

## Project Board

- **Board**: YAML Diffs Implementation
- **Current Status**: Backlog
- **Target Status**: In Progress ✅
- **Next Status**: In Review (when PR created)

## Next Steps After Implementation

1. Create test PR to verify all workflows run
2. Verify all workflows pass
3. Check status badges update correctly
4. Create PR for review
5. Merge PR → Auto-updates board to "In Review"

## Notes

- Use caching for dependencies to speed up workflows
- Consider using `actions/cache@v3` for pip cache
- Matrix strategy allows testing on multiple Python versions efficiently
- Fail-fast approach: stop on first error
- Optional workflows (deploy, dependabot) can be added later if needed

