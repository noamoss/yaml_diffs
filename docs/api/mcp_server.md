# MCP Server for yaml-diffs

The yaml-diffs MCP (Model Context Protocol) server exposes the REST API endpoints as MCP tools, enabling AI assistants to interact with the yaml-diffs service via the MCP protocol.

## Overview

The MCP server provides three tools that wrap the REST API endpoints:

- **`validate_document`**: Validate a YAML document against the OpenSpec schema and Pydantic models
- **`diff_documents`**: Compare two YAML documents and return detected changes
- **`health_check`**: Check the health status of the yaml-diffs API

## Installation

The MCP server is included with the yaml-diffs package. Install it using:

```bash
pip install yaml-diffs
```

Or install from source:

```bash
git clone https://github.com/noamoss/yaml_diffs.git
cd yaml_diffs
pip install -e .
```

## Configuration

The MCP server can be configured via environment variables or command-line options:

### Environment Variables

- **`YAML_DIFFS_API_URL`**: Base URL for the yaml-diffs API (default: `http://localhost:8000`)
- **`YAML_DIFFS_API_KEY`**: Optional API key for authentication (default: `None`)
- **`YAML_DIFFS_API_TIMEOUT`**: Request timeout in seconds (default: `30`)

### Command-Line Options

When running the server via CLI, you can override configuration:

```bash
yaml-diffs mcp-server --api-url http://api.example.com:8000 --api-key your-key --timeout 60
```

## Running the Server

### Using the CLI Command

The simplest way to run the MCP server is using the CLI command:

```bash
yaml-diffs mcp-server
```

This starts the server with stdio transport (standard MCP protocol).

### Using the Python Module

You can also run the server directly as a Python module:

```bash
python -m yaml_diffs.mcp_server.server
```

### Programmatic Usage

```python
from yaml_diffs.mcp_server.server import run_server
import asyncio

asyncio.run(run_server())
```

## MCP Client Configuration

### Claude Desktop

Add the following to your Claude Desktop configuration file (typically `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "yaml-diffs": {
      "command": "yaml-diffs-mcp-server",
      "args": [],
      "env": {
        "YAML_DIFFS_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

For a remote API instance:

```json
{
  "mcpServers": {
    "yaml-diffs": {
      "command": "yaml-diffs-mcp-server",
      "args": [],
      "env": {
        "YAML_DIFFS_API_URL": "https://api.example.com",
        "YAML_DIFFS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Other MCP Clients

The server uses stdio transport, which is the standard MCP protocol. Any MCP client that supports stdio transport can connect to the server.

## Tool Descriptions

### validate_document

Validates a YAML document against the OpenSpec schema and Pydantic models.

**Input:**
```json
{
  "yaml": "document:\n  id: \"test\"\n  type: \"law\"\n  ..."
}
```

**Output:**
```json
{
  "valid": true,
  "document": {
    "id": "test",
    "type": "law",
    ...
  }
}
```

Or if validation fails:
```json
{
  "valid": false,
  "error": "ValidationError",
  "message": "Validation error message",
  "details": [...]
}
```

### diff_documents

Compares two YAML documents and returns detected changes.

**Input:**
```json
{
  "old_yaml": "document:\n  id: \"test\"\n  ...",
  "new_yaml": "document:\n  id: \"test\"\n  ..."
}
```

**Output:**
```json
{
  "diff": {
    "changes": [
      {
        "change_type": "CONTENT_CHANGED",
        "section_path": "1.2",
        "old_content": "...",
        "new_content": "..."
      }
    ],
    "added_count": 1,
    "deleted_count": 0,
    "modified_count": 1,
    "moved_count": 0
  }
}
```

### health_check

Checks the health status of the yaml-diffs API.

**Input:**
```json
{}
```

**Output:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

## Error Handling

All tools handle errors gracefully and return structured error responses:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message"
}
```

Common error scenarios:

- **Network errors**: When the API is unreachable
- **API errors**: When the API returns an error status
- **Validation errors**: When input validation fails
- **Timeout errors**: When requests exceed the timeout

## Troubleshooting

### Server Won't Start

1. **Check Python version**: The MCP server requires Python 3.10 or higher
2. **Check dependencies**: Ensure all dependencies are installed: `pip install yaml-diffs`
3. **Check API availability**: Ensure the yaml-diffs API is running and accessible

### Connection Issues

1. **Verify API URL**: Check that `YAML_DIFFS_API_URL` points to a running API instance
2. **Check network connectivity**: Ensure the API endpoint is reachable
3. **Verify authentication**: If using API key authentication, ensure the key is correct

### Tool Errors

1. **Check API logs**: Review the API server logs for detailed error information
2. **Validate input**: Ensure YAML content is properly formatted
3. **Check API version**: Ensure the API version matches the MCP server expectations

## Development

### Running Tests

```bash
pytest tests/test_mcp_server.py tests/test_mcp_tools.py -v
```

### Code Structure

- `src/yaml_diffs/mcp_server/config.py`: Configuration management
- `src/yaml_diffs/mcp_server/client.py`: HTTP client for API communication
- `src/yaml_diffs/mcp_server/tools.py`: Tool definitions and handlers
- `src/yaml_diffs/mcp_server/server.py`: Main server implementation

## Related Documentation

- [REST API Documentation](api_server.md)
- [API Reference](../developer/api_reference.md)
- [Main README](../../README.md)
