"""Test GoogleCalendarConfig class."""

import json
import os
from unittest.mock import patch

import pytest

from ...calendar_api.exceptions import CalendarConfigurationError
from ..config import DEFAULT_SCOPES, GoogleCalendarConfig


class TestGoogleCalendarConfig:
    """Test GoogleCalendarConfig functionality."""

    def test_minimal_config(self, tmp_path):
        """Test minimal valid configuration."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "installed": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }))

        config = GoogleCalendarConfig(
            credentials_path=str(credentials_file),
            token_path="token.json",
            scopes=['https://www.googleapis.com/auth/calendar']
        )

        assert config.credentials_path == str(credentials_file)
        assert config.token_path == "token.json"
        assert config.read_only is False
        assert config.delegate_email is None

        # Check default scopes for full access
        assert "https://www.googleapis.com/auth/calendar" in config.scopes

    def test_read_only_config(self, tmp_path):
        """Test read-only configuration."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "installed": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }))

        config = GoogleCalendarConfig(
            credentials_path=str(credentials_file),
            token_path="token.json",
            scopes=["https://www.googleapis.com/auth/calendar.readonly"],
            read_only=True
        )

        expected_scopes = ["https://www.googleapis.com/auth/calendar.readonly"]
        assert config.scopes == expected_scopes
        assert config.read_only is True

    def test_custom_scopes(self, tmp_path):
        """Test custom scopes override defaults."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "installed": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }))

        custom_scopes = ["https://www.googleapis.com/auth/calendar.readonly"]
        config = GoogleCalendarConfig(
            credentials_path=str(credentials_file),
            token_path="token.json",
            scopes=custom_scopes
        )

        assert config.scopes == custom_scopes

    def test_delegate_email(self, tmp_path):
        """Test delegate email configuration."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "installed": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }))

        delegate_email = "delegate@example.com"
        config = GoogleCalendarConfig(
            credentials_path=str(credentials_file),
            token_path="token.json",
            scopes=DEFAULT_SCOPES,
            delegate_email=delegate_email
        )

        assert config.delegate_email == delegate_email

    def test_invalid_credentials_file(self):
        """Test validation with non-existent credentials file."""
        with pytest.raises(CalendarConfigurationError):
            GoogleCalendarConfig(
                credentials_path="nonexistent.json",
                token_path="token.json",
                scopes=DEFAULT_SCOPES
            )

    def test_invalid_credentials_format(self, tmp_path):
        """Test validation with invalid credentials file format."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text("invalid json")

        with pytest.raises(CalendarConfigurationError):
            GoogleCalendarConfig(
                credentials_path=str(credentials_file),
                token_path="token.json",
                scopes=DEFAULT_SCOPES
            )

    def test_invalid_scopes_format(self, tmp_path):
        """Test validation with invalid scopes format."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "installed": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }))

        with pytest.raises(CalendarConfigurationError):
            GoogleCalendarConfig(
                credentials_path=str(credentials_file),
                token_path="token.json",
                scopes="invalid_scopes"  # Should be a list
            )

    def test_token_path_directory_creation(self, tmp_path):
        """Test that token directory is created if it doesn't exist."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "installed": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }))

        token_path = tmp_path / "tokens" / "my_token.json"

        GoogleCalendarConfig(
            credentials_path=str(credentials_file),
            token_path=str(token_path),
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )

        # Directory should be created during validation
        assert token_path.parent.exists()

    def test_from_env_defaults(self, tmp_path):
        """Test creating config from environment variables with defaults."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "installed": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }))

        with patch.dict(os.environ, {
            "GOOGLE_CALENDAR_CREDENTIALS_PATH": str(credentials_file),
            "GOOGLE_CALENDAR_TOKEN_PATH": "test_token.json"
        }):
            config = GoogleCalendarConfig.from_env()

        assert config.credentials_path == str(credentials_file)
        assert config.token_path == "test_token.json"
        assert config.scopes == DEFAULT_SCOPES
        assert config.read_only is False
        assert config.delegate_email is None

    def test_from_env_custom_values(self, tmp_path):
        """Test creating config from environment variables with custom values."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "installed": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }))

        env_vars = {
            "GOOGLE_CALENDAR_CREDENTIALS_PATH": str(credentials_file),
            "GOOGLE_CALENDAR_TOKEN_PATH": "custom_token.json",
            "GOOGLE_CALENDAR_SCOPES": "https://www.googleapis.com/auth/calendar.readonly",
            "GOOGLE_CALENDAR_READ_ONLY": "true",
            "GOOGLE_CALENDAR_DELEGATE_EMAIL": "delegate@example.com"
        }

        with patch.dict(os.environ, env_vars):
            config = GoogleCalendarConfig.from_env()

        assert config.credentials_path == str(credentials_file)
        assert config.token_path == "custom_token.json"
        assert config.scopes == ["https://www.googleapis.com/auth/calendar.readonly"]
        assert config.read_only is True
        assert config.delegate_email == "delegate@example.com"

    def test_from_env_with_overrides(self, tmp_path):
        """Test creating config from environment with keyword overrides."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "installed": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }))

        with patch.dict(os.environ, {
            "GOOGLE_CALENDAR_CREDENTIALS_PATH": str(credentials_file),
        }):
            config = GoogleCalendarConfig.from_env(
                token_path="override_token.json",
                read_only=True
            )

        assert config.credentials_path == str(credentials_file)
        assert config.token_path == "override_token.json"
        assert config.read_only is True

    def test_to_dict(self, tmp_path):
        """Test converting config to dictionary."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "installed": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }))

        config = GoogleCalendarConfig(
            credentials_path=str(credentials_file),
            token_path="token.json",
            scopes=DEFAULT_SCOPES,
            read_only=True,
            delegate_email="delegate@example.com"
        )

        config_dict = config.to_dict()

        expected_dict = {
            "credentials_path": str(credentials_file),
            "token_path": "token.json",
            "scopes": DEFAULT_SCOPES,
            "read_only": True,
            "delegate_email": "delegate@example.com"
        }

        assert config_dict == expected_dict

    def test_invalid_delegate_email(self, tmp_path):
        """Test validation with invalid delegate email."""
        credentials_file = tmp_path / "credentials.json"
        credentials_file.write_text(json.dumps({
            "installed": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }))

        with pytest.raises(CalendarConfigurationError):
            GoogleCalendarConfig(
                credentials_path=str(credentials_file),
                token_path="token.json",
                scopes=DEFAULT_SCOPES,
                delegate_email="invalid-email"  # Missing @ symbol
            )
