"""
Calendar API Package.

This package contains the abstract interfaces, data models, and exceptions
that define the calendar integration API. All calendar provider implementations
must conform to these interfaces.
"""

# Core data types and models
# Exception hierarchy
from .exceptions import (
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
from .interfaces import (
    CalendarClient,
    CalendarProvider,
)
from .models import (
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
]
