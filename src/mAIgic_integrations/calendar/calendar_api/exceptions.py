"""
Calendar API Exception Classes.

This module defines a comprehensive hierarchy of exceptions for calendar operations.
All exceptions include provider error chaining for detailed error context.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .models import ConflictInfo, TimeSlot


class CalendarAPIError(Exception):
    """
    Base exception for all calendar API errors.

    All calendar-specific exceptions inherit from this base class,
    making it easy to catch all calendar-related errors.
    """

    def __init__(self, message: str, provider_error: Optional[Exception] = None):
        super().__init__(message)
        self.provider_error = provider_error


class CalendarConnectionError(CalendarAPIError):
    """
    Raised when calendar service connection fails.

    This includes network failures, service unavailability,
    and other connection-related issues.
    """
    pass


class CalendarAuthenticationError(CalendarAPIError):
    """
    Raised when calendar authentication fails.

    This includes invalid credentials, expired tokens,
    insufficient permissions, and OAuth flow failures.
    """
    pass


class CalendarPermissionError(CalendarAPIError):
    """
    Raised when operation is not permitted due to insufficient permissions.

    This includes attempts to modify events you don't organize,
    access private calendars, or perform operations your role doesn't allow.
    """

    def __init__(
        self,
        message: str,
        event_id: Optional[str] = None,
        required_permission: Optional[str] = None,
        provider_error: Optional[Exception] = None
    ):
        super().__init__(message, provider_error)
        self.event_id = event_id
        self.required_permission = required_permission


class CalendarEventNotFoundError(CalendarAPIError):
    """
    Raised when requested calendar event cannot be found.

    This includes deleted events, events outside your access scope,
    or invalid event IDs.
    """

    def __init__(
        self,
        message: str,
        event_id: Optional[str] = None,
        provider_error: Optional[Exception] = None
    ):
        super().__init__(message, provider_error)
        self.event_id = event_id


class CalendarSchedulingError(CalendarAPIError):
    """
    Raised when scheduling operations fail due to conflicts or constraints.

    This includes time conflicts, attendee availability issues,
    and scheduling constraint violations.
    """

    def __init__(
        self,
        message: str,
        conflicts: Optional[list["ConflictInfo"]] = None,
        suggested_times: Optional[list["TimeSlot"]] = None,
        provider_error: Optional[Exception] = None
    ):
        super().__init__(message, provider_error)
        self.conflicts = conflicts or []
        self.suggested_times = suggested_times or []


class CalendarTimeError(CalendarAPIError):
    """
    Raised when time-related operations fail.

    This includes timezone conversion errors, invalid date ranges,
    recurring pattern parsing failures, and time zone handling issues.
    """
    pass


class CalendarRecurrenceError(CalendarAPIError):
    """
    Raised when recurring event operations fail.

    This includes invalid recurrence patterns, errors modifying
    recurring series, and recurrence rule parsing failures.
    """

    def __init__(
        self,
        message: str,
        recurrence_pattern: Optional[str] = None,
        provider_error: Optional[Exception] = None
    ):
        super().__init__(message, provider_error)
        self.recurrence_pattern = recurrence_pattern


class CalendarInvitationError(CalendarAPIError):
    """
    Raised when invitation operations fail.

    This includes sending invitations, responding to invitations,
    and attendee management failures.
    """

    def __init__(
        self,
        message: str,
        event_id: Optional[str] = None,
        attendee_email: Optional[str] = None,
        action: Optional[str] = None,
        provider_error: Optional[Exception] = None
    ):
        super().__init__(message, provider_error)
        self.event_id = event_id
        self.attendee_email = attendee_email
        self.action = action


class CalendarValidationError(CalendarAPIError):
    """
    Raised when calendar data validation fails.

    This includes invalid event data, malformed time ranges,
    invalid attendee information, and other data validation failures.
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        invalid_value: Optional[str] = None,
        provider_error: Optional[Exception] = None
    ):
        super().__init__(message, provider_error)
        self.field_name = field_name
        self.invalid_value = invalid_value


class CalendarRateLimitError(CalendarAPIError):
    """
    Raised when calendar API rate limits are exceeded.

    This includes request throttling and quota exceeded errors.
    Clients should implement backoff and retry logic for these errors.
    """

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        provider_error: Optional[Exception] = None
    ):
        super().__init__(message, provider_error)
        self.retry_after = retry_after  # Seconds to wait


class CalendarQuotaExceededError(CalendarAPIError):
    """
    Raised when calendar storage or usage quotas are exceeded.

    This includes calendar storage limits, event count limits,
    and other quota-related failures.
    """
    pass


class CalendarConfigurationError(CalendarAPIError):
    """
    Raised when calendar client configuration is invalid.

    This includes missing required configuration parameters,
    invalid configuration values, and setup failures.
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        provider_error: Optional[Exception] = None
    ):
        super().__init__(message, provider_error)
        self.config_key = config_key


class CalendarSyncError(CalendarAPIError):
    """
    Raised when calendar synchronization fails.

    This includes sync conflicts, version mismatches,
    and other synchronization-related issues.
    """
    pass
