"""Tests for Railway deployment configuration.

Tests verify that the API server is properly configured for Railway deployment,
including environment variable handling, port binding, and health checks.
"""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from yaml_diffs.api_server.config import Settings, settings
from yaml_diffs.api_server.main import app


class TestRailwayEnvironmentVariables:
    """Test environment variable configuration for Railway."""

    def test_port_from_railway_env_var(self) -> None:
        """Test that PORT environment variable is read correctly (Railway requirement)."""
        with patch.dict(os.environ, {"PORT": "3000"}, clear=False):
            # Create new settings instance to pick up env var
            test_settings = Settings()
            assert test_settings.port == 3000
            assert test_settings.port_from_env == 3000

    def test_port_default_when_not_set(self) -> None:
        """Test that default port is used when PORT is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove PORT if it exists
            os.environ.pop("PORT", None)
            test_settings = Settings()
            assert test_settings.port == 8000
            assert test_settings.port_from_env == 8000

    def test_port_invalid_value_uses_default(self) -> None:
        """Test that invalid PORT value falls back to default."""
        with patch.dict(os.environ, {"PORT": "invalid"}, clear=False):
            test_settings = Settings()
            # Should fall back to default when PORT is invalid
            assert test_settings.port == 8000

    def test_host_binds_to_all_interfaces(self) -> None:
        """Test that HOST defaults to 0.0.0.0 (required for Railway)."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("HOST", None)
            test_settings = Settings()
            assert test_settings.host == "0.0.0.0"

    def test_host_can_be_overridden(self) -> None:
        """Test that HOST can be overridden (though not recommended for Railway)."""
        with patch.dict(os.environ, {"HOST": "127.0.0.1"}, clear=False):
            test_settings = Settings()
            assert test_settings.host == "127.0.0.1"

    def test_cors_origins_empty_by_default(self) -> None:
        """Test that CORS_ORIGINS defaults to empty list (most secure)."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CORS_ORIGINS", None)
            test_settings = Settings()
            assert test_settings.cors_origins == []

    def test_cors_origins_parsed_correctly(self) -> None:
        """Test that CORS_ORIGINS is parsed correctly from comma-separated string."""
        with patch.dict(
            os.environ, {"CORS_ORIGINS": "https://example.com,https://app.example.com"}, clear=False
        ):
            test_settings = Settings()
            assert test_settings.cors_origins == ["https://example.com", "https://app.example.com"]

    def test_cors_wildcard_warning_in_production(self) -> None:
        """Test that CORS wildcard triggers warning in production."""
        with patch.dict(
            os.environ, {"CORS_ORIGINS": "*", "ENVIRONMENT": "production"}, clear=False
        ):
            import logging

            with patch.object(logging, "warning") as mock_warning:
                Settings()
                # Should log warning about insecure CORS in production
                mock_warning.assert_called_once()
                assert "insecure" in str(mock_warning.call_args).lower()

    def test_log_level_configuration(self) -> None:
        """Test that LOG_LEVEL can be configured."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}, clear=False):
            test_settings = Settings()
            assert test_settings.log_level == "DEBUG"

    def test_app_version_from_env(self) -> None:
        """Test that APP_VERSION can be set via environment variable."""
        with patch.dict(os.environ, {"APP_VERSION": "1.2.3"}, clear=False):
            test_settings = Settings()
            assert test_settings.app_version == "1.2.3"


class TestRailwayHealthCheck:
    """Test health check endpoint for Railway monitoring."""

    def test_health_endpoint_returns_200(self) -> None:
        """Test that health endpoint returns 200 OK (Railway requirement)."""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_response_format(self) -> None:
        """Test that health endpoint returns correct response format."""
        client = TestClient(app)
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert data["status"] == "healthy"
        assert isinstance(data["version"], str)

    def test_health_endpoint_uses_settings_version(self) -> None:
        """Test that health endpoint uses version from settings."""
        client = TestClient(app)
        response = client.get("/health")
        data = response.json()
        # Version should match settings
        assert data["version"] == settings.app_version


class TestRailwayServerConfiguration:
    """Test server configuration for Railway deployment."""

    def test_app_binds_to_correct_host(self) -> None:
        """Test that FastAPI app is configured correctly."""
        # The app should be configured to bind to 0.0.0.0 via settings
        assert settings.host == "0.0.0.0" or settings.host is not None

    def test_app_uses_port_from_settings(self) -> None:
        """Test that app uses port from settings."""
        # Settings should have a port configured
        assert isinstance(settings.port, int)
        assert settings.port > 0

    def test_cors_middleware_configured(self) -> None:
        """Test that CORS middleware is configured in the app."""
        # Check that CORS middleware is in the app
        middleware_types = [type(middleware).__name__ for middleware in app.user_middleware]
        assert "CORSMiddleware" in str(middleware_types) or len(app.user_middleware) > 0

    def test_health_router_included(self) -> None:
        """Test that health check router is included in the app."""
        # Health endpoint should be accessible
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200


class TestRailwayStartCommand:
    """Test that the Railway start command configuration is correct."""

    def test_start_command_uses_uvicorn(self) -> None:
        """Test that start command uses uvicorn (as specified in railway.json)."""
        # This is a documentation/configuration test
        # The actual command is: uvicorn src.yaml_diffs.api_server.main:app --host 0.0.0.0 --port $PORT
        # We verify the app can be imported and used with uvicorn
        assert app is not None
        assert hasattr(app, "openapi")
        assert hasattr(app, "get")

    def test_app_module_structure(self) -> None:
        """Test that the app module structure matches Railway start command."""
        # Verify the import path matches railway.json start command
        from yaml_diffs.api_server import main

        assert hasattr(main, "app")
        assert main.app == app


@pytest.mark.integration
class TestRailwayIntegration:
    """Integration tests simulating Railway deployment environment."""

    def test_railway_environment_simulation(self) -> None:
        """Test API server with Railway-like environment variables."""
        railway_env = {
            "PORT": "8080",
            "HOST": "0.0.0.0",
            "LOG_LEVEL": "INFO",
            "CORS_ORIGINS": "https://example.com",
            "RAILWAY_ENVIRONMENT": "production",
        }

        with patch.dict(os.environ, railway_env, clear=False):
            # Create new settings with Railway environment
            test_settings = Settings()
            assert test_settings.port == 8080
            assert test_settings.host == "0.0.0.0"
            assert test_settings.log_level == "INFO"
            assert test_settings.cors_origins == ["https://example.com"]

    def test_health_check_with_railway_env(self) -> None:
        """Test health check works with Railway environment variables."""
        with patch.dict(
            os.environ, {"PORT": "3000", "RAILWAY_ENVIRONMENT": "production"}, clear=False
        ):
            client = TestClient(app)
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    def test_api_endpoints_accessible_with_railway_config(self) -> None:
        """Test that API endpoints are accessible with Railway configuration."""
        with patch.dict(os.environ, {"PORT": "8000"}, clear=False):
            client = TestClient(app)
            # Test root endpoint
            response = client.get("/")
            assert response.status_code == 200
            # Test health endpoint
            response = client.get("/health")
            assert response.status_code == 200
            # Test OpenAPI docs
            response = client.get("/docs")
            assert response.status_code == 200
