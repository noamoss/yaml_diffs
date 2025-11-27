#!/usr/bin/env python3
"""Example script to diff two YAML documents using the API."""

import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


def diff_documents(api_url: str, old_yaml_path: str, new_yaml_path: str):
    """Diff two YAML documents using the API.

    Args:
        api_url: Base URL of the API (e.g., https://yaml-diffs.up.railway.app)
        old_yaml_path: Path to the old version YAML file
        new_yaml_path: Path to the new version YAML file
    """
    # Read YAML files
    try:
        old_yaml = Path(old_yaml_path).read_text(encoding="utf-8")
        new_yaml = Path(new_yaml_path).read_text(encoding="utf-8")
    except FileNotFoundError as e:
        print(f"❌ File not found: {e.filename}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"❌ Encoding error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Make API request
    # Get timeout from environment variable or use default
    timeout = float(os.getenv("YAML_DIFFS_API_TIMEOUT", "30.0"))
    try:
        response = httpx.post(
            f"{api_url}/api/v1/diff",
            json={"old_yaml": old_yaml, "new_yaml": new_yaml},
            timeout=timeout,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"❌ Error {e.response.status_code}: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"❌ Network error: {e}", file=sys.stderr)
        sys.exit(1)

    result = response.json()
    diff = result["diff"]

    # Print summary
    print("=" * 60)
    print("📊 DIFF SUMMARY")
    print("=" * 60)
    print(f"Added sections:    {diff['added_count']}")
    print(f"Deleted sections:  {diff['deleted_count']}")
    print(f"Modified sections: {diff['modified_count']}")
    print(f"Moved sections:    {diff['moved_count']}")
    print(f"Total changes:     {len(diff['changes'])}")
    print("=" * 60)

    # Print detailed changes
    for i, change in enumerate(diff["changes"], 1):
        print(f"\n{i}. {change['change_type'].upper().replace('_', ' ')}")
        print(f"   Marker: {change['marker']}")
        print(f"   Section ID: {change['section_id']}")

        if change.get("old_marker_path") != change.get("new_marker_path"):
            print(f"   Path: {change.get('old_marker_path')} → {change.get('new_marker_path')}")

        if change.get("old_title") != change.get("new_title"):
            print(f"   Title: '{change.get('old_title')}' → '{change.get('new_title')}'")

        if change.get("old_content") != change.get("new_content"):
            if change.get("old_content"):
                print(f"   Old content: {change['old_content'][:100]}...")
            if change.get("new_content"):
                print(f"   New content: {change['new_content'][:100]}...")

    return result


if __name__ == "__main__":
    # Get API URL from command-line argument, environment variable, or default
    if len(sys.argv) == 4:
        # Command-line argument takes precedence
        api_url = sys.argv[1]
        old_yaml = sys.argv[2]
        new_yaml = sys.argv[3]
    elif len(sys.argv) == 3:
        # Use API URL from environment variable or default
        api_url = os.getenv("YAML_DIFFS_API_URL", "http://localhost:8000")
        old_yaml = sys.argv[1]
        new_yaml = sys.argv[2]
    else:
        print(f"Usage: {sys.argv[0]} [API_URL] <OLD_YAML> <NEW_YAML>")
        print("")
        print("Arguments:")
        print("  API_URL    Optional. Base URL of the API.")
        print("             If not provided, uses YAML_DIFFS_API_URL from .env file")
        print("             or environment variable (default: http://localhost:8000)")
        print("  OLD_YAML   Path to the old version YAML file")
        print("  NEW_YAML   Path to the new version YAML file")
        print("")
        print("Examples:")
        print(f"  {sys.argv[0]} examples/document_v1.yaml examples/document_v2.yaml")
        print("    (uses YAML_DIFFS_API_URL from .env or environment)")
        print(
            f"  {sys.argv[0]} https://yaml-diffs.up.railway.app examples/document_v1.yaml examples/document_v2.yaml"
        )
        print("    (uses provided API URL)")
        print("")
        print("Environment Variables:")
        print("  YAML_DIFFS_API_URL      Base URL of the API (default: http://localhost:8000)")
        print("  YAML_DIFFS_API_TIMEOUT  Request timeout in seconds (default: 30.0)")
        print("")
        print("Note: Create a .env file from .env.example to configure the API URL.")
        sys.exit(1)

    diff_documents(api_url, old_yaml, new_yaml)
