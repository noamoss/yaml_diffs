"""Configuration for MCP server.

Handles environment variables and configuration for API connection and authentication.
"""

from __future__ import annotations

import logging
import os
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class MCPServerConfig:
    """Configuration for MCP server.

    Loads configuration from environment variables with sensible defaults.
    Supports both local development and production API instances.

    Attributes:
        api_base_url: Base URL for the yaml-diffs API (default: "http://localhost:8000").
        api_key: Optional API key for authentication (default: None).
        timeout: Request timeout in seconds (default: 30).
    """

    def __init__(
        self,
        api_base_url: str | None = None,
        api_key: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """Initialize configuration from parameters or environment variables.

        Args:
            api_base_url: Override API base URL. If None, uses YAML_DIFFS_API_URL env var
                or defaults to "http://localhost:8000".
            api_key: Override API key. If None, uses YAML_DIFFS_API_KEY env var or None.
            timeout: Override timeout. If None, uses YAML_DIFFS_API_TIMEOUT env var
                or defaults to 30 seconds.
        """
        base_url = api_base_url or os.getenv("YAML_DIFFS_API_URL", "http://localhost:8000")
        assert base_url is not None  # Type narrowing for mypy
        base_url = base_url.rstrip("/")

        # Validate URL format
        parsed = urlparse(base_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(
                f"Invalid API base URL: {base_url}. URL must include scheme (http/https) and netloc (hostname)"
            )

        self.api_base_url = base_url

        self.api_key = api_key or os.getenv("YAML_DIFFS_API_KEY")

        timeout_str = os.getenv("YAML_DIFFS_API_TIMEOUT", "30")
        try:
            self.timeout = timeout if timeout is not None else int(timeout_str)
        except ValueError:
            logger.warning(
                f"Invalid YAML_DIFFS_API_TIMEOUT value: {timeout_str}. Using default: 30"
            )
            self.timeout = timeout if timeout is not None else 30

    def __repr__(self) -> str:
        """String representation of configuration."""
        api_key_display = "***" if self.api_key else None
        return (
            f"MCPServerConfig(api_base_url={self.api_base_url!r}, "
            f"api_key={api_key_display!r}, timeout={self.timeout})"
        )
