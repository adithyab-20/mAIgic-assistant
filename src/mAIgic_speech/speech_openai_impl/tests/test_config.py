"""Tests for OpenAI configuration."""

import pytest

from mAIgic_speech.speech_openai_impl.config import OpenAIConfig


class TestOpenAIConfig:
    """Test cases for OpenAIConfig."""

    def test_valid_config_creation(self) -> None:
        """Test creating a valid configuration."""
        config = OpenAIConfig(api_key="test-key")

        assert config.api_key == "test-key"
        assert config.organization is None
        assert config.base_url == "https://api.openai.com/v1"
        assert config.timeout == 30

    def test_config_with_all_parameters(self) -> None:
        """Test creating configuration with all parameters."""
        config = OpenAIConfig(
            api_key="test-key",
            organization="test-org",
            base_url="https://custom.openai.com/v1",
            timeout=60
        )

        assert config.api_key == "test-key"
        assert config.organization == "test-org"
        assert config.base_url == "https://custom.openai.com/v1"
        assert config.timeout == 60

    def test_empty_api_key_raises_error(self) -> None:
        """Test that empty API key raises ValueError."""
        with pytest.raises(ValueError, match="API key is required"):
            OpenAIConfig(api_key="")

    def test_none_api_key_raises_error(self) -> None:
        """Test that None API key raises ValueError."""
        with pytest.raises(ValueError, match="API key is required"):
            OpenAIConfig(api_key=None)  # type: ignore

    def test_zero_timeout_raises_error(self) -> None:
        """Test that zero timeout raises ValueError."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            OpenAIConfig(api_key="test-key", timeout=0)

    def test_negative_timeout_raises_error(self) -> None:
        """Test that negative timeout raises ValueError."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            OpenAIConfig(api_key="test-key", timeout=-1)

    def test_whitespace_api_key_raises_error(self) -> None:
        """Test that whitespace-only API key raises ValueError."""
        with pytest.raises(ValueError, match="API key is required"):
            OpenAIConfig(api_key="   ")
