"""Integration tests for API consistency across interfaces.

Tests that the library API, CLI, and REST API produce consistent results.
"""

from pathlib import Path

import pytest

from yaml_diffs.api import diff_and_format, diff_files, load_and_validate
from yaml_diffs.loader import load_document
from yaml_diffs.models import Document


@pytest.mark.integration
class TestAPIConsistency:
    """Test API consistency across different interfaces."""

    def test_load_and_validate_consistency(self, examples_dir: Path):
        """Test that load_and_validate produces consistent results."""
        minimal_file = examples_dir / "minimal_document.yaml"

        if not minimal_file.exists():
            pytest.skip("Example file not found")

        # Load using convenience function
        doc1 = load_and_validate(minimal_file)

        # Load using direct functions
        from yaml_diffs.validator import validate_document

        doc2 = validate_document(minimal_file)

        # Should produce same results
        assert doc1.id == doc2.id
        assert doc1.title == doc2.title
        assert doc1.type == doc2.type

    def test_diff_files_consistency(self, examples_dir: Path):
        """Test that diff_files produces consistent results."""
        v1_file = examples_dir / "document_v1.yaml"
        v2_file = examples_dir / "document_v2.yaml"

        if not (v1_file.exists() and v2_file.exists()):
            pytest.skip("Example files not found")

        # Diff using convenience function
        diff1 = diff_files(v1_file, v2_file)

        # Diff using direct functions
        from yaml_diffs.api import diff_documents

        doc1 = load_document(v1_file)
        doc2 = load_document(v2_file)
        diff2 = diff_documents(doc1, doc2)

        # Should produce same results
        assert len(diff1.changes) == len(diff2.changes)
        assert diff1.added_count == diff2.added_count
        assert diff1.deleted_count == diff2.deleted_count

    def test_diff_and_format_consistency(self, examples_dir: Path):
        """Test that diff_and_format produces consistent results."""
        v1_file = examples_dir / "document_v1.yaml"
        v2_file = examples_dir / "document_v2.yaml"

        if not (v1_file.exists() and v2_file.exists()):
            pytest.skip("Example files not found")

        # Format using convenience function
        json_output = diff_and_format(v1_file, v2_file, output_format="json")

        # Format using direct functions
        from yaml_diffs.api import diff_documents, format_diff

        doc1 = load_document(v1_file)
        doc2 = load_document(v2_file)
        diff = diff_documents(doc1, doc2)
        json_output2 = format_diff(diff, output_format="json")

        # Should produce same results
        assert json_output == json_output2


@pytest.mark.integration
class TestCompleteWorkflows:
    """Test complete document processing workflows."""

    def test_workflow_load_validate_diff_format(self, examples_dir: Path):
        """Test complete workflow: load → validate → diff → format."""
        v1_file = examples_dir / "document_v1.yaml"
        v2_file = examples_dir / "document_v2.yaml"

        if not (v1_file.exists() and v2_file.exists()):
            pytest.skip("Example files not found")

        # Step 1: Load
        doc1 = load_document(v1_file)
        doc2 = load_document(v2_file)

        assert isinstance(doc1, Document)
        assert isinstance(doc2, Document)

        # Step 2: Validate (already done by load_document, but explicit)
        from yaml_diffs.validator import validate_document

        validated_doc1 = validate_document(v1_file)
        validated_doc2 = validate_document(v2_file)

        assert validated_doc1.id == doc1.id
        assert validated_doc2.id == doc2.id

        # Step 3: Diff
        from yaml_diffs.api import diff_documents

        diff = diff_documents(doc1, doc2)

        assert diff is not None
        assert isinstance(diff.changes, list)
        assert len(diff.changes) >= 0

        # Step 4: Format
        from yaml_diffs.api import format_diff

        json_output = format_diff(diff, output_format="json")
        text_output = format_diff(diff, output_format="text")
        yaml_output = format_diff(diff, output_format="yaml")

        assert isinstance(json_output, str)
        assert isinstance(text_output, str)
        assert isinstance(yaml_output, str)

    def test_workflow_all_formats(self, examples_dir: Path):
        """Test workflow with all output formats."""
        v1_file = examples_dir / "document_v1.yaml"
        v2_file = examples_dir / "document_v2.yaml"

        if not (v1_file.exists() and v2_file.exists()):
            pytest.skip("Example files not found")

        # Test all formats
        formats = ["json", "text", "yaml"]

        for fmt in formats:
            output = diff_and_format(v1_file, v2_file, output_format=fmt)
            assert isinstance(output, str)
            assert len(output) > 0


@pytest.mark.integration
class TestErrorHandlingAcrossLayers:
    """Test error handling consistency across API layers."""

    def test_invalid_file_error_handling(self, tmp_path: Path):
        """Test that invalid files produce consistent errors."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text(
            """document:
  id: "test"
  # Missing required fields
""",
            encoding="utf-8",
        )

        # All should raise validation errors
        from yaml_diffs.exceptions import (
            OpenSpecValidationError,
            PydanticValidationError,
            YAMLLoadError,
        )

        with pytest.raises((OpenSpecValidationError, PydanticValidationError, YAMLLoadError)):
            load_and_validate(invalid_file)

        with pytest.raises((OpenSpecValidationError, PydanticValidationError, YAMLLoadError)):
            load_document(invalid_file)

    def test_nonexistent_file_error_handling(self):
        """Test that nonexistent files produce consistent errors."""
        from yaml_diffs.exceptions import YAMLLoadError

        # All should raise YAMLLoadError
        with pytest.raises(YAMLLoadError):
            load_and_validate("nonexistent_file_12345.yaml")

        with pytest.raises(YAMLLoadError):
            load_document("nonexistent_file_12345.yaml")
