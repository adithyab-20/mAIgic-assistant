"""
Tests for Gmail configuration functionality.
"""

import os
from unittest.mock import patch

import pytest

from ...email_api.exceptions import EmailConfigurationError
from ..config import GmailConfig, get_default_gmail_config


class TestGmailConfig:
    """Test cases for Gmail configuration class."""

    def test_basic_config_creation(self):
        """Test creating a basic Gmail configuration."""
        config = GmailConfig(
            credentials_path="my_credentials.json",
            token_path="my_token.json"
        )

        assert config.credentials_path == "my_credentials.json"
        assert config.token_path == "my_token.json"
        assert config.timeout_seconds == 30
        assert config.max_retries == 3
        assert len(config.scopes) == 3  # Default scopes are set

    def test_default_config_creation(self):
        """Test creating configuration with default values."""
        config = GmailConfig()

        assert config.credentials_path == "credentials.json"
        assert config.token_path == "token.json"
        assert config.timeout_seconds == 30
        assert config.max_retries == 3
        assert config.scopes is not None

    def test_config_with_custom_scopes(self):
        """Test creating configuration with custom OAuth2 scopes."""
        custom_scopes = ["https://www.googleapis.com/auth/gmail.readonly"]

        config = GmailConfig(
            scopes=custom_scopes
        )

        assert config.scopes == custom_scopes

    def test_config_with_custom_settings(self):
        """Test creating configuration with custom timeout and retry settings."""
        config = GmailConfig(
            timeout_seconds=60,
            max_retries=5
        )

        assert config.timeout_seconds == 60
        assert config.max_retries == 5

    @patch('os.path.exists')
    def test_config_validation_success(self, mock_exists):
        """Test successful configuration validation."""
        mock_exists.return_value = True  # Mock that credentials file exists

        config = GmailConfig(
            credentials_path="test_credentials.json"
        )

        # Should not raise an exception
        config.validate()
        mock_exists.assert_called_once_with("test_credentials.json")

    @patch('os.path.exists')
    def test_config_validation_missing_credentials_file(self, mock_exists):
        """Test validation failure for missing credentials file."""
        mock_exists.return_value = False  # Mock that file doesn't exist

        config = GmailConfig(
            credentials_path="nonexistent.json"
        )

        with pytest.raises(EmailConfigurationError, match="Gmail credentials file not found"):
            config.validate()

    def test_config_validation_invalid_timeout(self):
        """Test validation failure for invalid timeout."""
        config = GmailConfig(
            timeout_seconds=0
        )

        with pytest.raises(EmailConfigurationError, match="timeout_seconds must be positive"):
            config.validate()

    def test_config_validation_invalid_retries(self):
        """Test validation failure for invalid retry count."""
        config = GmailConfig(
            max_retries=-1
        )

        with pytest.raises(EmailConfigurationError, match="max_retries must be non-negative"):
            config.validate()


class TestGmailConfigFromEnvironment:
    """Test cases for environment-based configuration."""

    @patch('os.path.exists')
    @patch.dict(os.environ, {
        'GMAIL_CREDENTIALS_PATH': 'env_credentials.json',
        'GMAIL_TOKEN_PATH': 'env_token.json',
        'GMAIL_TIMEOUT_SECONDS': '45',
        'GMAIL_MAX_RETRIES': '2'
    })
    def test_from_env_basic(self, mock_exists):
        """Test loading configuration from environment variables."""
        mock_exists.return_value = True  # Mock that credentials file exists

        config = GmailConfig.from_env()

        assert config.credentials_path == "env_credentials.json"
        assert config.token_path == "env_token.json"
        assert config.timeout_seconds == 45
        assert config.max_retries == 2

    @patch('os.path.exists')
    @patch.dict(os.environ, {
        'MYAPP_CREDENTIALS_PATH': 'custom_creds.json',
        'MYAPP_TOKEN_PATH': 'custom_token.json',
        'MYAPP_TIMEOUT_SECONDS': '60',
        'MYAPP_MAX_RETRIES': '1'
    })
    def test_from_env_custom_prefix(self, mock_exists):
        """Test loading configuration with custom environment prefix."""
        mock_exists.return_value = True  # Mock that credentials file exists

        config = GmailConfig.from_env(env_prefix="MYAPP_")

        assert config.credentials_path == "custom_creds.json"
        assert config.token_path == "custom_token.json"
        assert config.timeout_seconds == 60
        assert config.max_retries == 1

    @patch.dict(os.environ, {})
    def test_from_env_with_defaults(self):
        """Test loading configuration with missing environment variables uses defaults."""
        config = GmailConfig.from_env()

        # Should use default values when env vars are not set
        assert config.credentials_path == "credentials.json"
        assert config.token_path == "token.json"
        assert config.timeout_seconds == 30
        assert config.max_retries == 3

    @patch.dict(os.environ, {
        'GMAIL_TIMEOUT_SECONDS': 'invalid'
    })
    def test_from_env_invalid_numeric(self):
        """Test environment loading with invalid numeric values."""
        with pytest.raises(ValueError):
            GmailConfig.from_env()


class TestGetDefaultGmailConfig:
    """Test cases for the convenience function."""

    @patch('os.path.exists')
    def test_get_default_config(self, mock_exists):
        """Test getting default configuration."""
        mock_exists.return_value = True  # Mock that credentials file exists

        config = get_default_gmail_config()

        # Should use default values, not environment variables
        assert config.credentials_path == "credentials.json"
        assert config.token_path == "token.json"
        assert config.timeout_seconds == 30
        assert config.max_retries == 3

    @patch('os.path.exists')
    def test_get_default_config_with_defaults(self, mock_exists):
        """Test getting default configuration with no environment variables."""
        mock_exists.return_value = True  # Mock that credentials file exists

        config = get_default_gmail_config()

        # Should use default values
        assert config.credentials_path == "credentials.json"
        assert config.token_path == "token.json"
        assert config.timeout_seconds == 30
        assert config.max_retries == 3
