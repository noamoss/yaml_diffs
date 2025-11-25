"""Main MCP server implementation.

Creates and runs the MCP server with tool registration and lifecycle management.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, cast

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from yaml_diffs.__version__ import __version__
from yaml_diffs.mcp_server.client import APIClient
from yaml_diffs.mcp_server.config import MCPServerConfig
from yaml_diffs.mcp_server.tools import call_tool, get_tool_definitions

logger = logging.getLogger(__name__)

# Global API client (initialized in lifespan)
# Note: This global variable is necessary for the MCP server pattern where tool handlers
# need access to the client. The MCP SDK's handler decorators don't support dependency
# injection, so we use a global variable. This is thread-safe for stdio transport
# (single-threaded), but if the server ever supports concurrent requests, this would
# need to be reconsidered.
api_client: APIClient | None = None


@asynccontextmanager
async def server_lifespan(
    config: MCPServerConfig | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Server lifespan context manager.

    Initializes resources on startup and cleans up on shutdown.

    Args:
        config: Optional MCP server configuration. If None, loads from environment variables.

    Yields:
        Dictionary with lifespan context (currently empty, but available for future use).
    """
    global api_client

    # Startup: Initialize API client
    if config is None:
        config = MCPServerConfig()
    logger.info(f"Initializing MCP server with config: {config}")
    api_client = APIClient(config)
    logger.info("MCP server initialized successfully")

    try:
        yield {"api_client": api_client}
    finally:
        # Shutdown: Clean up resources
        if api_client is not None:
            await api_client.close()
            api_client = None
        logger.info("MCP server shutdown complete")


def _create_server(config: MCPServerConfig | None = None) -> Server:
    """Create and configure the MCP server instance.

    Args:
        config: Optional MCP server configuration. If None, loads from environment variables.

    Returns:
        Configured Server instance.
    """

    # Create server instance with lifespan that uses the provided config
    # Note: The MCP SDK expects lifespan callables to accept a Server parameter,
    # even if we don't use it (we capture config from the closure)
    # The @asynccontextmanager decorator returns an AbstractAsyncContextManager,
    # but mypy can't infer this, so we use cast to satisfy type checking
    def lifespan_wrapper(_server: Server) -> Any:
        return cast(Any, server_lifespan(config))

    server = Server("yaml-diffs-mcp-server", lifespan=lifespan_wrapper)

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available MCP tools.

        Returns:
            List of Tool objects defining available tools.
        """
        return get_tool_definitions()

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        """Handle tool call requests.

        Args:
            name: Tool name.
            arguments: Tool arguments.

        Returns:
            List of TextContent objects with tool result.

        Raises:
            ValueError: If tool name is unknown or API client is not initialized.
        """
        if api_client is None:
            raise ValueError("API client not initialized")

        return await call_tool(api_client, name, arguments)

    return server


async def run_server(config: MCPServerConfig | None = None) -> None:
    """Run the MCP server with stdio transport.

    This is the main entry point for the MCP server. It sets up the server
    with stdio transport (standard MCP protocol) and runs the server loop.

    Args:
        config: Optional MCP server configuration. If None, loads from environment variables.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info(f"Starting yaml-diffs MCP server v{__version__}")

    # Create server instance
    server = _create_server(config)

    # Run server with stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="yaml-diffs-mcp-server",
                server_version=__version__,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main(config: MCPServerConfig | None = None) -> None:
    """Main entry point for running the MCP server.

    Args:
        config: Optional MCP server configuration. If None, loads from environment variables.
    """
    try:
        asyncio.run(run_server(config))
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        raise  # Re-raise to exit with code 130 (standard for SIGINT)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
