"""Shared utilities for CLI commands."""

from __future__ import annotations

import sys

import click

from yaml_diffs.exceptions import (
    OpenSpecValidationError,
    PydanticValidationError,
    ValidationError,
    YAMLLoadError,
)


def handle_cli_error(error: Exception, file_path: str | None = None) -> None:
    """Handle CLI errors with user-friendly messages.

    Args:
        error: The exception that occurred.
        file_path: Optional file path that caused the error.
    """
    file_info = f" ({file_path})" if file_path else ""

    if isinstance(error, YAMLLoadError):
        click.echo(f"Error: Failed to load YAML file{file_info}", err=True)
        if error.message:
            click.echo(f"  {error.message}", err=True)
        if error.original_error:
            click.echo(f"  Details: {error.original_error}", err=True)
        sys.exit(1)

    elif isinstance(error, OpenSpecValidationError):
        click.echo(f"Error: Document validation failed{file_info}", err=True)
        if error.message:
            click.echo(f"  {error.message}", err=True)
        if error.errors:
            click.echo("  Validation errors:", err=True)
            for err in error.errors[:5]:  # Show first 5 errors
                click.echo(f"    - {err}", err=True)
            if len(error.errors) > 5:
                click.echo(f"    ... and {len(error.errors) - 5} more errors", err=True)
        sys.exit(1)

    elif isinstance(error, PydanticValidationError):
        click.echo(f"Error: Document structure validation failed{file_info}", err=True)
        if error.message:
            click.echo(f"  {error.message}", err=True)
        if error.errors:
            click.echo("  Validation errors:", err=True)
            for err in error.errors[:5]:  # Show first 5 errors
                click.echo(f"    - {err}", err=True)
            if len(error.errors) > 5:
                click.echo(f"    ... and {len(error.errors) - 5} more errors", err=True)
        sys.exit(1)

    elif isinstance(error, ValidationError):
        click.echo(f"Error: Validation failed{file_info}", err=True)
        if error.message:
            click.echo(f"  {error.message}", err=True)
        sys.exit(1)

    elif isinstance(error, FileNotFoundError):
        click.echo(f"Error: File not found{file_info}", err=True)
        click.echo(f"  {error}", err=True)
        sys.exit(1)

    elif isinstance(error, ValueError):
        click.echo(f"Error: Invalid value{file_info}", err=True)
        click.echo(f"  {error}", err=True)
        sys.exit(1)

    else:
        click.echo(f"Error: Unexpected error occurred{file_info}", err=True)
        click.echo(f"  {type(error).__name__}: {error}", err=True)
        sys.exit(1)

