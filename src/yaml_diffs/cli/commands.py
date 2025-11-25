"""CLI commands for yaml-diffs.

This module implements the validate, diff, and mcp-server commands.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click

from yaml_diffs import ChangeType
from yaml_diffs.api import diff_and_format, validate_document
from yaml_diffs.cli.utils import handle_cli_error
from yaml_diffs.exceptions import (
    OpenSpecValidationError,
    PydanticValidationError,
    ValidationError,
    YAMLLoadError,
)


def _show_progress(message: str, file_path: str | Path) -> None:
    """Show progress message if output is a TTY.

    Displays a progress message to stderr when processing large files (>1MB).
    The message only appears when stderr is connected to a terminal (TTY),
    preventing progress indicators from appearing in piped output or log files.

    Args:
        message: Progress message to display (e.g., "Loading", "Validating").
        file_path: Path to the file being processed. Used to determine file size.

    Note:
        Progress messages are written to stderr to avoid interfering with
        actual command output written to stdout.
    """
    if sys.stderr.isatty():  # Check stderr since we write to stderr
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        size_mb = file_size / (1024 * 1024)
        if size_mb > 1.0:
            click.echo(f"{message} ({size_mb:.1f} MB)...", err=True)


@click.command(name="validate")
@click.argument("file", type=click.Path(exists=True, readable=True, path_type=Path))
def validate_command(file: Path) -> None:
    """Validate a YAML document against the legal document schema.

    This command validates a YAML file against both the OpenSpec schema
    and Pydantic models. It will report any validation errors found.

    Examples:

        \b
        # Validate a document
        yaml-diffs validate document.yaml

        \b
        # Validate with progress indicator (for large files)
        yaml-diffs validate large-document.yaml
    """
    try:
        _show_progress("Loading", file)
        doc = validate_document(file)

        # If we get here, validation succeeded
        click.echo(f"✓ Document '{file}' is valid")
        click.echo(f"  Document ID: {doc.id}")
        if doc.title:
            click.echo(f"  Title: {doc.title}")
        click.echo(f"  Type: {doc.type}")
        click.echo(f"  Sections: {len(doc.sections)}")

    except (YAMLLoadError, ValidationError, OpenSpecValidationError, PydanticValidationError) as e:
        handle_cli_error(e, file_path=str(file))
    except Exception as e:
        handle_cli_error(e, file_path=str(file))


@click.command(name="diff")
@click.argument("old_file", type=click.Path(exists=True, readable=True, path_type=Path))
@click.argument("new_file", type=click.Path(exists=True, readable=True, path_type=Path))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "text", "yaml"], case_sensitive=False),
    default="json",
    help="Output format (default: json)",
)
@click.option(
    "--output",
    "output_file",
    type=click.Path(path_type=Path, writable=True),
    default=None,
    help="Save output to file instead of stdout",
)
@click.option(
    "--filter-change-types",
    "filter_change_types",
    multiple=True,
    type=str,  # Accept any string, validate in code to provide better error messages
    help="Filter results by change type (can be used multiple times). "
    "Valid types: SECTION_ADDED, SECTION_REMOVED, CONTENT_CHANGED, "
    "TITLE_CHANGED, SECTION_MOVED, UNCHANGED",
)
@click.option(
    "--filter-section-path",
    "filter_section_path",
    type=str,
    default=None,
    help="Filter results by section marker path (exact match)",
)
def diff_command(
    old_file: Path,
    new_file: Path,
    output_format: str,
    output_file: Path | None,
    filter_change_types: tuple[str, ...],
    filter_section_path: str | None,
) -> None:
    """Diff two YAML document versions and show the differences.

    This command compares two YAML documents and shows the differences
    between them. The output can be formatted as JSON, text, or YAML.

    Examples:

        \b
        # Basic diff with JSON output
        yaml-diffs diff old.yaml new.yaml

        \b
        # Diff with text format
        yaml-diffs diff old.yaml new.yaml --format text

        \b
        # Save diff to file
        yaml-diffs diff old.yaml new.yaml --output diff.json

        \b
        # Filter by change type
        yaml-diffs diff old.yaml new.yaml --filter-change-types CONTENT_CHANGED

        \b
        # Filter by section path
        yaml-diffs diff old.yaml new.yaml --filter-section-path "1.2.3"
    """
    try:
        # Convert filter_change_types to ChangeType enum if provided
        change_type_filters: list[ChangeType] | None = None
        if filter_change_types:
            change_type_filters = []
            invalid_types = []
            for ct_str in filter_change_types:
                try:
                    change_type_filters.append(ChangeType[ct_str.upper()])
                except KeyError:
                    invalid_types.append(ct_str)
                    click.echo(f"Warning: Unknown change type '{ct_str}', ignoring", err=True)

            # If all filter types were invalid, raise an error instead of showing empty results
            if not change_type_filters and invalid_types:
                handle_cli_error(
                    ValueError(
                        f"All provided change type filters were invalid: {', '.join(invalid_types)}. "
                        f"Valid types are: {', '.join([ct.name for ct in ChangeType])}"
                    )
                )

        _show_progress("Loading old document", old_file)
        _show_progress("Loading new document", new_file)

        # Perform the diff
        formatted_output = diff_and_format(
            old_file,
            new_file,
            output_format=output_format.lower(),
            filter_change_types=change_type_filters,
            filter_section_path=filter_section_path,
        )

        # Write output
        if output_file:
            try:
                # Ensure parent directory exists
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(formatted_output, encoding="utf-8")
                click.echo(f"✓ Diff saved to '{output_file}'")
            except PermissionError:
                handle_cli_error(
                    PermissionError(f"Cannot write to '{output_file}': permission denied")
                )
            except OSError as e:
                handle_cli_error(OSError(f"Cannot write to '{output_file}': {e}"))
        else:
            click.echo(formatted_output)

    except (YAMLLoadError, ValidationError, OpenSpecValidationError, PydanticValidationError) as e:
        # Determine which file caused the error (if possible)
        file_path = None
        if isinstance(e, YAMLLoadError) and e.file_path:
            file_path = e.file_path
        elif hasattr(e, "file_path"):  # Check if other exceptions have file_path
            file_path = e.file_path
        handle_cli_error(e, file_path=file_path)
    except ValueError as e:
        # Handle format errors, etc.
        handle_cli_error(e)
    except Exception as e:
        handle_cli_error(e)


@click.command(name="mcp-server")
@click.option(
    "--api-url",
    "api_url",
    type=str,
    default=None,
    help="Override API base URL (default: http://localhost:8000 or YAML_DIFFS_API_URL env var)",
)
@click.option(
    "--api-key",
    "api_key",
    type=str,
    default=None,
    help="Override API key for authentication (default: YAML_DIFFS_API_KEY env var)",
)
@click.option(
    "--timeout",
    "timeout",
    type=int,
    default=None,
    help="Override request timeout in seconds (default: 30 or YAML_DIFFS_API_TIMEOUT env var)",
)
def mcp_server_command(api_url: str | None, api_key: str | None, timeout: int | None) -> None:
    """Run the MCP (Model Context Protocol) server for yaml-diffs API.

    This command starts an MCP server that exposes the REST API endpoints
    as MCP tools, enabling AI assistants to interact with the yaml-diffs
    service via the MCP protocol.

    The server uses stdio transport (standard MCP protocol) and provides
    three tools:
    - validate_document: Validate a YAML document
    - diff_documents: Diff two YAML documents
    - health_check: Check API health status

    Configuration can be provided via command-line options or environment
    variables:
    - YAML_DIFFS_API_URL: API base URL (default: http://localhost:8000)
    - YAML_DIFFS_API_KEY: Optional API key for authentication
    - YAML_DIFFS_API_TIMEOUT: Request timeout in seconds (default: 30)

    Examples:

        \b
        # Run with default settings (local API)
        yaml-diffs mcp-server

        \b
        # Run with custom API URL
        yaml-diffs mcp-server --api-url http://api.example.com:8000

        \b
        # Run with API key authentication
        yaml-diffs mcp-server --api-key your-api-key-here
    """
    try:
        # Create configuration from CLI arguments
        from yaml_diffs.mcp_server.config import MCPServerConfig
        from yaml_diffs.mcp_server.server import main

        config = MCPServerConfig(
            api_base_url=api_url,
            api_key=api_key,
            timeout=timeout,
        )

        # Run the server with the configuration
        main(config)
    except Exception as e:
        handle_cli_error(e)
