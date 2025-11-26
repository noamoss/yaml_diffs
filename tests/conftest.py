"""Shared pytest fixtures for yaml-diffs test suite.

This module provides reusable fixtures for testing across the entire test suite.
Fixtures are organized by category: documents, sections, files, and mocks.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from yaml_diffs.models import Document, DocumentType, Section, Source, Version

if TYPE_CHECKING:
    from collections.abc import Generator

# ============================================================================
# Path and File Fixtures
# ============================================================================


@pytest.fixture
def examples_dir() -> Path:
    """Path to the examples directory."""
    return Path(__file__).parent.parent / "examples"


@pytest.fixture
def minimal_document_path(examples_dir: Path) -> Path:
    """Path to the minimal example document."""
    return examples_dir / "minimal_document.yaml"


@pytest.fixture
def document_v1_path(examples_dir: Path) -> Path:
    """Path to document version 1 example."""
    return examples_dir / "document_v1.yaml"


@pytest.fixture
def document_v2_path(examples_dir: Path) -> Path:
    """Path to document version 2 example."""
    return examples_dir / "document_v2.yaml"


@pytest.fixture
def complex_document_path(examples_dir: Path) -> Path:
    """Path to the complex example document."""
    return examples_dir / "complex_document.yaml"


@pytest.fixture
def tmp_yaml_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary YAML file for testing.

    Yields:
        Path to temporary YAML file
    """
    file_path = tmp_path / "test.yaml"
    yield file_path
    if file_path.exists():
        file_path.unlink()


# ============================================================================
# ID and UUID Fixtures
# ============================================================================


@pytest.fixture
def sample_id() -> str:
    """Generate a sample UUID string for testing."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_uuid() -> str:
    """Generate a sample UUID string for testing (backward compatibility)."""
    return str(uuid.uuid4())


# ============================================================================
# Content Fixtures
# ============================================================================


@pytest.fixture
def hebrew_text() -> str:
    """Sample Hebrew text for testing."""
    return "חוק יסוד: כבוד האדם וחירותו"


@pytest.fixture
def minimal_yaml_content() -> str:
    """Minimal valid YAML document content."""
    return """document:
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


@pytest.fixture
def minimal_yaml_file(tmp_path: Path, minimal_yaml_content: str) -> Path:
    """Create a temporary YAML file with minimal content."""
    file_path = tmp_path / "minimal.yaml"
    file_path.write_text(minimal_yaml_content, encoding="utf-8")
    return file_path


# ============================================================================
# Section Fixtures
# ============================================================================


@pytest.fixture
def minimal_section(sample_id: str) -> Section:
    """Create a minimal section with id and marker."""
    return Section(id=sample_id, marker="1")


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
def nested_section(sample_id: str) -> Section:
    """Create a section with nested subsections."""
    child1_id = str(uuid.uuid4())
    child2_id = str(uuid.uuid4())
    return Section(
        id=sample_id,
        marker="1",
        title="סעיף ראשי",
        content="תוכן ראשי",
        sections=[
            Section(id=child1_id, marker="א", content="תוכן משנה א"),
            Section(id=child2_id, marker="ב", content="תוכן משנה ב"),
        ],
    )


@pytest.fixture
def deeply_nested_section(sample_id: str) -> Section:
    """Create a section with deep nesting (5+ levels)."""
    level5_id = str(uuid.uuid4())
    level4_id = str(uuid.uuid4())
    level3_id = str(uuid.uuid4())
    level2_id = str(uuid.uuid4())

    level5 = Section(id=level5_id, marker="א", content="Level 5")
    level4 = Section(id=level4_id, marker="4", content="Level 4", sections=[level5])
    level3 = Section(id=level3_id, marker="3", content="Level 3", sections=[level4])
    level2 = Section(id=level2_id, marker="2", content="Level 2", sections=[level3])

    return Section(id=sample_id, marker="1", content="Level 1", sections=[level2])


# ============================================================================
# Document Fixtures
# ============================================================================


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


@pytest.fixture
def full_document(sample_id: str, hebrew_text: str) -> Document:
    """Create a document with all fields and sections."""
    section1_id = str(uuid.uuid4())
    section2_id = str(uuid.uuid4())

    return Document(
        id="law-5678",
        title="חוק מלא",
        type=DocumentType.LAW,
        language="hebrew",
        version=Version(number="2.0", description="גרסה שנייה"),
        source=Source(
            url="https://example.com/law5678",
            fetched_at="2025-01-20T09:50:00Z",
        ),
        sections=[
            Section(
                id=section1_id,
                marker="1",
                title="סעיף ראשון",
                content=hebrew_text,
            ),
            Section(
                id=section2_id,
                marker="2",
                title="סעיף שני",
                content="תוכן נוסף",
            ),
        ],
    )


@pytest.fixture
def complex_document(sample_id: str) -> Document:
    """Create a complex document with deep nesting and multiple sections."""
    # Create nested structure
    nested_section_id = str(uuid.uuid4())
    nested_child_id = str(uuid.uuid4())

    nested_child = Section(
        id=nested_child_id,
        marker="(א)",
        title="תת-סעיף",
        content="תוכן תת-סעיף",
    )

    nested = Section(
        id=nested_section_id,
        marker="1",
        title="סעיף מקונן",
        content="תוכן מקונן",
        sections=[nested_child],
    )

    section1_id = str(uuid.uuid4())
    section2_id = str(uuid.uuid4())

    return Document(
        id="reg-complex-001",
        title="תקנה מורכבת",
        type=DocumentType.REGULATION,
        language="hebrew",
        version=Version(number="1.0"),
        source=Source(
            url="https://example.com/regulation",
            fetched_at="2025-01-20T09:50:00Z",
        ),
        sections=[
            Section(
                id=section1_id,
                marker="פרק א'",
                title="פרק ראשון",
                content="תוכן הפרק",
                sections=[nested],
            ),
            Section(
                id=section2_id,
                marker="פרק ב'",
                title="פרק שני",
                content="תוכן נוסף",
            ),
        ],
    )


@pytest.fixture
def document_with_hebrew_content() -> Document:
    """Create a document with Hebrew content throughout."""
    section_id = str(uuid.uuid4())
    return Document(
        id="hebrew-doc-001",
        title="מסמך בעברית",
        type=DocumentType.LAW,
        language="hebrew",
        version=Version(number="1.0"),
        source=Source(
            url="https://example.com/hebrew",
            fetched_at="2025-01-20T09:50:00Z",
        ),
        sections=[
            Section(
                id=section_id,
                marker="א",
                title="סעיף בעברית",
                content="זהו תוכן בעברית עם ניקוד: אָבִיב, קַיִץ, סְתָו, חֹרֶף",
            ),
        ],
    )


# ============================================================================
# Document Pair Fixtures (for diffing)
# ============================================================================


@pytest.fixture
def document_pair_for_diff() -> tuple[Document, Document]:
    """Create a pair of documents for diffing tests."""
    section_id = str(uuid.uuid4())

    old_doc = Document(
        id="doc-001",
        title="מסמך ישן",
        type=DocumentType.LAW,
        version=Version(number="1.0"),
        source=Source(
            url="https://example.com/doc",
            fetched_at="2025-01-20T09:50:00Z",
        ),
        sections=[
            Section(
                id=section_id,
                marker="1",
                title="סעיף ראשון",
                content="תוכן ישן",
            ),
        ],
    )

    new_doc = Document(
        id="doc-001",
        title="מסמך חדש",
        type=DocumentType.LAW,
        version=Version(number="2.0"),
        source=Source(
            url="https://example.com/doc",
            fetched_at="2025-01-21T09:50:00Z",
        ),
        sections=[
            Section(
                id=section_id,
                marker="1",
                title="סעיף ראשון",
                content="תוכן חדש",
            ),
            Section(
                id=str(uuid.uuid4()),
                marker="2",
                title="סעיף שני",
                content="תוכן נוסף",
            ),
        ],
    )

    return (old_doc, new_doc)


# ============================================================================
# Mock and External Dependency Fixtures
# ============================================================================


@pytest.fixture
def mock_api_client():
    """Mock API client for testing MCP server and API interactions."""
    from unittest.mock import AsyncMock, MagicMock

    mock_client = MagicMock()
    mock_client.validate_document = AsyncMock(return_value={"valid": True})
    mock_client.diff_documents = AsyncMock(return_value={"diff": {}})
    mock_client.health_check = AsyncMock(return_value={"status": "healthy"})
    mock_client.close = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client
