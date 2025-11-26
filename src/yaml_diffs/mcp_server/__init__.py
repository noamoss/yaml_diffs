"""MCP server for yaml-diffs API endpoints.

This package provides an MCP (Model Context Protocol) server that exposes
the REST API endpoints as MCP tools, enabling AI assistants to interact
with the yaml-diffs service via the MCP protocol.
"""

from yaml_diffs.mcp_server.config import MCPServerConfig
from yaml_diffs.mcp_server.server import run_server

__all__ = ["MCPServerConfig", "run_server"]

