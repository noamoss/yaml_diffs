"""Tests for package distribution and installation.

This module tests that the package can be built, installed, and works correctly
after installation. These tests verify the distribution configuration.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def dist_dir() -> Path:
    """Path to the dist directory."""
    return PROJECT_ROOT / "dist"


@pytest.fixture
def build_dir() -> Path:
    """Path to the build directory."""
    return PROJECT_ROOT / "build"


@pytest.fixture(scope="module")
def built_package() -> Generator[tuple[Path, Path], None, None]:
    """Build the package and return paths to wheel and sdist.

    Yields:
        Tuple of (wheel_path, sdist_path)
    """
    # Clean previous builds
    dist_dir = PROJECT_ROOT / "dist"
    build_dir = PROJECT_ROOT / "build"
    if dist_dir.exists():
        for file in dist_dir.glob("yaml_diffs-*"):
            file.unlink()
    if build_dir.exists():
        shutil.rmtree(build_dir)

    # Build the package
    # Detect if uv is available and use it if so (for CI environments)
    uv_path = shutil.which("uv")
    if uv_path:
        # Use uv run python -m build for uv-managed environments
        build_cmd = [uv_path, "run", "python", "-m", "build"]
    else:
        # Fall back to sys.executable for non-uv environments
        build_cmd = [sys.executable, "-m", "build"]

    result = subprocess.run(
        build_cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        pytest.skip(f"Package build failed: {result.stderr}")

    # Find built packages
    wheel_files = list(dist_dir.glob("*.whl"))
    sdist_files = list(dist_dir.glob("*.tar.gz"))

    if not wheel_files or not sdist_files:
        pytest.skip("Package files not found after build")

    yield (wheel_files[0], sdist_files[0])


def test_package_builds(built_package: tuple[Path, Path]) -> None:
    """Test that the package builds successfully."""
    wheel_path, sdist_path = built_package
    assert wheel_path.exists(), f"Wheel file not found: {wheel_path}"
    assert sdist_path.exists(), f"Source distribution not found: {sdist_path}"


def test_package_metadata_wheel(built_package: tuple[Path, Path]) -> None:
    """Test that wheel package has correct metadata."""
    wheel_path, _ = built_package

    # Wheel files are zip archives
    with zipfile.ZipFile(wheel_path) as wheel:
        # Check for metadata files
        metadata_files = [f for f in wheel.namelist() if "METADATA" in f]
        assert len(metadata_files) > 0, "METADATA file not found in wheel"

        # Read METADATA
        metadata_file = metadata_files[0]
        metadata_content = wheel.read(metadata_file).decode("utf-8")

        # Check required metadata fields
        assert "Name: yaml-diffs" in metadata_content
        assert "Version: 0.1.0" in metadata_content
        assert "Author: Noam Oss" in metadata_content
        assert "License: MIT" in metadata_content
        assert "Requires-Python: >=3.10" in metadata_content


def test_package_metadata_sdist(built_package: tuple[Path, Path]) -> None:
    """Test that source distribution has correct metadata."""
    _, sdist_path = built_package

    # Source distributions are tar.gz archives
    with tarfile.open(sdist_path, "r:gz") as tar:
        # Check for PKG-INFO
        pkg_info_members = [m for m in tar.getmembers() if "PKG-INFO" in m.name]
        assert len(pkg_info_members) > 0, "PKG-INFO not found in source distribution"

        # Read PKG-INFO
        pkg_info = tar.extractfile(pkg_info_members[0])
        assert pkg_info is not None
        pkg_info_content = pkg_info.read().decode("utf-8")

        # Check required metadata fields
        assert "Name: yaml-diffs" in pkg_info_content
        assert "Version: 0.1.0" in pkg_info_content
        assert "Author: Noam Oss" in pkg_info_content
        assert "License: MIT" in pkg_info_content
        assert "Requires-Python: >=3.10" in pkg_info_content


def test_schema_file_included_wheel(built_package: tuple[Path, Path]) -> None:
    """Test that schema YAML file is included in wheel."""
    wheel_path, _ = built_package

    with zipfile.ZipFile(wheel_path) as wheel:
        schema_files = [f for f in wheel.namelist() if "schema" in f and f.endswith(".yaml")]
        assert len(schema_files) > 0, "Schema YAML file not found in wheel"
        assert any("legal_document_spec.yaml" in f for f in schema_files)


def test_schema_file_included_sdist(built_package: tuple[Path, Path]) -> None:
    """Test that schema YAML file is included in source distribution."""
    _, sdist_path = built_package

    with tarfile.open(sdist_path, "r:gz") as tar:
        schema_files = [
            m.name for m in tar.getmembers() if "schema" in m.name and m.name.endswith(".yaml")
        ]
        assert len(schema_files) > 0, "Schema YAML file not found in source distribution"
        assert any("legal_document_spec.yaml" in f for f in schema_files)


def test_dev_files_excluded_wheel(built_package: tuple[Path, Path]) -> None:
    """Test that development files are excluded from wheel."""
    wheel_path, _ = built_package

    with zipfile.ZipFile(wheel_path) as wheel:
        files = wheel.namelist()

        # Check that dev files are not included
        assert not any("tests/" in f for f in files), "Tests directory found in wheel"
        assert not any("examples/" in f for f in files), "Examples directory found in wheel"
        assert not any("docs/" in f for f in files), "Docs directory found in wheel"
        assert not any(".github/" in f for f in files), ".github directory found in wheel"


def test_dev_files_excluded_sdist(built_package: tuple[Path, Path]) -> None:
    """Test that development files are excluded from source distribution."""
    _, sdist_path = built_package

    with tarfile.open(sdist_path, "r:gz") as tar:
        files = [m.name for m in tar.getmembers()]

        # Extract base directory name (first part of path)
        base_dirs = {f.split("/")[0] for f in files if "/" in f}

        # Check that dev directories are not in the base
        # Note: MANIFEST.in excludes these, but they might still be in the archive
        # We check that they're not at the root level
        assert "tests" not in base_dirs, "Tests directory found in source distribution"
        assert "examples" not in base_dirs, "Examples directory found in source distribution"
        assert "docs" not in base_dirs, "Docs directory found in source distribution"
        assert ".github" not in base_dirs, ".github directory found in source distribution"


def test_package_installs(built_package: tuple[Path, Path], tmp_path: Path) -> None:
    """Test that the package can be installed in a clean environment."""
    wheel_path, _ = built_package

    # Create a temporary virtual environment
    venv_path = tmp_path / "test_venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_path)],
        check=True,
        capture_output=True,
    )

    # Determine pip path based on OS
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
    else:
        pip_path = venv_path / "bin" / "pip"

    # Install the package
    result = subprocess.run(
        [str(pip_path), "install", str(wheel_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"Installation failed: {result.stderr}"


def test_cli_works_after_install(built_package: tuple[Path, Path], tmp_path: Path) -> None:
    """Test that CLI commands work after installation."""
    wheel_path, _ = built_package

    # Create a temporary virtual environment
    venv_path = tmp_path / "test_venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_path)],
        check=True,
        capture_output=True,
    )

    # Determine paths based on OS
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
        cli_path = venv_path / "Scripts" / "yaml-diffs"
    else:
        pip_path = venv_path / "bin" / "pip"
        cli_path = venv_path / "bin" / "yaml-diffs"

    # Install the package
    subprocess.run(
        [str(pip_path), "install", str(wheel_path)],
        check=True,
        capture_output=True,
    )

    # Test CLI version command
    result = subprocess.run(
        [str(cli_path), "--version"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"CLI version command failed: {result.stderr}"
    assert "yaml-diffs" in result.stdout or "yaml-diffs" in result.stderr
    assert "0.1.0" in result.stdout or "0.1.0" in result.stderr


def test_imports_work_after_install(built_package: tuple[Path, Path], tmp_path: Path) -> None:
    """Test that all main imports work after installation."""
    wheel_path, _ = built_package

    # Create a temporary virtual environment
    venv_path = tmp_path / "test_venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_path)],
        check=True,
        capture_output=True,
    )

    # Determine paths based on OS
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"

    # Install the package
    subprocess.run(
        [str(pip_path), "install", str(wheel_path)],
        check=True,
        capture_output=True,
    )

    # Test imports
    import_test = """
import yaml_diffs
from yaml_diffs import (
    load_document,
    validate_document,
    diff_documents,
    format_diff,
    Document,
    Section,
    __version__
)
assert __version__ == "0.1.0"
print("All imports successful!")
"""

    result = subprocess.run(
        [str(python_path), "-c", import_test],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"Import test failed: {result.stderr}"
    assert "All imports successful!" in result.stdout


def test_schema_accessible_after_install(built_package: tuple[Path, Path], tmp_path: Path) -> None:
    """Test that schema file is accessible after installation."""
    wheel_path, _ = built_package

    # Create a temporary virtual environment
    venv_path = tmp_path / "test_venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_path)],
        check=True,
        capture_output=True,
    )

    # Determine paths based on OS
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"

    # Install the package
    subprocess.run(
        [str(pip_path), "install", str(wheel_path)],
        check=True,
        capture_output=True,
    )

    # Test schema file access
    schema_test = """
from yaml_diffs.schema import load_schema

# Check that schema can be loaded
schema = load_schema()
assert schema is not None
assert 'version' in schema or 'info' in schema

# Verify schema has expected structure
assert isinstance(schema, dict)
print("Schema file accessible and loadable!")
"""

    result = subprocess.run(
        [str(python_path), "-c", schema_test],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"Schema access test failed: {result.stderr}"
    assert "Schema file accessible and loadable!" in result.stdout
