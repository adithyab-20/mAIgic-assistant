"""
Calendar Client Interfaces.

This module defines the abstract interfaces for calendar operations. The design
emphasizes role-based permissions to prevent common calendar mistakes and provides
rich information for AI decision-making.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from .models import (
    AvailabilityQuery,
    AvailableSlot,
    BatchUpdateResult,
    CalendarInfo,
    CalendarSearchQuery,
    CalendarSearchResult,
    Event,
    EventChanges,
    InvitationResponse,
    NotifyOption,
    PermissionInfo,
    TimeSlot,
    UpdateResult,
)


class CalendarClient(ABC):
    """
    Calendar interface for AI personal assistants.

    Designed for AI assistants that need to:
    - Understand user's schedule and availability context
    - Find optimal times for meetings and events
    - Handle calendar modifications with proper role-based permissions
    - Provide rich context for scheduling decisions

    Uses role-based methods to match user mental models and prevent permission errors:
    - create_my_event/update_my_event for events you organize
    - respond_to_invitation for events others organize
    - Explicit permission handling throughout

    Uses async context manager pattern for automatic connection management.

    Example:
        async with GoogleCalendarClient(config) as client:
            # Get context (universal access)
            events = await client.get_events(time_range)
            available = await client.find_available_slots(query)

            # Organize events (role: organizer)
            result = await client.create_my_event(event)
            await client.update_my_event(event_id, changes)

            # Respond to invitations (role: attendee)
            await client.respond_to_invitation(event_id, response)
    """

    # Context Manager Protocol
    @abstractmethod
    async def __aenter__(self) -> "CalendarClient":
        """Enter async context and connect to calendar service."""
        pass  # pragma: no cover

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context and disconnect from calendar service."""
        pass  # pragma: no cover

    # Universal Methods (read-only or minimal permissions)

    @abstractmethod
    async def get_events(
        self,
        time_range: TimeSlot,
        calendar_ids: Optional[list[str]] = None,
        include_declined: bool = False
    ) -> list[Event]:
        """
        Get events in time range for AI context analysis.

        This is the primary method AI assistants use to understand
        what's happening in the user's schedule.

        Args:
            time_range: Time period to search
            calendar_ids: Specific calendars to search (None = primary)
            include_declined: Include events user declined

        Returns:
            List of events in the time range

        Raises:
            CalendarConnectionError: If calendar service unavailable
            CalendarAuthenticationError: If authentication fails
            CalendarTimeError: If time_range is invalid
        """
        pass  # pragma: no cover

    @abstractmethod
    async def find_available_slots(
        self,
        query: AvailabilityQuery
    ) -> list[AvailableSlot]:
        """
        Find available time slots for scheduling new events.

        Critical for AI assistants to suggest optimal meeting times
        considering all attendees' availability.

        Args:
            query: Availability search parameters

        Returns:
            List of available time slots with confidence scores

        Raises:
            CalendarConnectionError: If calendar service unavailable
            CalendarTimeError: If query time range is invalid
            CalendarValidationError: If query parameters are invalid
        """
        pass  # pragma: no cover

    @abstractmethod
    async def search_events(
        self,
        query: CalendarSearchQuery
    ) -> CalendarSearchResult:
        """
        Search events by text, attendees, or other criteria.

        Enables AI assistants to find relevant past/future events
        for context understanding and scheduling decisions.

        Args:
            query: Search parameters

        Returns:
            Search results with pagination info

        Raises:
            CalendarConnectionError: If calendar service unavailable
            CalendarValidationError: If search query is invalid
        """
        pass  # pragma: no cover

    @abstractmethod
    async def get_event(
        self,
        event_id: str
    ) -> Event:
        """
        Get detailed information about a specific event.

        Args:
            event_id: Calendar event identifier

        Returns:
            Complete event information

        Raises:
            CalendarEventNotFoundError: If event doesn't exist
            CalendarPermissionError: If no read access to event
            CalendarConnectionError: If calendar service unavailable
        """
        pass  # pragma: no cover

    # Organizer Methods (requires organizer permissions)

    @abstractmethod
    async def create_my_event(
        self,
        event: Event,
        calendar_id: Optional[str] = None,
        notify_attendees: NotifyOption = NotifyOption.DEFAULT
    ) -> UpdateResult:
        """
        Create new event that I organize.

        Use this method when creating events where you are the organizer.
        Automatically handles attendee invitations based on notify_attendees setting.

        Args:
            event: Event details (event_id will be auto-generated)
            calendar_id: Which calendar to create in (None = primary)
            notify_attendees: How to handle attendee notifications

        Returns:
            Result with success status and conflict/permission details

        Raises:
            CalendarPermissionError: If insufficient permissions for calendar
            CalendarSchedulingError: If time conflicts with existing events
            CalendarValidationError: If event data is invalid
            CalendarConnectionError: If calendar service unavailable
        """
        pass  # pragma: no cover

    @abstractmethod
    async def update_my_event(
        self,
        event_id: str,
        changes: EventChanges,
        notify_attendees: NotifyOption = NotifyOption.DEFAULT
    ) -> UpdateResult:
        """
        Update event that I organize.

        Use this method to modify events where you are the organizer.
        Provides rich conflict and attendee impact information for user decisions.

        Args:
            event_id: Event to update
            changes: What fields to modify
            notify_attendees: How to handle attendee notifications

        Returns:
            Result with update details and impact analysis

        Raises:
            CalendarEventNotFoundError: If event doesn't exist
            CalendarPermissionError: If not organizer of event
            CalendarSchedulingError: If changes create conflicts
            CalendarValidationError: If changes are invalid
        """
        pass  # pragma: no cover

    @abstractmethod
    async def delete_my_event(
        self,
        event_id: str,
        notify_attendees: NotifyOption = NotifyOption.DEFAULT,
        cancellation_message: Optional[str] = None
    ) -> UpdateResult:
        """
        Delete event that I organize.

        Use this method to cancel/delete events where you are the organizer.
        Automatically handles attendee notifications.

        Args:
            event_id: Event to delete
            notify_attendees: How to handle attendee notifications
            cancellation_message: Optional message to attendees

        Returns:
            Result with deletion confirmation and attendee notification info

        Raises:
            CalendarEventNotFoundError: If event doesn't exist
            CalendarPermissionError: If not organizer of event
            CalendarConnectionError: If calendar service unavailable
        """
        pass  # pragma: no cover

    # Attendee Methods (requires attendee permissions)

    @abstractmethod
    async def respond_to_invitation(
        self,
        event_id: str,
        response: InvitationResponse
    ) -> UpdateResult:
        """
        Respond to calendar invitation as attendee.

        Use this method to accept/decline/tentatively accept invitations
        to events organized by others.

        Args:
            event_id: Event to respond to
            response: Accept/decline/tentative with optional comment

        Returns:
            Result with response confirmation

        Raises:
            CalendarEventNotFoundError: If event doesn't exist
            CalendarInvitationError: If not invited to event
            CalendarPermissionError: If cannot respond (e.g., already responded)
            CalendarConnectionError: If calendar service unavailable
        """
        pass  # pragma: no cover

    @abstractmethod
    async def suggest_reschedule(
        self,
        event_id: str,
        proposed_time: TimeSlot,
        message: Optional[str] = None
    ) -> UpdateResult:
        """
        Suggest reschedule as attendee (if provider supports).

        Use this method to propose alternative times for events
        organized by others. Not all providers support this feature.

        Args:
            event_id: Event to suggest reschedule for
            proposed_time: Alternative time slot
            message: Optional message to organizer

        Returns:
            Result with suggestion status

        Raises:
            CalendarEventNotFoundError: If event doesn't exist
            CalendarPermissionError: If not attendee or feature unsupported
            CalendarTimeError: If proposed time is invalid
            CalendarConnectionError: If calendar service unavailable
        """
        pass  # pragma: no cover

    # Batch Operations (atomic operations for complex scenarios)

    @abstractmethod
    async def batch_create_events(
        self,
        events: list[Event],
        calendar_id: Optional[str] = None,
        notify_attendees: NotifyOption = NotifyOption.DEFAULT
    ) -> BatchUpdateResult:
        """
        Create multiple events atomically.

        All events succeed or all fail together. Optimizes network calls
        and provides transaction-like behavior for complex scheduling operations.

        Args:
            events: Events to create
            calendar_id: Which calendar to create in (None = primary)
            notify_attendees: How to handle attendee notifications

        Returns:
            Batch result with individual success/failure details

        Raises:
            CalendarPermissionError: If insufficient permissions
            CalendarConnectionError: If calendar service unavailable
        """
        pass  # pragma: no cover

    @abstractmethod
    async def batch_update_events(
        self,
        updates: list[tuple[str, EventChanges]],  # (event_id, changes)
        notify_attendees: NotifyOption = NotifyOption.DEFAULT
    ) -> BatchUpdateResult:
        """
        Update multiple events atomically.

        All updates succeed or all fail together. Critical for complex
        schedule reorganizations where related events must all change.

        Args:
            updates: List of (event_id, changes) tuples
            notify_attendees: How to handle attendee notifications

        Returns:
            Batch result with individual success/failure details

        Raises:
            CalendarPermissionError: If insufficient permissions for any event
            CalendarConnectionError: If calendar service unavailable
        """
        pass  # pragma: no cover

    # Permission and Information Methods

    @abstractmethod
    async def get_event_permissions(
        self,
        event_id: str
    ) -> PermissionInfo:
        """
        Check what operations are allowed on this event.

        Provides detailed permission information to prevent errors
        and inform user about what actions are possible.

        Args:
            event_id: Event to check permissions for

        Returns:
            Detailed permission information

        Raises:
            CalendarEventNotFoundError: If event doesn't exist
            CalendarConnectionError: If calendar service unavailable
        """
        pass  # pragma: no cover

    @abstractmethod
    async def get_calendars(self) -> list[CalendarInfo]:
        """
        Get available calendars for this user.

        Returns information about calendars the user can read/write,
        including permissions and metadata.

        Returns:
            List of available calendars with permissions

        Raises:
            CalendarConnectionError: If calendar service unavailable
            CalendarAuthenticationError: If authentication fails
        """
        pass  # pragma: no cover


class CalendarProvider(ABC):
    """
    Factory for creating calendar clients.

    Each calendar provider (Google, Outlook, etc.) implements this
    interface to provide configuration validation and client creation.
    """

    @abstractmethod
    async def create_client(self, config: dict[str, Any]) -> CalendarClient:
        """
        Create and configure a calendar client.

        Args:
            config: Provider-specific configuration

        Returns:
            Configured calendar client

        Raises:
            CalendarConfigurationError: If config is invalid
        """
        pass  # pragma: no cover

    @abstractmethod
    def validate_config(self, config: dict[str, Any]) -> bool:
        """
        Validate configuration for this provider.

        Args:
            config: Configuration to validate

        Returns:
            True if valid, False otherwise
        """
        pass  # pragma: no cover

    @abstractmethod
    def get_required_config_keys(self) -> list[str]:
        """
        Get list of required configuration keys for this provider.

        Returns:
            List of required configuration keys
        """
        pass  # pragma: no cover

    @abstractmethod
    def get_optional_config_keys(self) -> list[str]:
        """Get list of optional configuration keys."""
        pass  # pragma: no cover

    @abstractmethod
    def get_config_description(self, key: str) -> str:
        """Get human-readable description of a configuration key."""
        pass  # pragma: no cover
