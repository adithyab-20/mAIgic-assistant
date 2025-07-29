"""Google Calendar configuration."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..calendar_api.exceptions import CalendarConfigurationError

DEFAULT_SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]


@dataclass
class GoogleCalendarConfig:
    """Configuration for Google Calendar integration."""

    credentials_path: str
    token_path: str
    scopes: list[str]
    read_only: bool = False
    delegate_email: str | None = None
    user_timezone: str = "UTC"
    application_name: str = "mAIgic Calendar"

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Handle None scopes
        if self.scopes is None:
            self.scopes = DEFAULT_SCOPES.copy()
        elif not self.scopes:
            self.scopes = DEFAULT_SCOPES.copy()

        self.validate()

    def validate(self) -> None:
        """Validate configuration settings.

        Raises:
            CalendarConfigurationError: If configuration is invalid
        """
        # Validate credentials file exists and is readable
        credentials_file = Path(self.credentials_path)
        if not credentials_file.exists():
            raise CalendarConfigurationError(
                f"Credentials file not found: {self.credentials_path}"
            )

        if not credentials_file.is_file():
            raise CalendarConfigurationError(
                f"Credentials path is not a file: {self.credentials_path}"
            )

        # Validate credentials file is valid JSON
        try:
            with open(credentials_file) as f:
                json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise CalendarConfigurationError(
                f"Invalid credentials file format: {e}"
            ) from e

        # Validate token path directory exists or can be created
        token_path = Path(self.token_path)
        token_dir = token_path.parent
        if not token_dir.exists():
            try:
                token_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise CalendarConfigurationError(
                    f"Cannot create token directory: {e}"
                ) from e

        # Validate scopes format
        if not isinstance(self.scopes, list):
            raise CalendarConfigurationError("Scopes must be a list of strings")

        for scope in self.scopes:
            if not isinstance(scope, str):
                raise CalendarConfigurationError("All scopes must be strings")

        # Validate delegate email format if provided
        if self.delegate_email is not None:
            if not isinstance(self.delegate_email, str) or '@' not in self.delegate_email:
                raise CalendarConfigurationError(
                    "Delegate email must be a valid email address"
                )

    @classmethod
    def from_env(cls, **kwargs: Any) -> "GoogleCalendarConfig":
        """Create configuration from environment variables.

        Environment variables:
        - GOOGLE_CALENDAR_CREDENTIALS_PATH
        - GOOGLE_CALENDAR_TOKEN_PATH
        - GOOGLE_CALENDAR_SCOPES (comma-separated)
        - GOOGLE_CALENDAR_READ_ONLY
        - GOOGLE_CALENDAR_DELEGATE_EMAIL

        Args:
            **kwargs: Override specific configuration values

        Returns:
            GoogleCalendarConfig instance
        """
        # Default paths based on new structure
        credentials_path = kwargs.get(
            "credentials_path",
            os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "credentials/google_calendar/credentials.json")
        )
        token_path = kwargs.get(
            "token_path",
            os.getenv("GOOGLE_CALENDAR_TOKEN_PATH", "credentials/google_calendar/token.json")
        )

        # Parse scopes from environment
        scopes_env = os.getenv("GOOGLE_CALENDAR_SCOPES", "")
        if scopes_env:
            scopes = [scope.strip() for scope in scopes_env.split(",")]
        else:
            scopes = DEFAULT_SCOPES.copy()

        # Parse boolean and optional values
        read_only = kwargs.get(
            "read_only",
            os.getenv("GOOGLE_CALENDAR_READ_ONLY", "false").lower() == "true"
        )
        delegate_email = kwargs.get(
            "delegate_email",
            os.getenv("GOOGLE_CALENDAR_DELEGATE_EMAIL")
        )

        config_data: dict[str, Any] = {
            "credentials_path": credentials_path,
            "token_path": token_path,
            "scopes": scopes,
            "read_only": read_only,
            "delegate_email": delegate_email,
        }

        # Override with any explicit kwargs
        config_data.update(kwargs)

        return cls(**config_data)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "credentials_path": self.credentials_path,
            "token_path": self.token_path,
            "scopes": self.scopes,
            "read_only": self.read_only,
            "delegate_email": self.delegate_email,
        }
