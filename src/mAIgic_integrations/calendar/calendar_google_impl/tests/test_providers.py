"""
Tests for Google Calendar Provider.

This module tests the GoogleCalendarProvider class and its functionality.
"""

import json
from unittest.mock import Mock

import pytest

from ....credentials import CredentialManager
from ...calendar_api.exceptions import CalendarConfigurationError
from ..clients import GoogleCalendarClient
from ..config import GoogleCalendarConfig
from ..providers import GoogleCalendarProvider


class TestGoogleCalendarProvider:
    """Test GoogleCalendarProvider functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.provider = GoogleCalendarProvider()
        # Create a mock credential manager for tests
        self.mock_credential_manager = Mock(spec=CredentialManager)
        # Set up the mock to return valid credentials
        self.mock_credential_manager.get_credentials.return_value = {
            "credentials_path": "test_credentials.json",
            "token_path": "test_token.json",
            "scopes": ["https://www.googleapis.com/auth/calendar"]
        }

    def test_get_required_config_keys(self):
        """Test required configuration keys."""
        required_keys = self.provider.get_required_config_keys()

        assert required_keys == ["credentials_path"]

    def test_get_optional_config_keys(self):
        """Test optional configuration keys."""
        optional_keys = self.provider.get_optional_config_keys()

        expected_keys = [
            "token_path",
            "scopes",
            "application_name",
            "user_timezone",
            "read_only",
            "delegate_email"
        ]
        assert optional_keys == expected_keys

    def test_get_config_description_required(self):
        """Test config description for required keys."""
        description = self.provider.get_config_description("credentials_path")

        assert "Google OAuth2 credentials JSON file" in description
        assert "Google Cloud Console" in description

    def test_get_config_description_optional(self):
        """Test config description for optional keys."""
        description = self.provider.get_config_description("token_path")
        assert "OAuth2 access/refresh tokens" in description

        description = self.provider.get_config_description("user_timezone")
        assert "timezone" in description.lower()

        description = self.provider.get_config_description("read_only")
        assert "read-only access" in description

    def test_get_config_description_unknown_key(self):
        """Test config description for unknown key."""
        description = self.provider.get_config_description("unknown_key")
        assert description == "Configuration key: unknown_key"

    def test_validate_config_valid(self, tmp_path):
        """Test configuration validation with valid config."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "client_id": "test-client-id",
            "client_secret": "test-client-secret"
        }))

        config = {
            "credentials_path": str(credentials_file),
            "token_path": "token.json",
            "application_name": "Test App",
            "user_timezone": "US/Eastern",
            "read_only": False
        }

        assert self.provider.validate_config(config) is True

    def test_validate_config_minimal_valid(self, tmp_path):
        """Test validation with minimal valid config."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "client_id": "test-client-id",
            "client_secret": "test-client-secret"
        }))

        config = {
            "credentials_path": str(credentials_file)
        }

        assert self.provider.validate_config(config) is True

    def test_validate_config_not_dict(self):
        """Test validation fails for non-dict config."""
        assert self.provider.validate_config("not a dict") is False
        assert self.provider.validate_config(None) is False
        assert self.provider.validate_config([]) is False

    def test_validate_config_missing_required(self):
        """Test validation fails for missing required keys."""
        config = {
            "token_path": "token.json"
            # Missing credentials_path
        }

        assert self.provider.validate_config(config) is False

    def test_validate_config_empty_required_value(self, tmp_path):
        """Test validation fails for empty required values."""
        config = {
            "credentials_path": ""  # Empty string
        }

        assert self.provider.validate_config(config) is False

        config = {
            "credentials_path": None  # None value
        }

        assert self.provider.validate_config(config) is False

    def test_validate_config_invalid_credentials_path_type(self):
        """Test validation fails for non-string credentials path."""
        config = {
            "credentials_path": 123  # Should be string
        }

        assert self.provider.validate_config(config) is False

    def test_validate_config_invalid_optional_types(self, tmp_path):
        """Test validation fails for invalid optional field types."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "client_id": "test-client-id",
            "client_secret": "test-client-secret"
        }))

        # Invalid token_path type
        config = {
            "credentials_path": str(credentials_file),
            "token_path": 123  # Should be string
        }
        assert self.provider.validate_config(config) is False

        # Invalid scopes type
        config = {
            "credentials_path": str(credentials_file),
            "scopes": "not-a-list"  # Should be list or None
        }
        assert self.provider.validate_config(config) is False

        # Invalid application_name type
        config = {
            "credentials_path": str(credentials_file),
            "application_name": 123  # Should be string
        }
        assert self.provider.validate_config(config) is False

        # Invalid user_timezone type
        config = {
            "credentials_path": str(credentials_file),
            "user_timezone": 123  # Should be string
        }
        assert self.provider.validate_config(config) is False

        # Invalid read_only type
        config = {
            "credentials_path": str(credentials_file),
            "read_only": "not-bool"  # Should be bool
        }
        assert self.provider.validate_config(config) is False

        # Invalid delegate_email type (non-None, non-string)
        config = {
            "credentials_path": str(credentials_file),
            "delegate_email": 123  # Should be string or None
        }
        assert self.provider.validate_config(config) is False

    def test_validate_config_valid_optional_types(self, tmp_path):
        """Test validation passes for valid optional field types."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "client_id": "test-client-id",
            "client_secret": "test-client-secret"
        }))

        # Valid scopes as None
        config = {
            "credentials_path": str(credentials_file),
            "scopes": None
        }
        assert self.provider.validate_config(config) is True

        # Valid scopes as list
        config = {
            "credentials_path": str(credentials_file),
            "scopes": ["scope1", "scope2"]
        }
        assert self.provider.validate_config(config) is True

        # Valid delegate_email as None
        config = {
            "credentials_path": str(credentials_file),
            "delegate_email": None
        }
        assert self.provider.validate_config(config) is True

    def test_create_client_valid_config(self, tmp_path):
        """Test creating client with valid configuration."""
        credentials_file = tmp_path / "test_credentials.json"
        credentials_file.write_text(json.dumps({
            "installed": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }))

        # Update mock to return the actual test file path
        self.mock_credential_manager.get_credentials.return_value = {
            "credentials_path": str(credentials_file),
            "token_path": str(tmp_path / "token.json"),
            "scopes": ["https://www.googleapis.com/auth/calendar"]
        }

        config = {
            "read_only": False
        }

        client = self.provider.create_client("test_user", self.mock_credential_manager, **config)

        assert isinstance(client, GoogleCalendarClient)
        assert isinstance(client.config, GoogleCalendarConfig)
        assert client.config.credentials_path == str(credentials_file)
        assert client.config.token_path == str(tmp_path / "token.json")
        assert client.config.read_only is False

    def test_create_client_invalid_config(self):
        """Test creating client with invalid configuration."""
        invalid_config = {
            "credentials_path": "nonexistent.json"
        }

        with pytest.raises(CalendarConfigurationError, match="Credentials file not found"):
            self.provider.create_client("test_user", self.mock_credential_manager, **invalid_config)

    def test_create_client_validation_fails(self):
        """Test creating client when validation fails."""
        invalid_config = {
            # Missing credentials_path
            "token_path": "token.json"
        }

        with pytest.raises(CalendarConfigurationError, match="Credentials file not found"):
            self.provider.create_client("test_user", self.mock_credential_manager, **invalid_config)

    def test_get_setup_instructions(self):
        """Test getting setup instructions."""
        instructions = GoogleCalendarProvider.get_setup_instructions()

        assert "Google Cloud Console" in instructions
        assert "OAuth 2.0 Client ID" in instructions
        assert "Enable the Google Calendar API" in instructions
        assert "Download the JSON file" in instructions

    def test_get_provider_info(self):
        """Test getting provider information."""
        info = GoogleCalendarProvider.get_provider_info()

        assert info["name"] == "Google Calendar"
        assert info["provider_id"] == "google"
        assert info["description"] == "Google Calendar integration using Google Calendar API v3"
        assert info["version"] == "0.1.0"
        assert info["authentication"] == "OAuth2"

        # Check supported features
        supported_features = info["supported_features"]
        assert "event_creation" in supported_features
        assert "event_modification" in supported_features
        assert "availability_queries" in supported_features
        assert "batch_operations" in supported_features

        # Check unsupported features
        unsupported_features = info["unsupported_features"]
        assert "reschedule_suggestions" in unsupported_features

        # Check required dependencies
        dependencies = info["required_dependencies"]
        assert "google-auth" in dependencies
        assert "google-auth-oauthlib" in dependencies
        assert "google-api-python-client" in dependencies
