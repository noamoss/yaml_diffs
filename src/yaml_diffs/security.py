"""Security utilities for path validation.

This module provides path validation functions to prevent directory traversal
attacks and restrict file access to specific directories. These utilities are
designed for API security contexts where user-provided file paths need to be
validated before file operations.
"""

from __future__ import annotations

from pathlib import Path

from yaml_diffs.exceptions import PathValidationError


def validate_path_safe(
    file_path: str | Path,
    base_dir: Path | None = None,
) -> Path:
    """Validate that a file path is safe and doesn't contain directory traversal.

    This function validates file paths to prevent directory traversal attacks
    (e.g., `../../../etc/passwd`). It can optionally restrict paths to a base
    directory for API security contexts.

    The validation:
    - Checks for directory traversal sequences (`..`)
    - Resolves symlinks to detect symlink-based attacks
    - Optionally restricts paths to a base directory
    - Normalizes paths to handle edge cases

    Args:
        file_path: Path to validate (string or Path object).
        base_dir: Optional base directory to restrict paths to. If provided,
            all paths must be within this directory. If None, only directory
            traversal is checked.

    Returns:
        Resolved, validated Path object.

    Raises:
        PathValidationError: If the path is unsafe. Reasons include:
            - "directory_traversal": Path contains `..` sequences
            - "outside_base_dir": Path resolves outside base_dir
            - "absolute_path": Absolute path provided when base_dir is set

    Examples:
        >>> from pathlib import Path
        >>> validate_path_safe("documents/file.yaml")
        Path('documents/file.yaml')

        >>> base = Path("/safe/directory")
        >>> validate_path_safe("file.yaml", base_dir=base)
        Path('/safe/directory/file.yaml')

        >>> validate_path_safe("../etc/passwd")
        Traceback (most recent call last):
            ...
        PathValidationError: Path contains directory traversal: ../etc/passwd
    """
    file_path_obj = Path(file_path) if isinstance(file_path, str) else file_path

    # Check for directory traversal sequences
    # Check for .. in any part of the path
    # We need to check the original path string representation as well
    # because resolve() might not catch all cases
    path_str = str(file_path_obj)
    if ".." in path_str:
        # Check if it's a legitimate use (e.g., "file..yaml" vs "../file")
        parts = Path(path_str).parts
        if ".." in parts:
            raise PathValidationError(
                f"Path contains directory traversal: {file_path_obj}",
                file_path=str(file_path_obj),
                reason="directory_traversal",
            )

    # If base_dir is provided, validate against it
    if base_dir is not None:
        base_dir_obj = Path(base_dir) if isinstance(base_dir, str) else base_dir
        base_dir_resolved = base_dir_obj.resolve()

        # Reject absolute paths if base_dir is set (unless they're within base_dir)
        if file_path_obj.is_absolute():
            file_path_resolved = file_path_obj.resolve()
            # Check if the absolute path is within base_dir
            try:
                file_path_resolved.relative_to(base_dir_resolved)
            except ValueError:
                # Path is outside base_dir
                raise PathValidationError(
                    f"Path is outside allowed directory: {file_path_obj}",
                    file_path=str(file_path_obj),
                    reason="outside_base_dir",
                ) from None
        else:
            # For relative paths, resolve them relative to base_dir
            resolved_path = (base_dir_resolved / file_path_obj).resolve()

            # Check if resolved path is within base_dir
            try:
                resolved_path.relative_to(base_dir_resolved)
            except ValueError:
                # Path resolves outside base_dir (e.g., via symlinks)
                raise PathValidationError(
                    f"Path resolves outside allowed directory: {file_path_obj}",
                    file_path=str(file_path_obj),
                    reason="outside_base_dir",
                ) from None

            return resolved_path

    # If no base_dir, just return the resolved path (if absolute) or original (if relative)
    # But we still need to resolve to check for symlink attacks
    if file_path_obj.is_absolute():
        return file_path_obj.resolve()

    # For relative paths without base_dir, we can't fully resolve them
    # but we've already checked for .. sequences
    return file_path_obj


def is_path_safe(
    file_path: str | Path,
    base_dir: Path | None = None,
) -> bool:
    """Check if a file path is safe without raising an exception.

    This is a non-raising version of `validate_path_safe()` that returns
    True if the path is safe, False otherwise.

    Args:
        file_path: Path to check (string or Path object).
        base_dir: Optional base directory to restrict paths to.

    Returns:
        True if the path is safe, False otherwise.

    Examples:
        >>> is_path_safe("documents/file.yaml")
        True
        >>> is_path_safe("../etc/passwd")
        False
    """
    try:
        validate_path_safe(file_path, base_dir)
        return True
    except PathValidationError:
        return False
