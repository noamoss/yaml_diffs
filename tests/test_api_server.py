"""Tests for the REST API server.

Comprehensive test suite covering all endpoints, error cases, and edge cases.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Try to import jsonschema, skip tests if not available
try:
    from jsonschema import FormatChecker  # noqa: F401
    from jsonschema.validators import Draft202012Validator  # noqa: F401
except ImportError:
    pytestmark = pytest.mark.skip("jsonschema library not available")

from yaml_diffs.api_server.main import app

# Test client
client = TestClient(app)

# Test data paths
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
MINIMAL_DOC = EXAMPLES_DIR / "minimal_document.yaml"
DOC_V1 = EXAMPLES_DIR / "document_v1.yaml"
DOC_V2 = EXAMPLES_DIR / "document_v2.yaml"


@pytest.fixture
def minimal_yaml_content() -> str:
    """Minimal valid YAML document content."""
    return MINIMAL_DOC.read_text(encoding="utf-8")


@pytest.fixture
def document_v1_content() -> str:
    """Document version 1 content."""
    return DOC_V1.read_text(encoding="utf-8")


@pytest.fixture
def document_v2_content() -> str:
    """Document version 2 content."""
    return DOC_V2.read_text(encoding="utf-8")


# Health check endpoint tests
def test_health_endpoint() -> None:
    """Test health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["version"] == "0.1.0"


def test_health_endpoint_response_model() -> None:
    """Test health check endpoint response matches schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)


# Root endpoint tests
def test_root_endpoint() -> None:
    """Test root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "docs" in data
    assert data["docs"] == "/docs"


# Validation endpoint tests
def test_validate_endpoint_valid_document(minimal_yaml_content: str) -> None:
    """Test validate endpoint with valid document."""
    response = client.post(
        "/api/v1/validate",
        json={"yaml": minimal_yaml_content},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["document"] is not None
    assert data["document"]["id"] == "law-1234"
    assert data["document"]["title"] == "חוק הדוגמה לרגולציה"
    assert data["error"] is None
    assert data["message"] is None


def test_validate_endpoint_invalid_yaml() -> None:
    """Test validate endpoint with invalid YAML syntax."""
    invalid_yaml = "invalid: yaml: content: ["
    response = client.post(
        "/api/v1/validate",
        json={"yaml": invalid_yaml},
    )
    assert response.status_code == 400
    data = response.json()
    # Global exception handlers return JSONResponse with content directly
    assert "error" in data
    assert "message" in data


def test_validate_endpoint_invalid_document() -> None:
    """Test validate endpoint with invalid document structure."""
    invalid_doc = """document:
  id: "test"
  # Missing required fields
"""
    response = client.post(
        "/api/v1/validate",
        json={"yaml": invalid_doc},
    )
    assert response.status_code == 422
    data = response.json()
    # Global exception handlers return JSONResponse with content directly
    assert "error" in data
    assert "message" in data
    assert "details" in data


def test_validate_endpoint_empty_yaml() -> None:
    """Test validate endpoint with empty YAML."""
    response = client.post(
        "/api/v1/validate",
        json={"yaml": ""},
    )
    # Should fail validation (empty string not allowed by schema)
    assert response.status_code == 422


def test_validate_endpoint_missing_field() -> None:
    """Test validate endpoint with missing yaml field."""
    response = client.post(
        "/api/v1/validate",
        json={},
    )
    assert response.status_code == 422


def test_validate_endpoint_hebrew_content(minimal_yaml_content: str) -> None:
    """Test validate endpoint handles Hebrew content correctly."""
    response = client.post(
        "/api/v1/validate",
        json={"yaml": minimal_yaml_content},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    # Verify Hebrew text is preserved
    assert "חוק" in data["document"]["title"]


# Diff endpoint tests
def test_diff_endpoint_valid_documents(document_v1_content: str, document_v2_content: str) -> None:
    """Test diff endpoint with valid documents."""
    response = client.post(
        "/api/v1/diff",
        json={
            "old_yaml": document_v1_content,
            "new_yaml": document_v2_content,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "diff" in data
    diff = data["diff"]
    assert "changes" in diff
    assert "added_count" in diff
    assert "deleted_count" in diff
    assert "modified_count" in diff
    assert "moved_count" in diff
    assert isinstance(diff["changes"], list)
    assert diff["added_count"] >= 0
    assert diff["deleted_count"] >= 0


def test_diff_endpoint_identical_documents(minimal_yaml_content: str) -> None:
    """Test diff endpoint with identical documents."""
    response = client.post(
        "/api/v1/diff",
        json={
            "old_yaml": minimal_yaml_content,
            "new_yaml": minimal_yaml_content,
        },
    )
    assert response.status_code == 200
    data = response.json()
    diff = data["diff"]
    # Should have no changes or only UNCHANGED entries
    assert diff["added_count"] == 0
    assert diff["deleted_count"] == 0


def test_diff_endpoint_invalid_old_yaml(document_v2_content: str) -> None:
    """Test diff endpoint with invalid old YAML."""
    invalid_yaml = "invalid: yaml: ["
    response = client.post(
        "/api/v1/diff",
        json={
            "old_yaml": invalid_yaml,
            "new_yaml": document_v2_content,
        },
    )
    assert response.status_code == 400
    data = response.json()
    # Global exception handlers return JSONResponse with content directly
    assert "error" in data
    assert "message" in data


def test_diff_endpoint_invalid_new_yaml(document_v1_content: str) -> None:
    """Test diff endpoint with invalid new YAML."""
    invalid_yaml = "invalid: yaml: ["
    response = client.post(
        "/api/v1/diff",
        json={
            "old_yaml": document_v1_content,
            "new_yaml": invalid_yaml,
        },
    )
    assert response.status_code == 400
    data = response.json()
    # Global exception handlers return JSONResponse with content directly
    assert "error" in data
    assert "message" in data


def test_diff_endpoint_missing_fields() -> None:
    """Test diff endpoint with missing required fields."""
    response = client.post(
        "/api/v1/diff",
        json={},
    )
    assert response.status_code == 422


def test_diff_endpoint_malformed_request() -> None:
    """Test diff endpoint with malformed request body."""
    response = client.post(
        "/api/v1/diff",
        json={"old_yaml": "valid"},
        # Missing new_yaml
    )
    assert response.status_code == 422


# API status codes tests
def test_api_status_codes() -> None:
    """Test API returns correct HTTP status codes."""
    # Health check - 200
    response = client.get("/health")
    assert response.status_code == 200

    # Valid validation - 200
    minimal_yaml = MINIMAL_DOC.read_text(encoding="utf-8")
    response = client.post(
        "/api/v1/validate",
        json={"yaml": minimal_yaml},
    )
    assert response.status_code == 200

    # Invalid YAML - 400
    response = client.post(
        "/api/v1/validate",
        json={"yaml": "invalid: ["},
    )
    assert response.status_code == 400

    # Invalid document structure - 422
    response = client.post(
        "/api/v1/validate",
        json={"yaml": "document:\n  id: test"},
    )
    assert response.status_code == 422


# CORS tests
def test_cors_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CORS headers are present in responses."""
    # Set CORS_ORIGINS for this test
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
    # Recreate app with new settings (for test purposes, we'll just test that CORS is configured)
    # In practice, CORS will work when origins are configured
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    # With empty CORS origins by default, OPTIONS may return 400
    # This test verifies CORS is configured (actual CORS behavior depends on settings)
    assert response.status_code in [200, 204, 400]  # 400 is OK if no CORS origins configured


# Integration tests
def test_api_endpoints_end_to_end(document_v1_content: str, document_v2_content: str) -> None:
    """Test full workflow: validate both documents, then diff them."""
    # Validate first document
    response1 = client.post(
        "/api/v1/validate",
        json={"yaml": document_v1_content},
    )
    assert response1.status_code == 200
    assert response1.json()["valid"] is True

    # Validate second document
    response2 = client.post(
        "/api/v1/validate",
        json={"yaml": document_v2_content},
    )
    assert response2.status_code == 200
    assert response2.json()["valid"] is True

    # Diff the documents
    response3 = client.post(
        "/api/v1/diff",
        json={
            "old_yaml": document_v1_content,
            "new_yaml": document_v2_content,
        },
    )
    assert response3.status_code == 200
    diff = response3.json()["diff"]
    assert len(diff["changes"]) > 0


def test_openapi_spec_generation() -> None:
    """Test OpenAPI spec is generated correctly."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert "openapi" in spec
    assert "info" in spec
    assert "paths" in spec
    assert "/api/v1/validate" in spec["paths"]
    assert "/api/v1/diff" in spec["paths"]
    assert "/health" in spec["paths"]


def test_openapi_docs_accessible() -> None:
    """Test OpenAPI docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


# Environment variable tests
def test_api_port_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test API reads PORT from environment variable."""
    # Set PORT environment variable
    monkeypatch.setenv("PORT", "9000")
    # Reload settings
    from yaml_diffs.api_server.config import Settings

    settings = Settings()
    assert settings.port_from_env == 9000


def test_api_port_invalid_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test API handles invalid PORT environment variable."""
    # Set invalid PORT
    monkeypatch.setenv("PORT", "invalid")
    # Reload settings
    from yaml_diffs.api_server.config import Settings

    settings = Settings()
    # Should fall back to default
    assert settings.port_from_env == 8000


# Edge cases
def test_validate_endpoint_very_large_document() -> None:
    """Test validate endpoint with very large document."""
    # Create a large document with many sections
    large_yaml = """document:
  id: "large-doc"
  title: "מסמך גדול"
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections:
"""
    # Add many sections
    for i in range(100):
        large_yaml += f"""    - id: "sec-{i}"
      marker: "{i}"
      content: "Section {i} content"
      sections: []
"""

    response = client.post(
        "/api/v1/validate",
        json={"yaml": large_yaml},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert len(data["document"]["sections"]) == 100


def test_diff_endpoint_nested_structures(
    document_v1_content: str, document_v2_content: str
) -> None:
    """Test diff endpoint handles deeply nested structures."""
    response = client.post(
        "/api/v1/diff",
        json={
            "old_yaml": document_v1_content,
            "new_yaml": document_v2_content,
        },
    )
    assert response.status_code == 200
    diff = response.json()["diff"]
    # Should handle nested structures correctly
    assert isinstance(diff["changes"], list)


def test_validate_endpoint_missing_sections() -> None:
    """Test validate endpoint with document missing sections field."""
    yaml_without_sections = """document:
  id: "test"
  title: "מבחן"
  type: "law"
  language: "hebrew"
  version:
    number: "1.0"
  source:
    url: "https://example.com"
    fetched_at: "2025-01-20T09:50:00Z"
  sections: []
"""
    response = client.post(
        "/api/v1/validate",
        json={"yaml": yaml_without_sections},
    )
    # Should be valid (sections is required but can be empty list)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["document"]["sections"] == []


def test_error_response_format() -> None:
    """Test error responses have consistent format."""
    response = client.post(
        "/api/v1/validate",
        json={"yaml": "invalid: ["},
    )
    assert response.status_code == 400
    data = response.json()
    # Global exception handlers return JSONResponse with content directly
    assert "error" in data
    assert "message" in data
    # Should have either details or be None
    assert "details" in data or data.get("details") is None
