"""Configuration for API server.

Handles environment variables, CORS settings, and logging configuration.
"""

from __future__ import annotations

import logging
import os


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        """Initialize settings from environment variables."""
        # Server configuration
        self.port = self._get_int("PORT", 8000)
        self.host = os.getenv("HOST", "0.0.0.0")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # CORS configuration
        # Default to empty list (most secure) - require explicit configuration
        cors_origins_env = os.getenv("CORS_ORIGINS", "")
        self.cors_origins: list[str] = (
            [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
            if cors_origins_env
            else []  # Default to no CORS origins (most secure)
        )
        # Warn if CORS is too permissive in production
        if self.cors_origins == ["*"] and os.getenv("ENVIRONMENT") == "production":
            logging.warning(
                "CORS is set to allow all origins (*). This is insecure for production!"
            )
        self.cors_allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        cors_methods_env = os.getenv("CORS_ALLOW_METHODS", "*")
        self.cors_allow_methods: list[str] = (
            [method.strip() for method in cors_methods_env.split(",")]
            if cors_methods_env != "*"
            else ["*"]
        )
        cors_headers_env = os.getenv("CORS_ALLOW_HEADERS", "*")
        self.cors_allow_headers: list[str] = (
            [header.strip() for header in cors_headers_env.split(",")]
            if cors_headers_env != "*"
            else ["*"]
        )

        # Application metadata
        self.app_name = os.getenv("APP_NAME", "yaml-diffs API")
        self.app_version = os.getenv("APP_VERSION", "0.1.0")

    @staticmethod
    def _get_int(key: str, default: int) -> int:
        """Get integer from environment variable.

        Args:
            key: Environment variable name.
            default: Default value if not set or invalid.

        Returns:
            Integer value from environment or default.
        """
        value = os.getenv(key)
        if value:
            try:
                return int(value)
            except ValueError:
                logging.warning(
                    f"Invalid {key} environment variable: {value}. Using default: {default}"
                )
        return default

    @property
    def port_from_env(self) -> int:
        """Get port from PORT environment variable (Railway requirement).

        Railway sets the PORT environment variable, which takes precedence
        over the default port setting.

        Returns:
            Port number from PORT env var, or default port if not set.
        """
        return self.port


def configure_logging(level: str = "INFO") -> None:
    """Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# Global settings instance
settings = Settings()
