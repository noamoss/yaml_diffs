"""MCP tool definitions and handlers.

Defines the three MCP tools that wrap the REST API endpoints.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx
import mcp.types as types

from yaml_diffs.mcp_server.client import APIClient

logger = logging.getLogger(__name__)


def get_tool_definitions() -> list[types.Tool]:
    """Get list of MCP tool definitions.

    Returns:
        List of Tool objects defining the available MCP tools.
    """
    return [
        types.Tool(
            name="validate_document",
            description=(
                "Validate a YAML document against the OpenSpec schema and Pydantic models. "
                "Returns validation result with either the validated document or detailed error information."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "yaml": {
                        "type": "string",
                        "description": "YAML document content as string to validate",
                    }
                },
                "required": ["yaml"],
            },
        ),
        types.Tool(
            name="diff_documents",
            description=(
                "Compare two YAML documents and return detected changes. "
                "Returns a DocumentDiff object containing all detected changes including "
                "additions, deletions, modifications, and movements."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "old_yaml": {
                        "type": "string",
                        "description": "Old document version YAML content as string",
                    },
                    "new_yaml": {
                        "type": "string",
                        "description": "New document version YAML content as string",
                    },
                },
                "required": ["old_yaml", "new_yaml"],
            },
        ),
        types.Tool(
            name="health_check",
            description=(
                "Check the health status of the yaml-diffs API. "
                "Returns a simple health status response with version information."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


async def handle_validate_document(
    client: APIClient, arguments: dict[str, Any]
) -> list[types.TextContent]:
    """Handle validate_document tool call.

    Args:
        client: API client instance.
        arguments: Tool arguments containing 'yaml' key.

    Returns:
        List of TextContent objects with validation result.

    Raises:
        ValueError: If required arguments are missing.
    """
    if "yaml" not in arguments:
        raise ValueError("Missing required argument: yaml")

    yaml_content = str(arguments["yaml"])

    try:
        result = await client.validate_document(yaml_content)
        response_text = json.dumps(result, indent=2, ensure_ascii=False)
        return [types.TextContent(type="text", text=response_text)]
    except httpx.HTTPStatusError as e:
        error_message = f"API error validating document: HTTP {e.response.status_code}"
        logger.error(error_message, exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": "HTTPStatusError",
                        "message": error_message,
                        "status_code": e.response.status_code,
                        "valid": False,
                    },
                    indent=2,
                ),
            )
        ]
    except httpx.RequestError as e:
        error_message = f"Network error validating document: {str(e)}"
        logger.error(error_message, exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": "RequestError",
                        "message": error_message,
                        "valid": False,
                    },
                    indent=2,
                ),
            )
        ]
    except Exception as e:
        error_message = f"Error validating document: {str(e)}"
        logger.error(error_message, exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": type(e).__name__,
                        "message": error_message,
                        "valid": False,
                    },
                    indent=2,
                ),
            )
        ]


async def handle_diff_documents(
    client: APIClient, arguments: dict[str, Any]
) -> list[types.TextContent]:
    """Handle diff_documents tool call.

    Args:
        client: API client instance.
        arguments: Tool arguments containing 'old_yaml' and 'new_yaml' keys.

    Returns:
        List of TextContent objects with diff result.

    Raises:
        ValueError: If required arguments are missing.
    """
    if "old_yaml" not in arguments:
        raise ValueError("Missing required argument: old_yaml")
    if "new_yaml" not in arguments:
        raise ValueError("Missing required argument: new_yaml")

    old_yaml = str(arguments["old_yaml"])
    new_yaml = str(arguments["new_yaml"])

    try:
        result = await client.diff_documents(old_yaml, new_yaml)
        response_text = json.dumps(result, indent=2, ensure_ascii=False)
        return [types.TextContent(type="text", text=response_text)]
    except httpx.HTTPStatusError as e:
        error_message = f"API error diffing documents: HTTP {e.response.status_code}"
        logger.error(error_message, exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": "HTTPStatusError",
                        "message": error_message,
                        "status_code": e.response.status_code,
                    },
                    indent=2,
                ),
            )
        ]
    except httpx.RequestError as e:
        error_message = f"Network error diffing documents: {str(e)}"
        logger.error(error_message, exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": "RequestError",
                        "message": error_message,
                    },
                    indent=2,
                ),
            )
        ]
    except Exception as e:
        error_message = f"Error diffing documents: {str(e)}"
        logger.error(error_message, exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": type(e).__name__,
                        "message": error_message,
                    },
                    indent=2,
                ),
            )
        ]


async def handle_health_check(
    client: APIClient, arguments: dict[str, Any]
) -> list[types.TextContent]:
    """Handle health_check tool call.

    Args:
        client: API client instance.
        arguments: Tool arguments (ignored for health check).

    Returns:
        List of TextContent objects with health status.
    """
    try:
        result = await client.health_check()
        response_text = json.dumps(result, indent=2, ensure_ascii=False)
        return [types.TextContent(type="text", text=response_text)]
    except httpx.HTTPStatusError as e:
        error_message = f"API error checking health: HTTP {e.response.status_code}"
        logger.error(error_message, exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": "HTTPStatusError",
                        "message": error_message,
                        "status_code": e.response.status_code,
                        "status": "unhealthy",
                    },
                    indent=2,
                ),
            )
        ]
    except httpx.RequestError as e:
        error_message = f"Network error checking health: {str(e)}"
        logger.error(error_message, exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": "RequestError",
                        "message": error_message,
                        "status": "unhealthy",
                    },
                    indent=2,
                ),
            )
        ]
    except Exception as e:
        error_message = f"Error checking health: {str(e)}"
        logger.error(error_message, exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": type(e).__name__,
                        "message": error_message,
                        "status": "unhealthy",
                    },
                    indent=2,
                ),
            )
        ]


async def call_tool(
    client: APIClient, name: str, arguments: dict[str, Any]
) -> list[types.TextContent]:
    """Call the appropriate tool handler based on tool name.

    Args:
        client: API client instance.
        name: Tool name.
        arguments: Tool arguments.

    Returns:
        List of TextContent objects with tool result.

    Raises:
        ValueError: If tool name is unknown.
    """
    if name == "validate_document":
        return await handle_validate_document(client, arguments)
    elif name == "diff_documents":
        return await handle_diff_documents(client, arguments)
    elif name == "health_check":
        return await handle_health_check(client, arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")
