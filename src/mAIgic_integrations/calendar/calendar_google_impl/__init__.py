"""
Google Calendar Implementation.

This package provides a Google Calendar implementation of the mAIgic calendar interface.
Uses the Google Calendar API v3 for all calendar operations.

Example usage:
    from mAIgic_integrations.calendar.calendar_google_impl import (
        GoogleCalendarClient,
        GoogleCalendarConfig,
        GoogleCalendarProvider
    )

    config = GoogleCalendarConfig(
        credentials_path="path/to/credentials.json",
        token_path="path/to/token.json"
    )

    async with GoogleCalendarClient(config) as client:
        events = await client.get_events(time_range)
        result = await client.create_my_event(event)
"""

from .clients import GoogleCalendarClient
from .config import GoogleCalendarConfig
from .providers import GoogleCalendarProvider

__all__ = [
    "GoogleCalendarClient",
    "GoogleCalendarConfig",
    "GoogleCalendarProvider",
]

__version__ = "0.1.0"
__author__ = "mAIgic Assistant"
__description__ = "Google Calendar implementation for mAIgic calendar interface"
