"""Configuration management for mAIgic integrations."""

import os
from dataclasses import dataclass
from typing import Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class IntegrationConfig:
    """Configuration for all integrations."""

    # Environment settings
    environment: str = "development"
    credentials_dir: str = "credentials"
    credential_storage: str = "file"

    # Integration enablement
    google_calendar_enabled: bool = False
    google_gmail_enabled: bool = False
    microsoft_outlook_enabled: bool = False

    # User settings
    default_user: str = "default"

    @classmethod
    def from_env(cls, **overrides: Any) -> "IntegrationConfig":
        """Create configuration from environment variables."""
        return cls(
            environment=overrides.get("environment", os.getenv("MAIGIC_ENVIRONMENT", "development")),
            credentials_dir=overrides.get("credentials_dir", os.getenv("MAIGIC_CREDENTIALS_DIR", "credentials")),
            credential_storage=overrides.get("credential_storage", os.getenv("MAIGIC_CREDENTIAL_STORAGE", "file")),

            google_calendar_enabled=overrides.get(
                "google_calendar_enabled",
                os.getenv("GOOGLE_CALENDAR_ENABLED", "false").lower() == "true"
            ),
            google_gmail_enabled=overrides.get(
                "google_gmail_enabled",
                os.getenv("GOOGLE_GMAIL_ENABLED", "false").lower() == "true"
            ),
            microsoft_outlook_enabled=overrides.get(
                "microsoft_outlook_enabled",
                os.getenv("MICROSOFT_OUTLOOK_ENABLED", "false").lower() == "true"
            ),

            default_user=overrides.get("default_user", os.getenv("MAIGIC_DEFAULT_USER", "default")),
        )

    def validate(self) -> None:  # pragma: no cover
        """Validate configuration settings."""
        if not self.credentials_dir:  # pragma: no cover
            raise ValueError("credentials_dir cannot be empty")  # pragma: no cover

        if self.environment not in ["development", "staging", "production"]:  # pragma: no cover
            raise ValueError(f"Invalid environment: {self.environment}")  # pragma: no cover

        if self.credential_storage not in ["file", "vault"]:  # pragma: no cover
            raise ValueError(f"Invalid credential_storage: {self.credential_storage}")  # pragma: no cover
