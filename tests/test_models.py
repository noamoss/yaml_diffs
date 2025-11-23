"""Tests for Pydantic models."""

import uuid

import pytest
import yaml
from pydantic import ValidationError

from yaml_diffs.models import Document, DocumentType, Section, Source, Version


# Test fixtures
@pytest.fixture
def sample_id() -> str:
    """Generate a sample ID for testing (string format)."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_uuid() -> str:
    """Generate a sample UUID string for testing (backward compatibility)."""
    return str(uuid.uuid4())


@pytest.fixture
def hebrew_text() -> str:
    """Sample Hebrew text for testing."""
    return "חוק יסוד: כבוד האדם וחירותו"


@pytest.fixture
def minimal_section(sample_id: str) -> Section:
    """Create a minimal section with only id."""
    return Section(id=sample_id)


@pytest.fixture
def full_section(sample_id: str, hebrew_text: str) -> Section:
    """Create a section with all fields."""
    return Section(
        id=sample_id,
        content=hebrew_text,
        marker="א",
        title="סעיף ראשון",
        sections=[],
    )


@pytest.fixture
def minimal_document(sample_id: str) -> Document:
    """Create a minimal document with required fields only."""
    return Document(
        id="law-1234",
        title="חוק הדוגמה",
        type=DocumentType.LAW,
        version=Version(number="1.0"),
        source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
    )


class TestSectionCreation:
    """Test Section model creation with various field combinations."""

    def test_create_section_with_all_fields(self, sample_id: str, hebrew_text: str):
        """Test creating Section with id, content, marker, title, sections."""
        section = Section(
            id=sample_id,
            content=hebrew_text,
            marker="א",
            title="סעיף ראשון",
            sections=[],
        )

        assert section.id == sample_id
        assert isinstance(section.id, str)
        assert section.content == hebrew_text
        assert section.marker == "א"
        assert section.title == "סעיף ראשון"
        assert section.sections == []
        assert isinstance(section.sections, list)

    def test_create_section_with_minimal_fields(self, sample_id: str):
        """Test creating Section with only id provided."""
        section = Section(id=sample_id)

        assert section.id == sample_id
        assert isinstance(section.id, str)
        assert section.content == ""  # Should default to empty string
        assert section.marker is None
        assert section.title is None
        assert section.sections == []

    def test_nested_sections_deep_nesting(self, sample_id: str):
        """Test nested sections (3+ levels deep)."""
        # Create 4 levels deep
        level4 = Section(id=str(uuid.uuid4()), content="Level 4")
        level3 = Section(id=str(uuid.uuid4()), content="Level 3", sections=[level4])
        level2 = Section(id=str(uuid.uuid4()), content="Level 2", sections=[level3])
        level1 = Section(id=sample_id, content="Level 1", sections=[level2])

        # Verify all levels are accessible
        assert level1.content == "Level 1"
        assert len(level1.sections) == 1
        assert level1.sections[0].content == "Level 2"
        assert len(level1.sections[0].sections) == 1
        assert level1.sections[0].sections[0].content == "Level 3"
        assert len(level1.sections[0].sections[0].sections) == 1
        assert level1.sections[0].sections[0].sections[0].content == "Level 4"
        assert len(level1.sections[0].sections[0].sections[0].sections) == 0

    def test_auto_generate_id_when_id_not_provided(self):
        """Test auto-generate ID (UUID string) when id not provided."""
        section1 = Section()
        section2 = Section()

        # Verify IDs are generated as strings
        assert isinstance(section1.id, str)
        assert isinstance(section2.id, str)

        # Verify IDs are different
        assert section1.id != section2.id

        # Verify IDs match the pattern (alphanumeric, hyphens, underscores)
        import re

        pattern = r"^[a-zA-Z0-9_-]+$"
        assert re.match(pattern, section1.id)
        assert re.match(pattern, section2.id)

    def test_reject_invalid_data_types(self):
        """Test reject invalid data types."""
        # Test invalid id type
        with pytest.raises(ValidationError) as exc_info:
            Section(id=123)  # Should be string
        assert "id" in str(exc_info.value).lower()

        # Test invalid content type
        with pytest.raises(ValidationError) as exc_info:
            Section(id="sec-1", content=123)  # Should be string
        assert "content" in str(exc_info.value).lower()

        # Test invalid marker type
        with pytest.raises(ValidationError) as exc_info:
            Section(id="sec-1", marker=123)  # Should be string or None
        assert "marker" in str(exc_info.value).lower()

        # Test invalid sections type
        with pytest.raises(ValidationError) as exc_info:
            Section(id="sec-1", sections="not a list")  # Should be list
        assert "sections" in str(exc_info.value).lower()

    def test_reject_invalid_id_pattern(self):
        """Test reject invalid ID patterns."""
        # Test invalid ID pattern (contains invalid characters)
        with pytest.raises(ValidationError) as exc_info:
            Section(id="sec 1")  # Space is not allowed
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error_msg = str(exc_info.value).lower()
        assert "id" in error_msg or "pattern" in error_msg

        # Test empty ID
        with pytest.raises(ValidationError) as exc_info:
            Section(id="")  # Empty string not allowed
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_handle_hebrew_content_correctly(self, hebrew_text: str):
        """Test handle Hebrew content correctly."""
        section = Section(
            id="sec-1",
            content=hebrew_text,
            title="כותרת בעברית",
            marker="א",
        )

        # Verify Hebrew text is preserved correctly
        assert section.content == hebrew_text
        assert section.title == "כותרת בעברית"
        assert section.marker == "א"

        # Verify UTF-8 encoding
        assert section.content.encode("utf-8").decode("utf-8") == hebrew_text
        assert len(section.content) > 0  # Should have content

        # Test with mixed Hebrew and English
        mixed_content = f"{hebrew_text} - Basic Law"
        section_mixed = Section(id="sec-2", content=mixed_content)
        assert section_mixed.content == mixed_content


class TestDocumentCreation:
    """Test Document model creation."""

    def test_create_document_with_all_fields(self, sample_id: str, hebrew_text: str):
        """Test creating Document with all fields including new metadata."""
        section = Section(id=sample_id, content=hebrew_text)
        doc = Document(
            id="law-1234",
            title="חוק יסוד: כבוד האדם וחירותו",
            type=DocumentType.LAW,
            language="hebrew",
            version=Version(number="1.0", description="Initial version"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            authors=["הכנסת", "משרד המשפטים"],
            published_date="1992-03-17",
            updated_date="2024-01-15T10:30:00Z",
            sections=[section],
        )

        assert doc.id == "law-1234"
        assert doc.title == "חוק יסוד: כבוד האדם וחירותו"
        assert doc.type == DocumentType.LAW
        assert doc.language == "hebrew"
        assert doc.version.number == "1.0"
        assert doc.version.description == "Initial version"
        assert doc.source.url == "https://example.com/law"
        assert doc.source.fetched_at == "2025-01-20T09:50:00Z"
        assert doc.authors == ["הכנסת", "משרד המשפטים"]
        assert doc.published_date == "1992-03-17"
        assert doc.updated_date == "2024-01-15T10:30:00Z"
        assert len(doc.sections) == 1
        assert doc.sections[0].id == sample_id

    def test_create_document_with_minimal_fields(self):
        """Test creating Document with minimal required fields."""
        doc = Document(
            id="law-1234",
            title="חוק הדוגמה",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
        )

        assert doc.id == "law-1234"
        assert doc.title == "חוק הדוגמה"
        assert doc.type == DocumentType.LAW
        assert doc.language == "hebrew"  # Default value
        assert doc.version.number == "1.0"
        assert doc.version.description is None
        assert doc.source.url == "https://example.com/law"
        assert doc.authors is None
        assert doc.published_date is None
        assert doc.updated_date is None
        assert doc.sections == []

    def test_create_document_with_partial_metadata(self):
        """Test creating Document with some metadata fields."""
        doc = Document(
            id="law-1234",
            title="Test Document",
            type=DocumentType.REGULATION,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            published_date="2024-01-15",
        )

        assert doc.title == "Test Document"
        assert doc.type == DocumentType.REGULATION
        assert doc.authors is None
        assert doc.version.number == "1.0"
        assert doc.published_date == "2024-01-15"
        assert doc.updated_date is None

    def test_create_document_with_hebrew_metadata(self, hebrew_text: str):
        """Test creating Document with Hebrew text in metadata."""
        doc = Document(
            id="law-1234",
            title=hebrew_text,
            type=DocumentType.LAW,
            authors=["מחבר ראשון", "מחבר שני"],
            version=Version(number="1.0"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
        )

        assert doc.title == hebrew_text
        assert doc.authors == ["מחבר ראשון", "מחבר שני"]
        assert len(doc.authors) == 2

    def test_create_document_with_date_formats(self):
        """Test creating Document with different date formats."""
        # Date only format
        doc1 = Document(
            id="law-1234",
            title="Test",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            published_date="2024-01-15",
        )
        assert doc1.published_date == "2024-01-15"

        # Date-time format
        doc2 = Document(
            id="law-1234",
            title="Test",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            updated_date="2024-01-15T10:30:00Z",
        )
        assert doc2.updated_date == "2024-01-15T10:30:00Z"

        # Both dates
        doc3 = Document(
            id="law-1234",
            title="Test",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            published_date="2024-01-15",
            updated_date="2024-01-16T14:20:00Z",
        )
        assert doc3.published_date == "2024-01-15"
        assert doc3.updated_date == "2024-01-16T14:20:00Z"

    def test_create_document_with_empty_authors_list(self):
        """Test creating Document with empty authors list."""
        # Empty list should be allowed (though None is preferred)
        doc = Document(
            id="law-1234",
            title="Test",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            authors=[],
        )
        assert doc.authors == []

    def test_document_rejects_missing_required_fields(self):
        """Test Document rejects missing required fields."""
        # Missing id
        with pytest.raises(ValidationError) as exc_info:
            Document(
                title="Test",
                type=DocumentType.LAW,
                version=Version(number="1.0"),
                source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error_msg = str(exc_info.value).lower()
        assert "id" in error_msg

        # Missing title
        with pytest.raises(ValidationError) as exc_info:
            Document(
                id="law-1234",
                type=DocumentType.LAW,
                version=Version(number="1.0"),
                source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error_msg = str(exc_info.value).lower()
        assert "title" in error_msg

        # Missing version
        with pytest.raises(ValidationError) as exc_info:
            Document(
                id="law-1234",
                title="Test",
                type=DocumentType.LAW,
                source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error_msg = str(exc_info.value).lower()
        assert "version" in error_msg

        # Missing source
        with pytest.raises(ValidationError) as exc_info:
            Document(
                id="law-1234",
                title="Test",
                type=DocumentType.LAW,
                version=Version(number="1.0"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error_msg = str(exc_info.value).lower()
        assert "source" in error_msg

    def test_document_rejects_invalid_date_format(self):
        """Test Document rejects invalid date formats."""
        # Test invalid date format
        with pytest.raises(ValidationError) as exc_info:
            Document(
                id="law-1234",
                title="Test",
                type=DocumentType.LAW,
                version=Version(number="1.0"),
                source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
                published_date="not-a-date",
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error_msg = str(exc_info.value).lower()
        assert "published_date" in error_msg or "iso 8601" in error_msg

        # Test invalid updated_date format
        with pytest.raises(ValidationError) as exc_info:
            Document(
                id="law-1234",
                title="Test",
                type=DocumentType.LAW,
                version=Version(number="1.0"),
                source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
                updated_date="2024/01/15",  # Wrong format
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error_msg = str(exc_info.value).lower()
        assert "updated_date" in error_msg or "iso 8601" in error_msg

    def test_document_accepts_valid_date_formats(self):
        """Test Document accepts valid ISO 8601 date formats."""
        # Date only format
        doc1 = Document(
            id="law-1234",
            title="Test",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            published_date="2024-01-15",
        )
        assert doc1.published_date == "2024-01-15"

        # Date-time format
        doc2 = Document(
            id="law-1234",
            title="Test",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            updated_date="2024-01-15T10:30:00",
        )
        assert doc2.updated_date == "2024-01-15T10:30:00"

        # Date-time with timezone (Z)
        doc3 = Document(
            id="law-1234",
            title="Test",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            updated_date="2024-01-15T10:30:00Z",
        )
        assert doc3.updated_date == "2024-01-15T10:30:00Z"

    def test_document_type_enum(self):
        """Test DocumentType enum values."""
        doc = Document(
            id="law-1234",
            title="Test",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
        )
        assert doc.type == DocumentType.LAW
        assert doc.type.value == "law"

        # Test all enum values
        for doc_type in DocumentType:
            doc = Document(
                id="law-1234",
                title="Test",
                type=doc_type,
                version=Version(number="1.0"),
                source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            )
            assert doc.type == doc_type

    def test_version_object(self):
        """Test Version object structure."""
        # Version with number only
        version1 = Version(number="1.0")
        assert version1.number == "1.0"
        assert version1.description is None

        # Version with number and description
        version2 = Version(number="1.0", description="Initial version")
        assert version2.number == "1.0"
        assert version2.description == "Initial version"

    def test_source_object(self):
        """Test Source object structure."""
        source = Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z")
        assert source.url == "https://example.com/law"
        assert source.fetched_at == "2025-01-20T09:50:00Z"

        # Test invalid fetched_at format
        with pytest.raises(ValidationError) as exc_info:
            Source(url="https://example.com/law", fetched_at="not-a-date")
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error_msg = str(exc_info.value).lower()
        assert "fetched_at" in error_msg or "iso 8601" in error_msg

        # Test invalid URL format
        with pytest.raises(ValidationError) as exc_info:
            Source(url="not-a-url", fetched_at="2025-01-20T09:50:00Z")
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error_msg = str(exc_info.value).lower()
        assert "url" in error_msg or "uri" in error_msg

        # Test URL without scheme
        with pytest.raises(ValidationError) as exc_info:
            Source(url="example.com/law", fetched_at="2025-01-20T09:50:00Z")
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error_msg = str(exc_info.value).lower()
        assert "url" in error_msg or "uri" in error_msg

        # Test URL without netloc
        with pytest.raises(ValidationError) as exc_info:
            Source(url="https://", fetched_at="2025-01-20T09:50:00Z")
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error_msg = str(exc_info.value).lower()
        assert "url" in error_msg or "uri" in error_msg


class TestIntegration:
    """Integration tests for YAML loading and round-trip conversion."""

    def test_load_yaml_file_into_pydantic_models(self, tmp_path, hebrew_text: str):
        """Integration test: Load YAML file into Pydantic models."""
        # Create a test YAML file matching the JSON Schema structure
        yaml_content = f"""
document:
  id: "law-1234"
  title: "חוק יסוד: כבוד האדם וחירותו"
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com/test"
    fetched_at: "2025-01-20T09:50:00Z"
  authors:
    - "הכנסת"
  published_date: "1992-03-17"
  updated_date: "2024-01-15"
  sections:
    - id: "sec-1"
      content: "{hebrew_text}"
      marker: "א"
      title: "סעיף ראשון"
      sections:
        - id: "sec-1-1"
          content: "תוכן משני"
"""

        yaml_file = tmp_path / "test_document.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")

        # Load YAML
        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Extract document from wrapper
        doc_data = data["document"]

        # Convert to Pydantic models
        doc = Document(**doc_data)

        # Verify structure is correct
        assert doc.id == "law-1234"
        assert doc.title == "חוק יסוד: כבוד האדם וחירותו"
        assert doc.type == DocumentType.LAW
        assert doc.language == "hebrew"
        assert doc.version.number == "1.0"
        assert doc.source.url == "https://example.com/test"
        assert doc.authors == ["הכנסת"]
        assert doc.published_date == "1992-03-17"
        assert doc.updated_date == "2024-01-15"
        assert len(doc.sections) == 1
        assert doc.sections[0].id == "sec-1"
        assert doc.sections[0].content == hebrew_text
        assert doc.sections[0].marker == "א"
        assert len(doc.sections[0].sections) == 1
        assert doc.sections[0].sections[0].content == "תוכן משני"

    def test_round_trip_pydantic_to_yaml_to_pydantic(self, hebrew_text: str):
        """Integration test: Round-trip Pydantic → YAML → Pydantic."""
        # Create Pydantic model with all metadata fields
        original_doc = Document(
            id="law-1234",
            title="חוק יסוד: כבוד האדם וחירותו",
            type=DocumentType.LAW,
            language="hebrew",
            version=Version(number="1.0", description="Initial version"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            authors=["הכנסת"],
            published_date="1992-03-17",
            updated_date="2024-01-15",
            sections=[
                Section(
                    id="sec-1",
                    content=hebrew_text,
                    marker="א",
                    title="סעיף ראשון",
                    sections=[
                        Section(
                            id="sec-1-1",
                            content="תוכן משני",
                        ),
                    ],
                ),
            ],
        )

        # Convert to dict (using model_dump with mode="json" to serialize enums as strings)
        doc_dict = original_doc.model_dump(mode="json")

        # Convert to YAML
        yaml_str = yaml.dump(doc_dict, allow_unicode=True, default_flow_style=False)

        # Load YAML back
        loaded_data = yaml.safe_load(yaml_str)

        # Convert to Pydantic
        loaded_doc = Document(**loaded_data)

        # Verify equality (compare key fields)
        assert loaded_doc.id == original_doc.id
        assert loaded_doc.title == original_doc.title
        assert loaded_doc.type == original_doc.type
        assert loaded_doc.language == original_doc.language
        assert loaded_doc.version.number == original_doc.version.number
        assert loaded_doc.version.description == original_doc.version.description
        assert loaded_doc.source.url == original_doc.source.url
        assert loaded_doc.source.fetched_at == original_doc.source.fetched_at
        assert loaded_doc.authors == original_doc.authors
        assert loaded_doc.published_date == original_doc.published_date
        assert loaded_doc.updated_date == original_doc.updated_date
        assert len(loaded_doc.sections) == len(original_doc.sections)
        assert loaded_doc.sections[0].id == original_doc.sections[0].id
        assert loaded_doc.sections[0].content == original_doc.sections[0].content
        assert loaded_doc.sections[0].marker == original_doc.sections[0].marker
        assert loaded_doc.sections[0].title == original_doc.sections[0].title
        assert len(loaded_doc.sections[0].sections) == len(original_doc.sections[0].sections)
        assert loaded_doc.sections[0].sections[0].id == original_doc.sections[0].sections[0].id
        assert (
            loaded_doc.sections[0].sections[0].content
            == original_doc.sections[0].sections[0].content
        )

    def test_round_trip_with_auto_generated_ids(self):
        """Test round-trip preserves auto-generated IDs."""
        # Create document with auto-generated IDs
        original_doc = Document(
            id="law-1234",
            title="Test",
            type=DocumentType.LAW,
            version=Version(number="1.0"),
            source=Source(url="https://example.com/law", fetched_at="2025-01-20T09:50:00Z"),
            sections=[
                Section(content="Section 1", sections=[Section(content="Section 1.1")]),
            ],
        )

        # Get the IDs
        section1_id = original_doc.sections[0].id
        section1_1_id = original_doc.sections[0].sections[0].id

        # Round-trip (use mode="json" to serialize enums as strings)
        doc_dict = original_doc.model_dump(mode="json")
        yaml_str = yaml.dump(doc_dict, allow_unicode=True)
        loaded_data = yaml.safe_load(yaml_str)
        loaded_doc = Document(**loaded_data)

        # Verify IDs are preserved
        assert loaded_doc.sections[0].id == section1_id
        assert loaded_doc.sections[0].sections[0].id == section1_1_id


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_content_string(self, sample_id: str):
        """Test section with empty content string."""
        section = Section(id=sample_id, content="")
        assert section.content == ""

    def test_very_long_hebrew_text(self, sample_id: str):
        """Test section with very long Hebrew text."""
        long_text = "חוק יסוד: כבוד האדם וחירותו " * 100
        section = Section(id=sample_id, content=long_text)
        assert len(section.content) > 1000
        assert section.content.startswith("חוק יסוד")

    def test_multiple_nested_sections(self, sample_id: str):
        """Test section with multiple nested sections."""
        section = Section(
            id=sample_id,
            content="Parent",
            sections=[
                Section(id="sec-1", content="Child 1"),
                Section(id="sec-2", content="Child 2"),
                Section(id="sec-3", content="Child 3"),
            ],
        )
        assert len(section.sections) == 3
        assert section.sections[0].content == "Child 1"
        assert section.sections[1].content == "Child 2"
        assert section.sections[2].content == "Child 3"

    def test_id_as_string(self, sample_id: str):
        """Test that ID can be provided as string."""
        section = Section(id=sample_id)
        assert isinstance(section.id, str)
        assert section.id == sample_id

        # Test with custom string ID (not UUID)
        section2 = Section(id="sec-1")
        assert section2.id == "sec-1"
        assert isinstance(section2.id, str)
