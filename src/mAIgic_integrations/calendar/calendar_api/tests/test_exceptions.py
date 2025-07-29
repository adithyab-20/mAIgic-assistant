"""
Tests for calendar API exceptions.

This module tests the exception hierarchy to ensure proper inheritance,
constructor functionality, and error handling patterns.
"""

import pytest

from ..exceptions import (
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


class TestCalendarAPIError:
    """Test base CalendarAPIError exception."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = CalendarAPIError("Test error message")
        assert str(error) == "Test error message"
        assert error.provider_error is None

    def test_error_with_provider_error(self):
        """Test error with original provider exception."""
        original = ValueError("Original error")
        error = CalendarAPIError("Wrapped error", provider_error=original)
        assert str(error) == "Wrapped error"
        assert error.provider_error is original

    def test_error_inheritance(self):
        """Test that CalendarAPIError inherits from Exception."""
        error = CalendarAPIError("Test error")
        assert isinstance(error, Exception)


class TestSpecificExceptions:
    """Test specific calendar exception types."""

    def test_connection_error(self):
        """Test CalendarConnectionError."""
        error = CalendarConnectionError("Cannot connect to calendar service")
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Cannot connect to calendar service"

    def test_authentication_error(self):
        """Test CalendarAuthenticationError."""
        error = CalendarAuthenticationError("Invalid credentials")
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Invalid credentials"

    def test_permission_error(self):
        """Test CalendarPermissionError with additional fields."""
        error = CalendarPermissionError(
            "Access denied",
            event_id="event-123",
            required_permission="edit_events"
        )
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Access denied"
        assert error.event_id == "event-123"
        assert error.required_permission == "edit_events"

    def test_event_not_found_error(self):
        """Test CalendarEventNotFoundError with event ID."""
        error = CalendarEventNotFoundError("Event not found", event_id="event-123")
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Event not found"
        assert error.event_id == "event-123"

    def test_scheduling_error(self):
        """Test CalendarSchedulingError with conflicts."""
        conflicts = ["Time conflict with existing meeting"]
        suggested_times = ["2024-01-15T15:00:00Z"]
        error = CalendarSchedulingError(
            "Scheduling conflict",
            conflicts=conflicts,
            suggested_times=suggested_times
        )
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Scheduling conflict"
        assert error.conflicts == conflicts
        assert error.suggested_times == suggested_times

    def test_time_error(self):
        """Test CalendarTimeError."""
        error = CalendarTimeError("Invalid timezone")
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Invalid timezone"

    def test_recurrence_error(self):
        """Test CalendarRecurrenceError with pattern."""
        pattern = "FREQ=WEEKLY;BYDAY=MO,WE,FR"
        error = CalendarRecurrenceError("Invalid recurrence pattern", recurrence_pattern=pattern)
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Invalid recurrence pattern"
        assert error.recurrence_pattern == pattern

    def test_invitation_error(self):
        """Test CalendarInvitationError with attendee details."""
        error = CalendarInvitationError(
            "Failed to send invitation",
            event_id="event-123",
            attendee_email="alice@example.com",
            action="send"
        )
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Failed to send invitation"
        assert error.event_id == "event-123"
        assert error.attendee_email == "alice@example.com"
        assert error.action == "send"

    def test_validation_error(self):
        """Test CalendarValidationError with field details."""
        error = CalendarValidationError(
            "Invalid email format",
            field_name="attendee_email",
            invalid_value="not-an-email"
        )
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Invalid email format"
        assert error.field_name == "attendee_email"
        assert error.invalid_value == "not-an-email"

    def test_rate_limit_error(self):
        """Test CalendarRateLimitError with retry information."""
        error = CalendarRateLimitError("Rate limit exceeded", retry_after=60)
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Rate limit exceeded"
        assert error.retry_after == 60

    def test_quota_exceeded_error(self):
        """Test CalendarQuotaExceededError."""
        error = CalendarQuotaExceededError("Storage quota exceeded")
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Storage quota exceeded"

    def test_configuration_error(self):
        """Test CalendarConfigurationError with config key."""
        error = CalendarConfigurationError("Missing configuration", config_key="credentials_path")
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Missing configuration"
        assert error.config_key == "credentials_path"

    def test_sync_error(self):
        """Test CalendarSyncError."""
        error = CalendarSyncError("Synchronization failed")
        assert isinstance(error, CalendarAPIError)
        assert str(error) == "Synchronization failed"


class TestExceptionConstructorDefaults:
    """Test exception constructor default values."""

    def test_permission_error_defaults(self):
        """Test CalendarPermissionError with default values."""
        error = CalendarPermissionError("Access denied")
        assert error.event_id is None
        assert error.required_permission is None
        assert error.provider_error is None

    def test_event_not_found_defaults(self):
        """Test CalendarEventNotFoundError with default values."""
        error = CalendarEventNotFoundError("Event not found")
        assert error.event_id is None
        assert error.provider_error is None

    def test_scheduling_error_defaults(self):
        """Test CalendarSchedulingError with default values."""
        error = CalendarSchedulingError("Scheduling conflict")
        assert error.conflicts == []  # Should default to empty list
        assert error.suggested_times == [] # Should default to empty list
        assert error.provider_error is None

    def test_recurrence_error_defaults(self):
        """Test CalendarRecurrenceError with default values."""
        error = CalendarRecurrenceError("Invalid recurrence")
        assert error.recurrence_pattern is None
        assert error.provider_error is None

    def test_invitation_error_defaults(self):
        """Test CalendarInvitationError with default values."""
        error = CalendarInvitationError("Invitation failed")
        assert error.event_id is None
        assert error.attendee_email is None
        assert error.action is None
        assert error.provider_error is None

    def test_validation_error_defaults(self):
        """Test CalendarValidationError with default values."""
        error = CalendarValidationError("Validation failed")
        assert error.field_name is None
        assert error.invalid_value is None
        assert error.provider_error is None

    def test_rate_limit_error_defaults(self):
        """Test CalendarRateLimitError with default values."""
        error = CalendarRateLimitError("Rate limited")
        assert error.retry_after is None
        assert error.provider_error is None

    def test_configuration_error_defaults(self):
        """Test CalendarConfigurationError with default values."""
        error = CalendarConfigurationError("Config error")
        assert error.config_key is None
        assert error.provider_error is None


class TestExceptionWithProviderError:
    """Test exceptions with provider error context."""

    def test_all_exceptions_accept_provider_error(self):
        """Test that all exceptions can accept provider_error parameter."""
        original_error = ConnectionError("Network failure")

        exceptions_to_test = [
            (CalendarConnectionError, "Connection failed"),
            (CalendarAuthenticationError, "Auth failed"),
            (CalendarPermissionError, "Permission denied"),
            (CalendarEventNotFoundError, "Not found"),
            (CalendarSchedulingError, "Conflict"),
            (CalendarTimeError, "Time error"),
            (CalendarRecurrenceError, "Recurrence error"),
            (CalendarInvitationError, "Invitation error"),
            (CalendarValidationError, "Validation error"),
            (CalendarRateLimitError, "Rate limited"),
            (CalendarQuotaExceededError, "Quota exceeded"),
            (CalendarConfigurationError, "Config error"),
            (CalendarSyncError, "Sync error"),
        ]

        for exception_class, message in exceptions_to_test:
            error = exception_class(message, provider_error=original_error)
            assert error.provider_error is original_error
            assert str(error) == message

    def test_provider_error_chain(self):
        """Test chaining provider errors."""
        network_error = ConnectionError("Network down")

        # Chain multiple provider errors
        error = CalendarConnectionError("Service unavailable", provider_error=network_error)
        chained_error = CalendarAPIError("High level error", provider_error=error)

        assert chained_error.provider_error is error
        assert error.provider_error is network_error


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all calendar exceptions inherit from CalendarAPIError."""
        exception_classes = [
            CalendarConnectionError,
            CalendarAuthenticationError,
            CalendarPermissionError,
            CalendarEventNotFoundError,
            CalendarSchedulingError,
            CalendarTimeError,
            CalendarRecurrenceError,
            CalendarInvitationError,
            CalendarValidationError,
            CalendarRateLimitError,
            CalendarQuotaExceededError,
            CalendarConfigurationError,
            CalendarSyncError,
        ]

        for exc_class in exception_classes:
            assert issubclass(exc_class, CalendarAPIError)
            assert issubclass(exc_class, Exception)

    def test_base_inherits_from_exception(self):
        """Test that CalendarAPIError inherits from Exception."""
        assert issubclass(CalendarAPIError, Exception)

    def test_can_catch_with_base_exception(self):
        """Test that specific exceptions can be caught with base exception."""
        try:
            raise CalendarConnectionError("Connection failed")
        except CalendarAPIError as e:
            assert isinstance(e, CalendarConnectionError)
            assert isinstance(e, CalendarAPIError)
            assert isinstance(e, Exception)

        try:
            raise CalendarPermissionError("Access denied")
        except CalendarAPIError as e:
            assert isinstance(e, CalendarPermissionError)
            assert isinstance(e, CalendarAPIError)


class TestExceptionUsagePatterns:
    """Test common exception usage patterns."""

    def test_exception_with_all_fields(self):
        """Test exception with all possible fields populated."""
        original = ValueError("Provider error")
        error = CalendarPermissionError(
            "You don't have permission to edit this event",
            event_id="event-123",
            required_permission="write",
            provider_error=original
        )

        assert str(error) == "You don't have permission to edit this event"
        assert error.event_id == "event-123"
        assert error.required_permission == "write"
        assert error.provider_error is original

    def test_exception_context_manager(self):
        """Test using exceptions in context managers."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise CalendarConnectionError("Connection failed", provider_error=e) from e
        except CalendarAPIError as calendar_error:
            assert isinstance(calendar_error, CalendarConnectionError)
            assert isinstance(calendar_error.provider_error, ValueError)
            assert str(calendar_error.provider_error) == "Original error"

    def test_multiple_exception_catch(self):
        """Test catching multiple exception types."""
        def test_operation(error_type):
            if error_type == "connection":
                raise CalendarConnectionError("Connection failed")
            elif error_type == "auth":
                raise CalendarAuthenticationError("Auth failed")
            elif error_type == "permission":
                raise CalendarPermissionError("Permission denied")
            else:
                raise CalendarAPIError("Generic error")

        # Test catching specific exceptions
        for error_type in ["connection", "auth", "permission", "generic"]:
            with pytest.raises(CalendarAPIError):
                test_operation(error_type)

        # Test catching specific types
        with pytest.raises(CalendarConnectionError):
            test_operation("connection")

        with pytest.raises(CalendarAuthenticationError):
            test_operation("auth")

        with pytest.raises(CalendarPermissionError):
            test_operation("permission")

    def test_exception_message_formatting(self):
        """Test exception message formatting."""
        # Test basic message
        error = CalendarAPIError("Simple message")
        assert str(error) == "Simple message"

        # Test message with additional context
        error = CalendarPermissionError(
            "Access denied for event 'Team Meeting'",
            event_id="meeting-123",
            required_permission="edit"
        )
        assert "Team Meeting" in str(error)
        assert error.event_id == "meeting-123"
        assert error.required_permission == "edit"

    def test_exception_serialization(self):
        """Test that exceptions can be properly represented."""
        error = CalendarSchedulingError(
            "Double booking detected",
            conflicts=["meeting-1", "meeting-2"]
        )

        # Test string representation
        error_str = str(error)
        assert "Double booking detected" == error_str

        # Test that additional data is accessible
        assert len(error.conflicts) == 2
        assert "meeting-1" in error.conflicts
