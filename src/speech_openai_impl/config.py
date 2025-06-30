"""Configuration for OpenAI API clients."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OpenAIConfig:
    """Configuration for OpenAI API clients.

    Args:
        api_key: OpenAI API key (required)
        organization: OpenAI organization ID (optional)
        base_url: Base URL for OpenAI API (default: https://api.openai.com/v1)
        timeout: Request timeout in seconds (default: 30)
    """
    api_key: str
    organization: Optional[str] = None
    base_url: str = "https://api.openai.com/v1"
    timeout: int = 30

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.api_key or not self.api_key.strip():
            raise ValueError("API key is required")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
