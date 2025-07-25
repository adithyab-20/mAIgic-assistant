"""
Gmail provider implementation.

This module provides the EmailProvider implementation for Gmail,
handling configuration and client creation.
"""

from typing import Any, List, cast

from ...registry import CredentialManager, EmailIntegrationProvider
from ..email_api.exceptions import EmailConfigurationError
from ..email_api.interfaces import EmailClient
from .clients import GmailClient
from .config import GmailConfig


class GmailProvider(EmailIntegrationProvider):
    """Gmail implementation of EmailProvider."""

    def get_service_name(self) -> str:
        """Get the service name for this provider."""
        return "google_gmail"

    def is_available(self) -> bool:
        """Check if this provider's dependencies are available."""
        try:
            import google.auth  # noqa: F401
            import google_auth_oauthlib.flow  # noqa: F401
            import googleapiclient.discovery  # noqa: F401
            return True
        except ImportError:
            return False

    def create_client(self, user_id: str, credential_manager: CredentialManager, **kwargs: Any) -> EmailClient:
        """Create a client instance using the credential manager."""
        # Get credentials from credential manager
        stored_credentials = credential_manager.get_credentials(user_id, self.get_service_name())

        if not stored_credentials:
            raise EmailConfigurationError(
                f"No credentials found for user '{user_id}' and service '{self.get_service_name()}'. "
                "Please run credential setup first."
            )

        # Create configuration from stored credentials and kwargs
        config = {
            "credentials_path": stored_credentials.get("credentials_path"),
            "token_path": stored_credentials.get("token_path", "token.json"),
            "timeout_seconds": kwargs.get("timeout_seconds", stored_credentials.get("timeout_seconds", 30)),
            "max_retries": kwargs.get("max_retries", stored_credentials.get("max_retries", 3))
        }

        # Create Gmail config and client
        gmail_config = GmailConfig(**config)
        gmail_config.validate()
        return GmailClient(gmail_config)

    def get_required_credentials(self) -> List[str]:
        """Get list of required credential fields."""
        return ["credentials_path"]

    def create_client_legacy(self, **config: Any) -> EmailClient:
        """
        Create a Gmail client instance.

        Args:
            **config: Gmail configuration parameters
                - credentials_path: Path to credentials.json file
                - token_path: Path to token.json file
                - timeout_seconds: Request timeout
                - max_retries: Maximum retry attempts

        Returns:
            Configured Gmail client instance
        """
        try:
            gmail_config = GmailConfig(**config)
            gmail_config.validate()
            return GmailClient(gmail_config)
        except Exception as e:
            raise EmailConfigurationError(f"Failed to create Gmail client: {str(e)}") from e

    def validate_config(self, **config: Any) -> bool:
        """
        Validate Gmail configuration.

        Args:
            **config: Configuration parameters to validate

        Returns:
            True if configuration is valid

        Raises:
            EmailConfigurationError: If configuration is invalid
        """
        try:
            gmail_config = GmailConfig(**config)
            gmail_config.validate()
            return True
        except EmailConfigurationError:
            raise
        except Exception as e:
            raise EmailConfigurationError(f"Invalid Gmail configuration: {str(e)}") from e

    def get_required_config_keys(self) -> List[str]:
        """
        Get list of required configuration keys for Gmail.

        Returns:
            List of required configuration key names
        """
        return ["credentials_path"]

    def get_optional_config_keys(self) -> List[str]:
        """
        Get list of optional configuration keys for Gmail.

        Returns:
            List of optional configuration key names
        """
        return ["token_path", "timeout_seconds", "max_retries"]

    def get_config_description(self) -> str:
        """
        Get human-readable description of Gmail configuration.

        Returns:
            Configuration description
        """
        return """
        Gmail Configuration:

        Required:
        - credentials_path: Path to Gmail API credentials.json file

        Optional:
        - token_path: Path to store OAuth2 tokens (default: "token.json")
        - timeout_seconds: Request timeout in seconds (default: 30)
        - max_retries: Maximum retry attempts (default: 3)

        Setup Instructions:
        1. Go to Google Cloud Console
        2. Create a new project or select existing one
        3. Enable Gmail API
        4. Create OAuth2 credentials (Desktop application)
        5. Download credentials.json file
        6. Set credentials_path to the file location
        """


def create_gmail_client(**config: Any) -> GmailClient:
    """
    Convenience function to create a Gmail client.

    Args:
        **config: Gmail configuration parameters

    Returns:
        Configured Gmail client instance
    """
    provider = GmailProvider()
    client = provider.create_client(**config)
    return cast(GmailClient, client)


def create_gmail_client_from_env(env_prefix: str = "GMAIL_") -> GmailClient:
    """
    Create Gmail client from environment variables.

    Args:
        env_prefix: Prefix for environment variable names

    Returns:
        Configured Gmail client instance
    """
    config = GmailConfig.from_env(env_prefix)
    return GmailClient(config)
