"""Tests to verify project structure exists."""

from pathlib import Path


def test_project_directories_exist():
    """Verify all required project directories exist."""
    base_dir = Path(__file__).parent.parent

    required_dirs = [
        base_dir / "src" / "yaml_diffs",
        base_dir / "tests",
        base_dir / "docs",
        base_dir / "examples",
    ]

    for directory in required_dirs:
        assert directory.exists(), f"Directory {directory} does not exist"
        assert directory.is_dir(), f"{directory} is not a directory"


def test_package_files_exist():
    """Verify package initialization files exist."""
    base_dir = Path(__file__).parent.parent

    required_files = [
        base_dir / "src" / "yaml_diffs" / "__init__.py",
        base_dir / "src" / "yaml_diffs" / "__version__.py",
        base_dir / "tests" / "__init__.py",
    ]

    for file_path in required_files:
        assert file_path.exists(), f"File {file_path} does not exist"
        assert file_path.is_file(), f"{file_path} is not a file"


def test_configuration_files_exist():
    """Verify configuration files exist."""
    base_dir = Path(__file__).parent.parent

    required_files = [
        base_dir / "pyproject.toml",
        base_dir / ".gitignore",
        base_dir / "README.md",
        base_dir / ".pre-commit-config.yaml",
    ]

    for file_path in required_files:
        assert file_path.exists(), f"File {file_path} does not exist"
        assert file_path.is_file(), f"{file_path} is not a file"

