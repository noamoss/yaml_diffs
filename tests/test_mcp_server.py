"""Unit tests for MCP server components.

Tests configuration, client, and server initialization.
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from yaml_diffs.mcp_server.client import APIClient
from yaml_diffs.mcp_server.config import MCPServerConfig


class TestMCPServerConfig:
    """Tests for MCPServerConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = MCPServerConfig()
        assert config.api_base_url == "http://localhost:8000"
        assert config.api_key is None
        assert config.timeout == 30

    def test_config_from_parameters(self) -> None:
        """Test configuration from parameters."""
        config = MCPServerConfig(
            api_base_url="http://api.example.com:9000",
            api_key="test-key",
            timeout=60,
        )
        assert config.api_base_url == "http://api.example.com:9000"
        assert config.api_key == "test-key"
        assert config.timeout == 60

    def test_config_from_env_vars(self) -> None:
        """Test configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "YAML_DIFFS_API_URL": "http://env.example.com:8000",
                "YAML_DIFFS_API_KEY": "env-key",
                "YAML_DIFFS_API_TIMEOUT": "45",
            },
        ):
            config = MCPServerConfig()
            assert config.api_base_url == "http://env.example.com:8000"
            assert config.api_key == "env-key"
            assert config.timeout == 45

    def test_config_env_override_parameters(self) -> None:
        """Test that parameters override environment variables."""
        with patch.dict(
            os.environ,
            {
                "YAML_DIFFS_API_URL": "http://env.example.com:8000",
                "YAML_DIFFS_API_KEY": "env-key",
            },
        ):
            config = MCPServerConfig(
                api_base_url="http://param.example.com:9000",
                api_key="param-key",
            )
            assert config.api_base_url == "http://param.example.com:9000"
            assert config.api_key == "param-key"

    def test_config_invalid_timeout(self) -> None:
        """Test configuration with invalid timeout value."""
        with patch.dict(os.environ, {"YAML_DIFFS_API_TIMEOUT": "invalid"}):
            config = MCPServerConfig()
            assert config.timeout == 30  # Should use default

    def test_config_timeout_zero(self) -> None:
        """Test that timeout=0 is handled correctly (not treated as falsy)."""
        config = MCPServerConfig(timeout=0)
        assert config.timeout == 0  # Should preserve 0, not use default

    def test_config_timeout_zero_with_env(self) -> None:
        """Test that timeout=0 parameter overrides environment variable."""
        with patch.dict(os.environ, {"YAML_DIFFS_API_TIMEOUT": "45"}):
            config = MCPServerConfig(timeout=0)
            assert config.timeout == 0  # Should use parameter, not env var

    def test_config_url_trailing_slash_removed(self) -> None:
        """Test that trailing slashes are removed from API URL."""
        config = MCPServerConfig(api_base_url="http://example.com/")
        assert config.api_base_url == "http://example.com"

    def test_config_invalid_url_no_scheme(self) -> None:
        """Test that invalid URL without scheme raises ValueError."""
        with pytest.raises(ValueError, match="Invalid API base URL"):
            MCPServerConfig(api_base_url="not-a-url")

    def test_config_invalid_url_no_netloc(self) -> None:
        """Test that invalid URL without netloc raises ValueError."""
        with pytest.raises(ValueError, match="Invalid API base URL"):
            MCPServerConfig(api_base_url="http://")

    def test_config_invalid_url_empty_string(self) -> None:
        """Test that empty string URL falls back to default (not an error)."""
        # Empty string is treated as falsy and falls back to default
        config = MCPServerConfig(api_base_url="")
        assert config.api_base_url == "http://localhost:8000"

    def test_config_valid_urls(self) -> None:
        """Test that valid URLs are accepted."""
        valid_urls = [
            "http://localhost:8000",
            "https://api.example.com",
            "http://192.168.1.1:9000",
            "https://example.com:443/path",
        ]
        for url in valid_urls:
            config = MCPServerConfig(api_base_url=url)
            assert config.api_base_url == url.rstrip("/")

    def test_config_repr(self) -> None:
        """Test string representation of configuration."""
        config = MCPServerConfig(api_key="secret-key")
        repr_str = repr(config)
        assert "MCPServerConfig" in repr_str
        assert "api_base_url" in repr_str
        assert "secret-key" not in repr_str  # Should be masked
        assert "***" in repr_str


class TestAPIClient:
    """Tests for APIClient."""

    @pytest.mark.asyncio
    async def test_client_initialization(self) -> None:
        """Test API client initialization."""
        config = MCPServerConfig()
        client = APIClient(config)
        assert client.config == config
        assert client._client.base_url == config.api_base_url
        await client.close()

    @pytest.mark.asyncio
    async def test_client_headers_without_auth(self) -> None:
        """Test HTTP headers without authentication."""
        config = MCPServerConfig()
        client = APIClient(config)
        headers = client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert "Authorization" not in headers
        await client.close()

    @pytest.mark.asyncio
    async def test_client_headers_with_auth(self) -> None:
        """Test HTTP headers with authentication."""
        config = MCPServerConfig(api_key="test-key")
        client = APIClient(config)
        headers = client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test-key"
        await client.close()

    @patch("yaml_diffs.mcp_server.client.httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_validate_document_success(self, mock_client_class: MagicMock) -> None:
        """Test successful document validation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"valid": True, "document": {"id": "test"}}
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client

        config = MCPServerConfig()
        client = APIClient(config)
        result = await client.validate_document("document: id: test")

        assert result == {"valid": True, "document": {"id": "test"}}
        mock_client.post.assert_called_once_with(
            "/api/v1/validate",
            json={"yaml": "document: id: test"},
        )
        await client.close()

    @patch("yaml_diffs.mcp_server.client.httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_validate_document_error(self, mock_client_class: MagicMock) -> None:
        """Test document validation with API error."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=MagicMock(), response=mock_response
        )

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client

        config = MCPServerConfig()
        client = APIClient(config)

        with pytest.raises(httpx.HTTPStatusError):
            await client.validate_document("invalid yaml")

        await client.close()

    @patch("yaml_diffs.mcp_server.client.httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_diff_documents_success(self, mock_client_class: MagicMock) -> None:
        """Test successful document diffing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"diff": {"changes": []}}
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client

        config = MCPServerConfig()
        client = APIClient(config)
        result = await client.diff_documents("old: yaml", "new: yaml")

        assert result == {"diff": {"changes": []}}
        mock_client.post.assert_called_once_with(
            "/api/v1/diff",
            json={"old_yaml": "old: yaml", "new_yaml": "new: yaml"},
        )
        await client.close()

    @patch("yaml_diffs.mcp_server.client.httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_client_class: MagicMock) -> None:
        """Test successful health check."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "healthy", "version": "0.1.0"}
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client

        config = MCPServerConfig()
        client = APIClient(config)
        result = await client.health_check()

        assert result == {"status": "healthy", "version": "0.1.0"}
        mock_client.get.assert_called_once_with("/health")
        await client.close()

    @pytest.mark.asyncio
    async def test_client_context_manager(self) -> None:
        """Test API client as async context manager."""
        config = MCPServerConfig()
        async with APIClient(config) as client:
            assert client.config == config
        # Client should be closed after context exit
        assert client._client.is_closed

    @patch("yaml_diffs.mcp_server.client.httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_client_timeout_zero_converted_to_none(
        self, mock_client_class: MagicMock
    ) -> None:
        """Test that timeout=0 is converted to None for httpx.AsyncClient."""
        mock_client = MagicMock()
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client

        config = MCPServerConfig(timeout=0)
        client = APIClient(config)
        # Verify httpx.AsyncClient was called with timeout=None
        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs["timeout"] is None
        await client.close()

    @patch("yaml_diffs.mcp_server.client.httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_client_timeout_positive_preserved(self, mock_client_class: MagicMock) -> None:
        """Test that positive timeout values are preserved."""
        mock_client = MagicMock()
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client

        config = MCPServerConfig(timeout=60)
        client = APIClient(config)
        # Verify httpx.AsyncClient was called with timeout=60
        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs["timeout"] == 60
        await client.close()
