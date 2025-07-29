"""
Calendar Integration Package.

This package provides a unified interface for calendar operations with a clean architecture
that supports multiple calendar providers. The interface uses role-based methods to clearly
separate organizer operations from attendee operations, preventing permission errors and
matching user mental models.

The package includes:
- Abstract calendar API interfaces and types
- Comprehensive exception hierarchy
- Full async/await support
- Role-based permission handling
- Rich time abstraction with timezone support
- Type safety throughout

Example usage:
    # Future Google Calendar implementation
    from mAIgic_integrations.calendar import GoogleCalendarClient, GoogleCalendarConfig

    config = GoogleCalendarConfig(
        credentials_path="credentials.json",
        token_path="token.json"
    )

    async with GoogleCalendarClient(config) as client:
        # Get events for context
        today = CalendarDateTime.now()
        tomorrow = today.add_hours(24)
        time_range = TimeSlot(today, tomorrow)
        events = await client.get_events(time_range)

        # Create my event
        event = Event(
            event_id="",
            title="Team Meeting",
            time_slot=TimeSlot(today.add_hours(2), today.add_hours(3))
        )
        result = await client.create_my_event(event)

        # Respond to invitation
        response = InvitationResponse(status=AttendeeStatus.ACCEPTED)
        await client.respond_to_invitation("some-event-id", response)
"""

# Core calendar types and enums
from .calendar_api.exceptions import (
    CalendarAPIError,
    CalendarAuthenticationError,
    CalendarConfigurationError,
    CalendarConnectionError,
    CalendarEventNotFoundError,
    CalendarInvitationError,
    CalendarPermissionError,
    CalendarQuotaExceededError,
    CalendarRateLimitError,
    CalendarRecurrenceError,
    CalendarSchedulingError,
    CalendarSyncError,
    CalendarTimeError,
    CalendarValidationError,
)

# Abstract interfaces
from .calendar_api.interfaces import (
    CalendarClient,
    CalendarProvider,
)
from .calendar_api.models import (
    # Core data classes
    Attendee,
    # Type aliases
    AttendeeList,
    # Enums
    AttendeeStatus,
    AvailabilityQuery,
    AvailableSlot,
    BatchUpdateResult,
    CalendarDateTime,
    CalendarInfo,
    CalendarSearchQuery,
    CalendarSearchResult,
    ConflictInfo,
    ConflictList,
    ConflictResolution,
    Event,
    EventChanges,
    EventList,
    EventPriority,
    EventStatus,
    InvitationActionType,
    InvitationResponse,
    NotifyOption,
    PermissionInfo,
    Recurrence,
    RecurrenceScope,
    TimeSlot,
    UpdateResult,
)

# Provider implementations
try:
    from .calendar_google_impl import GoogleCalendarProvider  # noqa: F401
    _GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    # Google Calendar dependencies not available
    _GOOGLE_CALENDAR_AVAILABLE = False

__all__ = [
    # Core data types
    "AttendeeStatus",
    "ConflictResolution",
    "EventPriority",
    "EventStatus",
    "InvitationActionType",
    "NotifyOption",
    "RecurrenceScope",
    "Attendee",
    "AvailabilityQuery",
    "AvailableSlot",
    "BatchUpdateResult",
    "CalendarDateTime",
    "CalendarInfo",
    "CalendarSearchQuery",
    "CalendarSearchResult",
    "ConflictInfo",
    "Event",
    "EventChanges",
    "InvitationResponse",
    "PermissionInfo",
    "Recurrence",
    "TimeSlot",
    "UpdateResult",
    "AttendeeList",
    "ConflictList",
    "EventList",

    # Abstract interfaces
    "CalendarClient",
    "CalendarProvider",

    # Exception hierarchy
    "CalendarAPIError",
    "CalendarAuthenticationError",
    "CalendarConfigurationError",
    "CalendarConnectionError",
    "CalendarEventNotFoundError",
    "CalendarInvitationError",
    "CalendarPermissionError",
    "CalendarQuotaExceededError",
    "CalendarRateLimitError",
    "CalendarRecurrenceError",
    "CalendarSchedulingError",
    "CalendarSyncError",
    "CalendarTimeError",
    "CalendarValidationError",

    # Provider implementations (added dynamically based on availability)
]

# Add Google Calendar components if available
if _GOOGLE_CALENDAR_AVAILABLE:
    __all__.extend([
        "GoogleCalendarClient",
        "GoogleCalendarProvider",
        "GoogleCalendarConfig",
    ])

# Version information
__version__ = "0.1.0"
__author__ = "mAIgic Assistant"
__description__ = "Calendar integration package with role-based CalendarClient interface"
