"""Main CLI entry point for yaml-diffs.

This module provides the main command-line interface using Click.
"""

from __future__ import annotations

import click

from yaml_diffs import __version__
from yaml_diffs.cli import commands
from yaml_diffs.cli.utils import handle_cli_error


@click.group()
@click.version_option(version=__version__, prog_name="yaml-diffs")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """yaml-diffs: Command-line tool for validating and diffing YAML documents.

    This tool provides commands for:
    - Validating YAML documents against the legal document schema
    - Diffing two versions of YAML documents to detect changes

    For more information, see: https://github.com/noamoss/yaml_diffs
    """
    # Ensure context object exists
    ctx.ensure_object(dict)


# Register commands
cli.add_command(commands.validate_command)
cli.add_command(commands.diff_command)


def main() -> None:
    """Main entry point for the CLI.

    This function is called by the console_scripts entry point.
    It wraps the CLI in error handling to provide consistent error messages.
    """
    try:
        cli()
    except Exception as e:
        handle_cli_error(e)


if __name__ == "__main__":
    main()
