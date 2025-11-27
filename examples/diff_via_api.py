#!/usr/bin/env python3
"""Example script to diff two YAML documents using the API."""

import sys
from pathlib import Path

import httpx


def diff_documents(api_url: str, old_yaml_path: str, new_yaml_path: str):
    """Diff two YAML documents using the API.

    Args:
        api_url: Base URL of the API (e.g., https://yamldiffs-production.up.railway.app)
        old_yaml_path: Path to the old version YAML file
        new_yaml_path: Path to the new version YAML file
    """
    # Read YAML files
    old_yaml = Path(old_yaml_path).read_text(encoding="utf-8")
    new_yaml = Path(new_yaml_path).read_text(encoding="utf-8")

    # Make API request
    try:
        response = httpx.post(
            f"{api_url}/api/v1/diff",
            json={"old_yaml": old_yaml, "new_yaml": new_yaml},
            timeout=30.0,
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
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <API_URL> <OLD_YAML> <NEW_YAML>")
        print(
            f"Example: {sys.argv[0]} https://yamldiffs-production.up.railway.app examples/document_v1.yaml examples/document_v2.yaml"
        )
        sys.exit(1)

    api_url = sys.argv[1]
    old_yaml = sys.argv[2]
    new_yaml = sys.argv[3]

    diff_documents(api_url, old_yaml, new_yaml)
