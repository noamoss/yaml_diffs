"""Unit tests for MCP tool handlers.

Tests tool definitions and handler functions.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from yaml_diffs.mcp_server.client import APIClient
from yaml_diffs.mcp_server.config import MCPServerConfig
from yaml_diffs.mcp_server.tools import (
    call_tool,
    get_tool_definitions,
    handle_diff_documents,
    handle_health_check,
    handle_validate_document,
)


class TestToolDefinitions:
    """Tests for tool definitions."""

    def test_get_tool_definitions(self) -> None:
        """Test that tool definitions are returned correctly."""
        tools = get_tool_definitions()
        assert len(tools) == 3

        tool_names = [tool.name for tool in tools]
        assert "validate_document" in tool_names
        assert "diff_documents" in tool_names
        assert "health_check" in tool_names

    def test_validate_document_tool_schema(self) -> None:
        """Test validate_document tool schema."""
        tools = get_tool_definitions()
        validate_tool = next(t for t in tools if t.name == "validate_document")

        assert validate_tool.name == "validate_document"
        assert "validate" in validate_tool.description.lower()
        assert validate_tool.inputSchema["type"] == "object"
        assert "yaml" in validate_tool.inputSchema["properties"]
        assert "yaml" in validate_tool.inputSchema["required"]

    def test_diff_documents_tool_schema(self) -> None:
        """Test diff_documents tool schema."""
        tools = get_tool_definitions()
        diff_tool = next(t for t in tools if t.name == "diff_documents")

        assert diff_tool.name == "diff_documents"
        assert "diff" in diff_tool.description.lower() or "compare" in diff_tool.description.lower()
        assert diff_tool.inputSchema["type"] == "object"
        assert "old_yaml" in diff_tool.inputSchema["properties"]
        assert "new_yaml" in diff_tool.inputSchema["properties"]
        assert "old_yaml" in diff_tool.inputSchema["required"]
        assert "new_yaml" in diff_tool.inputSchema["required"]

    def test_health_check_tool_schema(self) -> None:
        """Test health_check tool schema."""
        tools = get_tool_definitions()
        health_tool = next(t for t in tools if t.name == "health_check")

        assert health_tool.name == "health_check"
        assert "health" in health_tool.description.lower()
        assert health_tool.inputSchema["type"] == "object"
        assert len(health_tool.inputSchema.get("required", [])) == 0


class TestToolHandlers:
    """Tests for tool handler functions."""

    @pytest.fixture
    def mock_client(self) -> APIClient:
        """Create a mock API client."""
        config = MCPServerConfig()
        client = MagicMock(spec=APIClient)
        client.config = config
        return client

    @pytest.mark.asyncio
    async def test_handle_validate_document_success(self, mock_client: APIClient) -> None:
        """Test successful document validation handler."""
        mock_client.validate_document = AsyncMock(
            return_value={
                "valid": True,
                "document": {"id": "test", "type": "law"},
            }
        )

        result = await handle_validate_document(mock_client, {"yaml": "document: id: test"})

        assert len(result) == 1
        assert result[0].type == "text"
        response_data = json.loads(result[0].text)
        assert response_data["valid"] is True
        assert response_data["document"]["id"] == "test"
        mock_client.validate_document.assert_called_once_with("document: id: test")

    @pytest.mark.asyncio
    async def test_handle_validate_document_missing_arg(self, mock_client: APIClient) -> None:
        """Test validate_document handler with missing argument."""
        with pytest.raises(ValueError, match="Missing required argument: yaml"):
            await handle_validate_document(mock_client, {})

    @pytest.mark.asyncio
    async def test_handle_validate_document_error(self, mock_client: APIClient) -> None:
        """Test validate_document handler with API error."""
        mock_client.validate_document = AsyncMock(side_effect=Exception("API error"))

        result = await handle_validate_document(mock_client, {"yaml": "invalid"})

        assert len(result) == 1
        assert result[0].type == "text"
        response_data = json.loads(result[0].text)
        assert response_data["valid"] is False
        assert "error" in response_data
        assert "message" in response_data

    @pytest.mark.asyncio
    async def test_handle_diff_documents_success(self, mock_client: APIClient) -> None:
        """Test successful document diffing handler."""
        mock_client.diff_documents = AsyncMock(
            return_value={"diff": {"changes": [], "added_count": 0, "deleted_count": 0}}
        )

        result = await handle_diff_documents(
            mock_client, {"old_yaml": "old: yaml", "new_yaml": "new: yaml"}
        )

        assert len(result) == 1
        assert result[0].type == "text"
        response_data = json.loads(result[0].text)
        assert "diff" in response_data
        mock_client.diff_documents.assert_called_once_with("old: yaml", "new: yaml")

    @pytest.mark.asyncio
    async def test_handle_diff_documents_missing_old(self, mock_client: APIClient) -> None:
        """Test diff_documents handler with missing old_yaml argument."""
        with pytest.raises(ValueError, match="Missing required argument: old_yaml"):
            await handle_diff_documents(mock_client, {"new_yaml": "new: yaml"})

    @pytest.mark.asyncio
    async def test_handle_diff_documents_missing_new(self, mock_client: APIClient) -> None:
        """Test diff_documents handler with missing new_yaml argument."""
        with pytest.raises(ValueError, match="Missing required argument: new_yaml"):
            await handle_diff_documents(mock_client, {"old_yaml": "old: yaml"})

    @pytest.mark.asyncio
    async def test_handle_diff_documents_error(self, mock_client: APIClient) -> None:
        """Test diff_documents handler with API error."""
        mock_client.diff_documents = AsyncMock(side_effect=Exception("API error"))

        result = await handle_diff_documents(
            mock_client, {"old_yaml": "old: yaml", "new_yaml": "new: yaml"}
        )

        assert len(result) == 1
        assert result[0].type == "text"
        response_data = json.loads(result[0].text)
        assert "error" in response_data
        assert "message" in response_data

    @pytest.mark.asyncio
    async def test_handle_health_check_success(self, mock_client: APIClient) -> None:
        """Test successful health check handler."""
        mock_client.health_check = AsyncMock(return_value={"status": "healthy", "version": "0.1.0"})

        result = await handle_health_check(mock_client, {})

        assert len(result) == 1
        assert result[0].type == "text"
        response_data = json.loads(result[0].text)
        assert response_data["status"] == "healthy"
        assert response_data["version"] == "0.1.0"
        mock_client.health_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_health_check_error(self, mock_client: APIClient) -> None:
        """Test health_check handler with API error."""
        mock_client.health_check = AsyncMock(side_effect=Exception("API error"))

        result = await handle_health_check(mock_client, {})

        assert len(result) == 1
        assert result[0].type == "text"
        response_data = json.loads(result[0].text)
        assert response_data["status"] == "unhealthy"
        assert "error" in response_data
        assert "message" in response_data

    @pytest.mark.asyncio
    async def test_call_tool_validate(self, mock_client: APIClient) -> None:
        """Test call_tool with validate_document."""
        mock_client.validate_document = AsyncMock(return_value={"valid": True})

        result = await call_tool(mock_client, "validate_document", {"yaml": "test"})

        assert len(result) == 1
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_call_tool_diff(self, mock_client: APIClient) -> None:
        """Test call_tool with diff_documents."""
        mock_client.diff_documents = AsyncMock(return_value={"diff": {}})

        result = await call_tool(
            mock_client, "diff_documents", {"old_yaml": "old", "new_yaml": "new"}
        )

        assert len(result) == 1
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_call_tool_health(self, mock_client: APIClient) -> None:
        """Test call_tool with health_check."""
        mock_client.health_check = AsyncMock(return_value={"status": "healthy"})

        result = await call_tool(mock_client, "health_check", {})

        assert len(result) == 1
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_call_tool_unknown(self, mock_client: APIClient) -> None:
        """Test call_tool with unknown tool name."""
        with pytest.raises(ValueError, match="Unknown tool: unknown_tool"):
            await call_tool(mock_client, "unknown_tool", {})
