"""
Google Calendar Provider Implementation.

This module provides the GoogleCalendarProvider that implements the CalendarIntegrationProvider
interface for creating and configuring Google Calendar clients.
"""

from typing import Any

from ...registry import CalendarIntegrationProvider, CredentialManager
from ..calendar_api.exceptions import CalendarConfigurationError
from ..calendar_api.interfaces import CalendarClient
from .clients import GoogleCalendarClient
from .config import GoogleCalendarConfig


class GoogleCalendarProvider(CalendarIntegrationProvider):
    """
    Google Calendar provider for creating calendar clients.

    Handles configuration validation and client creation for Google Calendar integration.
    """

    def get_service_name(self) -> str:
        """Get the service name for this provider."""
        return "google_calendar"

    def is_available(self) -> bool:
        """Check if this provider's dependencies are available."""
        try:
            import google.auth  # noqa: F401
            import google_auth_oauthlib.flow  # noqa: F401
            import googleapiclient.discovery  # noqa: F401
            return True
        except ImportError:
            return False

    def create_client(self, user_id: str, credential_manager: CredentialManager, **kwargs: Any) -> CalendarClient:
        """Create a client instance using the credential manager."""
        # Get credentials from credential manager
        stored_credentials = credential_manager.get_credentials(user_id, self.get_service_name())

        if not stored_credentials:
            raise CalendarConfigurationError(
                f"No credentials found for user '{user_id}' and service '{self.get_service_name()}'. "
                "Please run credential setup first."
            )

        # Create configuration from stored credentials and kwargs
        credentials_path = stored_credentials.get("credentials_path")
        if not credentials_path:
            raise CalendarConfigurationError("Missing credentials_path in stored credentials")

        config = GoogleCalendarConfig(
            credentials_path=credentials_path,
            token_path=stored_credentials.get("token_path", "token.json"),
            scopes=stored_credentials.get("scopes", ["https://www.googleapis.com/auth/calendar"]),
            read_only=kwargs.get("read_only", stored_credentials.get("read_only", False)),
            delegate_email=kwargs.get("delegate_email", stored_credentials.get("delegate_email")),
            user_timezone=kwargs.get("user_timezone", stored_credentials.get("user_timezone", "UTC")),
            application_name=kwargs.get("application_name", stored_credentials.get("application_name", "mAIgic Assistant"))
        )

        # Create and return client
        return GoogleCalendarClient(config)

    def get_required_credentials(self) -> list[str]:
        """Get list of required credential fields."""
        return ["credentials_path"]

    async def create_client_legacy(self, config: dict[str, Any]) -> CalendarClient:
        """
        Create and configure a Google Calendar client.

        Args:
            config: Configuration dictionary with Google Calendar settings

        Returns:
            Configured GoogleCalendarClient instance

        Raises:
            CalendarConfigurationError: If configuration is invalid
        """
        try:
            # Validate configuration first
            if not self.validate_config(config):
                raise CalendarConfigurationError("Invalid configuration provided")

            # Create configuration object
            scopes = config.get("scopes")
            if scopes is None:
                scopes = ["https://www.googleapis.com/auth/calendar"]

            google_config = GoogleCalendarConfig(
                credentials_path=config["credentials_path"],
                token_path=config.get("token_path", "token.json"),
                scopes=scopes,
                read_only=config.get("read_only", False),
                delegate_email=config.get("delegate_email")
            )

            # Create and return client
            return GoogleCalendarClient(google_config)

        except Exception as e:
            raise CalendarConfigurationError(f"Failed to create Google Calendar client: {e}")

    def validate_config(self, config: dict[str, Any]) -> bool:
        """
        Validate Google Calendar configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(config, dict):
            return False

        # Check required keys
        required_keys = self.get_required_config_keys()
        for key in required_keys:
            if key not in config:
                return False

            # Check that required values are not None or empty
            if not config[key]:
                return False

        # Validate specific field types and formats
        if not isinstance(config["credentials_path"], str):
            return False

        # Validate optional fields if present
        optional_keys = self.get_optional_config_keys()
        for key in optional_keys:
            if key in config:
                # Type validation for optional fields
                if key == "token_path" and not isinstance(config[key], str):
                    return False
                elif key == "scopes" and not (isinstance(config[key], list) or config[key] is None):
                    return False
                elif key == "application_name" and not isinstance(config[key], str):
                    return False
                elif key == "user_timezone" and not isinstance(config[key], str):
                    return False
                elif key == "read_only" and not isinstance(config[key], bool):
                    return False
                elif key == "delegate_email" and config[key] is not None and not isinstance(config[key], str):
                    return False

        return True

    def get_required_config_keys(self) -> list[str]:
        """
        Get list of required configuration keys for Google Calendar.

        Returns:
            List of required configuration keys
        """
        return [
            "credentials_path"  # Path to Google OAuth2 credentials JSON file
        ]

    def get_optional_config_keys(self) -> list[str]:
        """
        Get list of optional configuration keys for Google Calendar.

        Returns:
            List of optional configuration keys
        """
        return [
            "token_path",        # Path to store OAuth2 tokens (default: "token.json")
            "scopes",           # List of OAuth2 scopes (default: auto-determined)
            "application_name",  # Application name (default: "mAIgic Assistant")
            "user_timezone",    # User's timezone (default: "UTC")
            "read_only",        # Read-only access (default: False)
            "delegate_email"    # Email for service account delegation (default: None)
        ]

    def get_config_description(self, key: str) -> str:
        """
        Get human-readable description of a configuration key.

        Args:
            key: Configuration key to describe

        Returns:
            Human-readable description of the configuration key
        """
        descriptions = {
            "credentials_path": (
                "Path to Google OAuth2 credentials JSON file. "
                "Download this from Google Cloud Console after setting up OAuth2 credentials."
            ),
            "token_path": (
                "Path where OAuth2 access/refresh tokens will be stored. "
                "Defaults to 'token.json' in the current directory."
            ),
            "scopes": (
                "List of Google Calendar API OAuth2 scopes to request. "
                "If not specified, defaults to appropriate scopes based on read_only setting."
            ),
            "application_name": (
                "Name to identify your application in Google Calendar API requests. "
                "Defaults to 'mAIgic Assistant'."
            ),
            "user_timezone": (
                "Default timezone for the user (e.g., 'US/Eastern', 'Europe/London'). "
                "Used for timezone-aware operations. Defaults to 'UTC'."
            ),
            "read_only": (
                "Whether to request read-only access to Google Calendar. "
                "If True, only viewing operations will be available. Defaults to False."
            ),
            "delegate_email": (
                "Email address of the user to impersonate when using service account credentials. "
                "Only needed for service account authentication. Defaults to None."
            )
        }

        return descriptions.get(key, f"Configuration key: {key}")

    @classmethod
    def get_setup_instructions(cls) -> str:
        """
        Get setup instructions for Google Calendar integration.

        Returns:
            Detailed setup instructions
        """
        return """
Google Calendar Setup Instructions:

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to APIs & Services > Library
   - Search for "Google Calendar API"
   - Click on it and press "Enable"

4. Create credentials:
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Configure OAuth consent screen if prompted
   - Choose "Desktop application" as application type
   - Download the JSON file

5. Save the credentials file and set the path in your configuration

Required scopes:
   - For read-only: https://www.googleapis.com/auth/calendar.readonly
   - For full access: https://www.googleapis.com/auth/calendar

For more details, see: https://developers.google.com/calendar/quickstart/python
"""

    @classmethod
    def get_provider_info(cls) -> dict[str, Any]:
        """
        Get information about this calendar provider.

        Returns:
            Provider information dictionary
        """
        return {
            "name": "Google Calendar",
            "provider_id": "google",
            "description": "Google Calendar integration using Google Calendar API v3",
            "version": "0.1.0",
            "supported_features": [
                "event_creation",
                "event_modification",
                "event_deletion",
                "invitation_responses",
                "availability_queries",
                "event_search",
                "recurring_events",
                "batch_operations",
                "multiple_calendars"
            ],
            "unsupported_features": [
                "reschedule_suggestions"  # Google Calendar API limitation
            ],
            "required_dependencies": [
                "google-auth",
                "google-auth-oauthlib",
                "google-api-python-client"
            ],
            "authentication": "OAuth2",
            "documentation_url": "https://developers.google.com/calendar/api"
        }
