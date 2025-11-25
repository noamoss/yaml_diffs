"""Tests for path validation security utilities."""

from pathlib import Path

import pytest

from yaml_diffs.exceptions import PathValidationError
from yaml_diffs.loader import load_yaml_file
from yaml_diffs.security import is_path_safe, validate_path_safe


class TestValidatePathSafe:
    """Tests for validate_path_safe function."""

    def test_valid_relative_path(self) -> None:
        """Test that normal relative paths are accepted."""
        result = validate_path_safe("documents/file.yaml")
        assert isinstance(result, Path)
        assert str(result) == "documents/file.yaml"

    def test_valid_path_with_path_object(self) -> None:
        """Test that Path objects are accepted."""
        path = Path("documents/file.yaml")
        result = validate_path_safe(path)
        assert isinstance(result, Path)

    def test_directory_traversal_single_level(self) -> None:
        """Test that single-level directory traversal is rejected."""
        with pytest.raises(PathValidationError) as exc_info:
            validate_path_safe("../etc/passwd")

        assert exc_info.value.reason == "directory_traversal"
        assert "directory traversal" in str(exc_info.value).lower()

    def test_directory_traversal_multiple_levels(self) -> None:
        """Test that multi-level directory traversal is rejected."""
        with pytest.raises(PathValidationError) as exc_info:
            validate_path_safe("../../etc/passwd")

        assert exc_info.value.reason == "directory_traversal"

    def test_directory_traversal_with_dot(self) -> None:
        """Test that ./../ directory traversal is rejected."""
        with pytest.raises(PathValidationError) as exc_info:
            validate_path_safe("./../etc/passwd")

        assert exc_info.value.reason == "directory_traversal"

    def test_directory_traversal_in_middle(self) -> None:
        """Test that .. in the middle of a path is rejected."""
        with pytest.raises(PathValidationError) as exc_info:
            validate_path_safe("documents/../etc/passwd")

        assert exc_info.value.reason == "directory_traversal"

    def test_valid_path_with_dots_in_filename(self) -> None:
        """Test that dots in filenames (not directory traversal) are allowed."""
        # This should work - "file..yaml" is a valid filename
        result = validate_path_safe("file..yaml")
        assert isinstance(result, Path)

    def test_base_dir_restriction_valid(self, tmp_path: Path) -> None:
        """Test that paths within base_dir are accepted."""
        base_dir = tmp_path / "documents"
        base_dir.mkdir()
        file_path = base_dir / "file.yaml"
        file_path.write_text("test: data")

        result = validate_path_safe("file.yaml", base_dir=base_dir)
        assert result == file_path.resolve()

    def test_base_dir_restriction_outside(self, tmp_path: Path) -> None:
        """Test that paths outside base_dir are rejected."""
        base_dir = tmp_path / "documents"
        base_dir.mkdir()

        with pytest.raises(PathValidationError) as exc_info:
            validate_path_safe("../outside.yaml", base_dir=base_dir)

        assert exc_info.value.reason in ("directory_traversal", "outside_base_dir")

    def test_base_dir_absolute_path_outside(self, tmp_path: Path) -> None:
        """Test that absolute paths outside base_dir are rejected."""
        base_dir = tmp_path / "documents"
        base_dir.mkdir()
        outside_path = tmp_path / "outside.yaml"

        with pytest.raises(PathValidationError) as exc_info:
            validate_path_safe(str(outside_path), base_dir=base_dir)

        assert exc_info.value.reason == "outside_base_dir"

    def test_base_dir_absolute_path_inside(self, tmp_path: Path) -> None:
        """Test that absolute paths inside base_dir are accepted."""
        base_dir = tmp_path / "documents"
        base_dir.mkdir()
        inside_path = base_dir / "file.yaml"
        inside_path.write_text("test: data")

        result = validate_path_safe(str(inside_path), base_dir=base_dir)
        assert result == inside_path.resolve()

    def test_base_dir_nested_path(self, tmp_path: Path) -> None:
        """Test that nested paths within base_dir are accepted."""
        base_dir = tmp_path / "documents"
        base_dir.mkdir()
        nested_dir = base_dir / "nested"
        nested_dir.mkdir()

        result = validate_path_safe("nested/file.yaml", base_dir=base_dir)
        assert result == (base_dir / "nested" / "file.yaml").resolve()

    def test_empty_path(self) -> None:
        """Test that empty paths are handled."""
        # Empty path should be valid (though not very useful)
        result = validate_path_safe("")
        assert isinstance(result, Path)

    def test_path_with_unicode(self) -> None:
        """Test that paths with Unicode characters (e.g., Hebrew) are handled."""
        result = validate_path_safe("מסמכים/קובץ.yaml")
        assert isinstance(result, Path)

    def test_path_with_special_characters(self) -> None:
        """Test that paths with special characters are handled."""
        result = validate_path_safe("file-name_with.special-chars.yaml")
        assert isinstance(result, Path)


class TestIsPathSafe:
    """Tests for is_path_safe function (non-raising version)."""

    def test_valid_path_returns_true(self) -> None:
        """Test that valid paths return True."""
        assert is_path_safe("documents/file.yaml") is True

    def test_directory_traversal_returns_false(self) -> None:
        """Test that directory traversal paths return False."""
        assert is_path_safe("../etc/passwd") is False
        assert is_path_safe("../../etc/passwd") is False
        assert is_path_safe("./../etc/passwd") is False

    def test_base_dir_restriction(self, tmp_path: Path) -> None:
        """Test base_dir restriction with is_path_safe."""
        base_dir = tmp_path / "documents"
        base_dir.mkdir()

        assert is_path_safe("file.yaml", base_dir=base_dir) is True
        assert is_path_safe("../outside.yaml", base_dir=base_dir) is False

    def test_absolute_path_outside_base_dir(self, tmp_path: Path) -> None:
        """Test that absolute paths outside base_dir return False."""
        base_dir = tmp_path / "documents"
        base_dir.mkdir()
        outside_path = tmp_path / "outside.yaml"

        assert is_path_safe(str(outside_path), base_dir=base_dir) is False


class TestPathTraversalAttacks:
    """Tests for various directory traversal attack patterns."""

    def test_standard_traversal(self) -> None:
        """Test standard ../ traversal."""
        with pytest.raises(PathValidationError):
            validate_path_safe("../etc/passwd")

    def test_double_traversal(self) -> None:
        """Test double ../ traversal."""
        with pytest.raises(PathValidationError):
            validate_path_safe("../../etc/passwd")

    def test_triple_traversal(self) -> None:
        """Test triple ../ traversal."""
        with pytest.raises(PathValidationError):
            validate_path_safe("../../../etc/passwd")

    def test_traversal_with_dot(self) -> None:
        """Test ./../ traversal."""
        with pytest.raises(PathValidationError):
            validate_path_safe("./../etc/passwd")

    def test_traversal_in_middle(self) -> None:
        """Test ../ in the middle of a path."""
        with pytest.raises(PathValidationError):
            validate_path_safe("documents/../etc/passwd")

    def test_traversal_at_end(self) -> None:
        """Test ../ at the end of a path."""
        with pytest.raises(PathValidationError):
            validate_path_safe("documents/../")

    def test_multiple_traversals(self) -> None:
        """Test multiple ../ sequences."""
        with pytest.raises(PathValidationError):
            validate_path_safe("documents/../../etc/passwd")


class TestSymlinkAttacks:
    """Tests for symlink-based attacks."""

    def test_symlink_outside_base_dir(self, tmp_path: Path) -> None:
        """Test that symlinks outside base_dir are detected."""
        base_dir = tmp_path / "documents"
        base_dir.mkdir()

        # Create a file outside base_dir
        outside_file = tmp_path / "outside.yaml"
        outside_file.write_text("secret: data")

        # Create a symlink inside base_dir pointing outside
        symlink = base_dir / "link.yaml"
        symlink.symlink_to(outside_file)

        # The symlink should be detected and rejected
        with pytest.raises(PathValidationError) as exc_info:
            validate_path_safe("link.yaml", base_dir=base_dir)

        assert exc_info.value.reason == "outside_base_dir"

    def test_symlink_inside_base_dir(self, tmp_path: Path) -> None:
        """Test that symlinks within base_dir are allowed."""
        base_dir = tmp_path / "documents"
        base_dir.mkdir()

        # Create a file inside base_dir
        inside_file = base_dir / "target.yaml"
        inside_file.write_text("data: test")

        # Create a symlink pointing to it
        symlink = base_dir / "link.yaml"
        symlink.symlink_to(inside_file)

        # This should be allowed
        result = validate_path_safe("link.yaml", base_dir=base_dir)
        assert result.exists()


class TestUnicodePathAttacks:
    """Tests for Unicode-based path attacks."""

    def test_hebrew_path(self) -> None:
        """Test that Hebrew paths are handled correctly."""
        result = validate_path_safe("מסמכים/קובץ.yaml")
        assert isinstance(result, Path)

    def test_unicode_traversal_attempt(self) -> None:
        """Test that Unicode characters don't bypass traversal checks."""
        # Even with Unicode, .. should still be detected
        with pytest.raises(PathValidationError):
            validate_path_safe("מסמכים/../etc/passwd")


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_path(self) -> None:
        """Test empty path."""
        result = validate_path_safe("")
        assert isinstance(result, Path)

    def test_single_dot(self) -> None:
        """Test single dot path."""
        result = validate_path_safe(".")
        assert isinstance(result, Path)

    def test_double_dot_alone(self) -> None:
        """Test that .. alone is rejected."""
        with pytest.raises(PathValidationError):
            validate_path_safe("..")

    def test_path_with_only_dots(self) -> None:
        """Test path with only dots."""
        # "..." is a valid filename, not traversal
        result = validate_path_safe("...")
        assert isinstance(result, Path)

    def test_path_starting_with_dot(self) -> None:
        """Test path starting with dot."""
        result = validate_path_safe("./file.yaml")
        assert isinstance(result, Path)

    def test_path_with_multiple_dots_in_filename(self) -> None:
        """Test filename with multiple dots."""
        result = validate_path_safe("file..name.yaml")
        assert isinstance(result, Path)


class TestLoadYamlFileWithValidation:
    """Integration tests for load_yaml_file with path validation."""

    def test_load_with_validation_valid_path(self, tmp_path: Path) -> None:
        """Test loading file with validation enabled for valid path."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("document:\n  id: test\n", encoding="utf-8")

        data = load_yaml_file(str(yaml_file), validate_path=True)
        assert isinstance(data, dict)
        assert "document" in data

    def test_load_with_validation_traversal_attack(self, tmp_path: Path) -> None:
        """Test that traversal attacks are blocked when validation is enabled."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("document:\n  id: test\n", encoding="utf-8")

        # Try to access file using traversal
        # Should raise PathValidationError directly (not converted to YAMLLoadError)
        with pytest.raises(PathValidationError) as exc_info:
            load_yaml_file("../test.yaml", validate_path=True)

        assert exc_info.value.reason == "directory_traversal"

    def test_load_with_validation_base_dir(self, tmp_path: Path) -> None:
        """Test loading file with base_dir restriction."""
        base_dir = tmp_path / "documents"
        base_dir.mkdir()
        yaml_file = base_dir / "test.yaml"
        yaml_file.write_text("document:\n  id: test\n", encoding="utf-8")

        data = load_yaml_file("test.yaml", validate_path=True, base_dir=base_dir)
        assert isinstance(data, dict)
        assert "document" in data

    def test_load_with_validation_outside_base_dir(self, tmp_path: Path) -> None:
        """Test that files outside base_dir are blocked."""
        base_dir = tmp_path / "documents"
        base_dir.mkdir()
        outside_file = tmp_path / "outside.yaml"
        outside_file.write_text("document:\n  id: test\n", encoding="utf-8")

        # Should raise PathValidationError directly (not converted to YAMLLoadError)
        with pytest.raises(PathValidationError) as exc_info:
            load_yaml_file(str(outside_file), validate_path=True, base_dir=base_dir)

        assert exc_info.value.reason == "outside_base_dir"

    def test_load_without_validation_backward_compatibility(self, tmp_path: Path) -> None:
        """Test that validation is optional (backward compatibility)."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("document:\n  id: test\n", encoding="utf-8")

        # Should work without validation (default behavior)
        data = load_yaml_file(str(yaml_file))
        assert isinstance(data, dict)

        # Should also work with explicit validate_path=False
        data = load_yaml_file(str(yaml_file), validate_path=False)
        assert isinstance(data, dict)
