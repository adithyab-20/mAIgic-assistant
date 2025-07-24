"""
Gmail configuration management.

This module handles Gmail API configuration including OAuth2 credentials
and connection settings for the simplified AI-focused interface.
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..email_api.exceptions import EmailConfigurationError


@dataclass
class GmailConfig:
    """Gmail API configuration for AI assistant."""

    # File paths for credentials
    credentials_path: str = "credentials.json"
    token_path: str = "token.json"

    # API settings
    scopes: Optional[List[str]] = None

    # Connection settings
    timeout_seconds: int = 30
    max_retries: int = 3

    def __post_init__(self) -> None:
        """Set default scopes if not provided."""
        if self.scopes is None:
            self.scopes = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify',
                'https://www.googleapis.com/auth/gmail.labels'
            ]

    def validate(self) -> None:
        """Validate configuration parameters."""
        if not os.path.exists(self.credentials_path):
            raise EmailConfigurationError(f"Gmail credentials file not found: {self.credentials_path}")

        if self.timeout_seconds <= 0:
            raise EmailConfigurationError("timeout_seconds must be positive")

        if self.max_retries < 0:
            raise EmailConfigurationError("max_retries must be non-negative")

    @classmethod
    def from_env(cls, env_prefix: str = "GMAIL_") -> "GmailConfig":
        """
        Create Gmail configuration from environment variables.

        Expected environment variables:
        - GMAIL_CREDENTIALS_PATH: Path to credentials.json file (optional, default: "credentials.json")
        - GMAIL_TOKEN_PATH: Path to token.json file (optional, default: "token.json")
        - GMAIL_TIMEOUT_SECONDS: Request timeout (optional, default: 30)
        - GMAIL_MAX_RETRIES: Maximum retry attempts (optional, default: 3)

        Args:
            env_prefix: Prefix for environment variable names

        Returns:
            GmailConfig instance

        Raises:
            EmailConfigurationError: If configuration is invalid
        """
        def get_env_var(name: str, required: bool = True, default: Optional[str] = None) -> str:
            """Get environment variable with proper error handling."""
            value = os.getenv(f"{env_prefix}{name}", default)
            if required and not value:
                raise EmailConfigurationError(f"Required environment variable {env_prefix}{name} not found")
            return value or (default or "")

        config = cls(
            credentials_path=get_env_var("CREDENTIALS_PATH", required=False, default="credentials.json"),
            token_path=get_env_var("TOKEN_PATH", required=False, default="token.json"),
            timeout_seconds=int(get_env_var("TIMEOUT_SECONDS", required=False, default="30")),
            max_retries=int(get_env_var("MAX_RETRIES", required=False, default="3"))
        )

        config.validate()
        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'credentials_path': self.credentials_path,
            'token_path': self.token_path,
            'scopes': self.scopes,
            'timeout_seconds': self.timeout_seconds,
            'max_retries': self.max_retries
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GmailConfig":
        """Create configuration from dictionary."""
        config = cls(**data)
        config.validate()
        return config


def get_default_gmail_config() -> GmailConfig:
    """
    Get default Gmail configuration.

    This creates a configuration with default file paths that works
    with the standard Gmail API setup process.

    Returns:
        GmailConfig instance with default settings

    Raises:
        EmailConfigurationError: If configuration is invalid
    """
    config = GmailConfig()
    config.validate()
    return config
