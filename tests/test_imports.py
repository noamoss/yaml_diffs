"""Tests to verify package can be imported and Python version compatibility."""

import sys


def test_python_version():
    """Verify Python version is 3.9 or higher."""
    assert sys.version_info >= (3, 9), f"Python 3.9+ required, got {sys.version_info}"


def test_package_import():
    """Verify the package can be imported."""
    import yaml_diffs

    assert yaml_diffs is not None


def test_package_version():
    """Verify package version is accessible."""
    from yaml_diffs import __version__

    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_dependencies_importable():
    """Verify key dependencies can be imported."""
    import fastapi
    import pydantic
    import yaml

    # Just verify they're importable, don't need to use them
    assert pydantic is not None
    assert yaml is not None
    assert fastapi is not None
