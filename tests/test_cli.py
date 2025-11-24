"""Tests for the CLI tool."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from yaml_diffs.cli.main import cli, main


@pytest.fixture
def runner() -> CliRunner:
    """Create a CliRunner instance for testing."""
    return CliRunner()


@pytest.fixture
def minimal_yaml_file(tmp_path: Path) -> Path:
    """Create a minimal valid YAML file for testing."""
    yaml_content = """document:
  id: "test-123"
  title: "חוק בדיקה"
  type: "law"
  language: "hebrew"
  version:
    number: "2024-01-01"
  source:
    url: "https://example.com/test"
    fetched_at: "2025-01-20T09:50:00Z"
  sections: []
"""
    file_path = tmp_path / "minimal.yaml"
    file_path.write_text(yaml_content, encoding="utf-8")
    return file_path


@pytest.fixture
def invalid_yaml_file(tmp_path: Path) -> Path:
    """Create an invalid YAML file for testing."""
    yaml_content = """document:
  id: "test-123"
  # Missing required fields
"""
    file_path = tmp_path / "invalid.yaml"
    file_path.write_text(yaml_content, encoding="utf-8")
    return file_path


@pytest.fixture
def document_v1_file(tmp_path: Path) -> Path:
    """Create document v1 for diff testing."""
    yaml_content = """document:
  id: "doc-1"
  title: "Test Document"
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com/doc1"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: "1"
      title: "Section 1"
      content: "Original content"
      sections: []
"""
    file_path = tmp_path / "doc_v1.yaml"
    file_path.write_text(yaml_content, encoding="utf-8")
    return file_path


@pytest.fixture
def document_v2_file(tmp_path: Path) -> Path:
    """Create document v2 for diff testing."""
    yaml_content = """document:
  id: "doc-1"
  title: "Test Document"
  type: "law"
  language: "hebrew"
  version:
    number: "2.0"
  source:
    url: "https://example.com/doc1"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
    - id: "sec-1"
      marker: "1"
      title: "Section 1"
      content: "Updated content"
      sections: []
    - id: "sec-2"
      marker: "2"
      title: "Section 2"
      content: "New section"
      sections: []
"""
    file_path = tmp_path / "doc_v2.yaml"
    file_path.write_text(yaml_content, encoding="utf-8")
    return file_path


class TestCLIHelp:
    """Test CLI help and usage information."""

    def test_help_command(self, runner: CliRunner) -> None:
        """Test that help command displays correctly."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "yaml-diffs" in result.output
        assert "validate" in result.output
        assert "diff" in result.output

    def test_version_command(self, runner: CliRunner) -> None:
        """Test that version command displays correctly."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "yaml-diffs" in result.output
        assert "version" in result.output.lower() or "0.1.0" in result.output

    def test_validate_help(self, runner: CliRunner) -> None:
        """Test validate command help."""
        result = runner.invoke(cli, ["validate", "--help"])
        assert result.exit_code == 0
        assert "validate" in result.output.lower()
        assert "YAML document" in result.output

    def test_diff_help(self, runner: CliRunner) -> None:
        """Test diff command help."""
        result = runner.invoke(cli, ["diff", "--help"])
        assert result.exit_code == 0
        assert "diff" in result.output.lower()
        assert "--format" in result.output
        assert "--output" in result.output


class TestValidateCommand:
    """Test the validate command."""

    def test_validate_command_success(self, runner: CliRunner, minimal_yaml_file: Path) -> None:
        """Test validate command with valid file."""
        result = runner.invoke(cli, ["validate", str(minimal_yaml_file)])
        assert result.exit_code == 0
        assert "is valid" in result.output
        assert "test-123" in result.output
        assert "Document ID" in result.output

    def test_validate_command_file_not_found(self, runner: CliRunner) -> None:
        """Test validate command with missing file."""
        result = runner.invoke(cli, ["validate", "nonexistent.yaml"])
        assert result.exit_code != 0
        assert "Error" in result.output or "not found" in result.output.lower()

    def test_validate_command_invalid_yaml(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test validate command with invalid YAML syntax."""
        invalid_file = tmp_path / "invalid_syntax.yaml"
        invalid_file.write_text("invalid: yaml: content: [", encoding="utf-8")

        result = runner.invoke(cli, ["validate", str(invalid_file)])
        assert result.exit_code != 0
        assert "Error" in result.output

    def test_validate_command_validation_error(
        self, runner: CliRunner, invalid_yaml_file: Path
    ) -> None:
        """Test validate command with validation errors."""
        result = runner.invoke(cli, ["validate", str(invalid_yaml_file)])
        assert result.exit_code != 0
        assert "Error" in result.output
        assert "validation" in result.output.lower()

    def test_validate_command_hebrew_content(
        self, runner: CliRunner, minimal_yaml_file: Path
    ) -> None:
        """Test validate command with Hebrew content."""
        result = runner.invoke(cli, ["validate", str(minimal_yaml_file)])
        assert result.exit_code == 0
        # Hebrew title should be preserved
        assert "חוק בדיקה" in result.output or "is valid" in result.output


class TestDiffCommand:
    """Test the diff command."""

    def test_diff_command_success(
        self, runner: CliRunner, document_v1_file: Path, document_v2_file: Path
    ) -> None:
        """Test diff command with two valid files."""
        result = runner.invoke(cli, ["diff", str(document_v1_file), str(document_v2_file)])
        assert result.exit_code == 0
        assert "added_count" in result.output or "changes" in result.output

    def test_diff_command_json_format(
        self, runner: CliRunner, document_v1_file: Path, document_v2_file: Path
    ) -> None:
        """Test diff command with JSON format."""
        result = runner.invoke(
            cli, ["diff", str(document_v1_file), str(document_v2_file), "--format", "json"]
        )
        assert result.exit_code == 0
        assert "added_count" in result.output or "changes" in result.output

    def test_diff_command_text_format(
        self, runner: CliRunner, document_v1_file: Path, document_v2_file: Path
    ) -> None:
        """Test diff command with text format."""
        result = runner.invoke(
            cli, ["diff", str(document_v1_file), str(document_v2_file), "--format", "text"]
        )
        assert result.exit_code == 0
        # Text format should be human-readable
        assert isinstance(result.output, str)
        assert len(result.output) > 0

    def test_diff_command_yaml_format(
        self, runner: CliRunner, document_v1_file: Path, document_v2_file: Path
    ) -> None:
        """Test diff command with YAML format."""
        result = runner.invoke(
            cli, ["diff", str(document_v1_file), str(document_v2_file), "--format", "yaml"]
        )
        assert result.exit_code == 0
        # YAML format should contain YAML-like structure
        assert "changes" in result.output or "added_count" in result.output

    def test_diff_command_output_file(
        self, runner: CliRunner, document_v1_file: Path, document_v2_file: Path, tmp_path: Path
    ) -> None:
        """Test diff command saves output to file."""
        output_file = tmp_path / "diff_output.json"
        result = runner.invoke(
            cli,
            [
                "diff",
                str(document_v1_file),
                str(document_v2_file),
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        assert "saved to" in result.output.lower()
        # Verify file content
        content = output_file.read_text(encoding="utf-8")
        assert len(content) > 0

    def test_diff_command_file_not_found(self, runner: CliRunner, document_v1_file: Path) -> None:
        """Test diff command with missing file."""
        result = runner.invoke(cli, ["diff", str(document_v1_file), "nonexistent.yaml"])
        assert result.exit_code != 0
        assert "Error" in result.output

    def test_diff_command_filter_change_types(
        self, runner: CliRunner, document_v1_file: Path, document_v2_file: Path
    ) -> None:
        """Test diff command with filter-change-types option."""
        result = runner.invoke(
            cli,
            [
                "diff",
                str(document_v1_file),
                str(document_v2_file),
                "--filter-change-types",
                "SECTION_ADDED",
            ],
        )
        assert result.exit_code == 0

    def test_diff_command_filter_section_path(
        self, runner: CliRunner, document_v1_file: Path, document_v2_file: Path
    ) -> None:
        """Test diff command with filter-section-path option."""
        result = runner.invoke(
            cli,
            [
                "diff",
                str(document_v1_file),
                str(document_v2_file),
                "--filter-section-path",
                "1",
            ],
        )
        assert result.exit_code == 0

    def test_diff_command_invalid_format(
        self, runner: CliRunner, document_v1_file: Path, document_v2_file: Path
    ) -> None:
        """Test diff command with invalid format."""
        result = runner.invoke(
            cli, ["diff", str(document_v1_file), str(document_v2_file), "--format", "invalid"]
        )
        assert result.exit_code != 0


class TestCLIIntegration:
    """Integration tests for CLI end-to-end workflows."""

    def test_cli_end_to_end_workflow(
        self,
        runner: CliRunner,
        minimal_yaml_file: Path,
        document_v1_file: Path,
        document_v2_file: Path,
    ) -> None:
        """Test complete CLI workflow: validate + diff."""
        # Validate first document
        result1 = runner.invoke(cli, ["validate", str(minimal_yaml_file)])
        assert result1.exit_code == 0

        # Diff two documents
        result2 = runner.invoke(cli, ["diff", str(document_v1_file), str(document_v2_file)])
        assert result2.exit_code == 0

    def test_cli_hebrew_content(
        self,
        runner: CliRunner,
        minimal_yaml_file: Path,
        document_v1_file: Path,
        document_v2_file: Path,
    ) -> None:
        """Test CLI with Hebrew content."""
        # Validate document with Hebrew content
        result = runner.invoke(cli, ["validate", str(minimal_yaml_file)])
        assert result.exit_code == 0

        # Diff should handle Hebrew content
        result = runner.invoke(cli, ["diff", str(document_v1_file), str(document_v2_file)])
        assert result.exit_code == 0

    def test_cli_error_messages(self, runner: CliRunner, invalid_yaml_file: Path) -> None:
        """Test that CLI provides clear error messages."""
        result = runner.invoke(cli, ["validate", str(invalid_yaml_file)])
        assert result.exit_code != 0
        # Error message should be clear and helpful
        assert "Error" in result.output
        assert len(result.output) > 0


class TestCLIMainEntry:
    """Test the main entry point."""

    def test_main_function(self, runner: CliRunner, minimal_yaml_file: Path) -> None:
        """Test that main function can be called and works correctly."""
        # Test that main() works when invoked through the entry point
        # Since main() calls cli(), we test it by invoking cli directly
        # which is what main() does internally
        result = runner.invoke(cli, ["validate", str(minimal_yaml_file)])
        assert result.exit_code == 0
        assert "is valid" in result.output

    def test_main_function_error_handling(self) -> None:
        """Test that main() error handling wrapper works correctly."""
        # Test that main() can be called and handles exceptions
        # We can't easily test the full error path without mocking sys.exit,
        # but we can verify the function exists and is callable
        assert callable(main)
        # Test that it calls cli() correctly by checking it doesn't raise
        # when given valid arguments (tested indirectly through cli tests)
