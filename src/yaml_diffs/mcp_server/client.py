"""HTTP client for communicating with yaml-diffs API.

Provides a simple interface for calling the REST API endpoints.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from yaml_diffs.mcp_server.config import MCPServerConfig

logger = logging.getLogger(__name__)


class APIClient:
    """HTTP client for yaml-diffs API.

    Handles HTTP communication with the REST API, including error handling
    and optional authentication.

    Attributes:
        config: MCP server configuration.
    """

    def __init__(self, config: MCPServerConfig) -> None:
        """Initialize API client with configuration.

        Args:
            config: MCP server configuration.
        """
        self.config = config
        # Convert timeout=0 to None (no timeout) as httpx expects timeout > 0 or None
        timeout_value = None if config.timeout == 0 else config.timeout
        self._client = httpx.AsyncClient(
            base_url=config.api_base_url,
            timeout=timeout_value,
            headers=self._get_headers(),
        )

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers including optional authentication.

        Returns:
            Dictionary of HTTP headers.
        """
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    async def validate_document(self, yaml: str) -> dict[str, Any]:
        """Validate a YAML document.

        Args:
            yaml: YAML content as string.

        Returns:
            Dictionary containing validation result.

        Raises:
            httpx.HTTPStatusError: If API request fails.
            httpx.RequestError: If network error occurs.
        """
        try:
            response = await self._client.post(
                "/api/v1/validate",
                json={"yaml": yaml},
            )
            response.raise_for_status()
            result: dict[str, Any] = response.json()
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"API error validating document: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Network error validating document: {e}")
            raise

    async def diff_documents(self, old_yaml: str, new_yaml: str) -> dict[str, Any]:
        """Diff two YAML documents.

        Args:
            old_yaml: Old document version YAML content as string.
            new_yaml: New document version YAML content as string.

        Returns:
            Dictionary containing diff result.

        Raises:
            httpx.HTTPStatusError: If API request fails.
            httpx.RequestError: If network error occurs.
        """
        try:
            response = await self._client.post(
                "/api/v1/diff",
                json={"old_yaml": old_yaml, "new_yaml": new_yaml},
            )
            response.raise_for_status()
            result: dict[str, Any] = response.json()
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"API error diffing documents: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Network error diffing documents: {e}")
            raise

    async def health_check(self) -> dict[str, Any]:
        """Check API health status.

        Returns:
            Dictionary containing health status.

        Raises:
            httpx.HTTPStatusError: If API request fails.
            httpx.RequestError: If network error occurs.
        """
        try:
            response = await self._client.get("/health")
            response.raise_for_status()
            result: dict[str, Any] = response.json()
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"API error checking health: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Network error checking health: {e}")
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> APIClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def __enter__(self) -> APIClient:
        """Synchronous context manager entry (for backward compatibility)."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Synchronous context manager exit (for backward compatibility).

        Note: This will raise RuntimeError if used in async context.
        Use async context manager (async with) instead.
        """
        # Note: This is not ideal for async client, but kept for backward compatibility
        # In practice, the async context manager should be used
        import asyncio

        # Check if there's a running event loop first
        try:
            asyncio.get_running_loop()
            # If we get here, there's a running loop - raise error
            raise RuntimeError(
                "Cannot use synchronous context manager with async client in running event loop. "
                "Use 'async with' instead."
            )
        except RuntimeError as e:
            # If get_running_loop() raised RuntimeError, it means no running loop exists
            # Check if this is our intentional error (contains "Cannot use synchronous context manager")
            # vs the asyncio error (which is "no running event loop")
            if "Cannot use synchronous context manager" in str(e):
                # This is our intentional error - re-raise it
                raise
            # Otherwise, it's the "no running event loop" error from asyncio - continue

        # No running loop - try to get/create event loop and run
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                # Loop is closed, create a new one
                asyncio.run(self.close())
            else:
                loop.run_until_complete(self.close())
        except RuntimeError:
            # No event loop exists at all, create one
            asyncio.run(self.close())
