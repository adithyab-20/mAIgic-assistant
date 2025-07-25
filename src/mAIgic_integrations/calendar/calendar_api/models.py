"""
Calendar Data Models.

This module defines all data structures used by the calendar interface.
Follows pydantic-style patterns but uses standard dataclasses for simplicity.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# First, let's add a note about pendulum dependency
# In a real implementation, CalendarDateTime would internally use pendulum.DateTime
# for robust timezone handling. For now, we use standard datetime as a placeholder.


# Enums for calendar operations
class EventStatus(Enum):
    """Event confirmation status."""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class AttendeeStatus(Enum):
    """Attendee response status."""
    NEEDS_ACTION = "needsAction"
    DECLINED = "declined"
    TENTATIVE = "tentative"
    ACCEPTED = "accepted"


class EventPriority(Enum):
    """Event priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class RecurrenceScope(Enum):
    """Scope for recurring event operations."""
    THIS_INSTANCE = "this"
    THIS_AND_FOLLOWING = "following"
    ALL_INSTANCES = "all"


class NotifyOption(Enum):
    """Options for attendee notifications."""
    NONE = "none"
    DEFAULT = "default"
    ALL = "all"


class ConflictResolution(Enum):
    """Options for handling scheduling conflicts."""
    FAIL = "fail"
    WARN = "warn"
    FORCE = "force"


class InvitationActionType(Enum):
    """Types of invitation actions."""
    SEND = "send"
    RESPOND = "respond"
    PROPOSE_TIME = "propose"


# Core data classes

@dataclass
class CalendarDateTime:
    """
    Calendar-specific datetime wrapper that handles timezone complexity.

    Internally uses pendulum but exposes a simple interface.
    All times are normalized to user's timezone by default.
    """
    dt: datetime  # In real implementation, this would be pendulum.DateTime

    @classmethod
    def now(cls, timezone: str = "UTC") -> "CalendarDateTime":
        """Get current time in specified timezone."""
        # Real implementation would use pendulum.now(timezone)
        return cls(datetime.now())

    @classmethod
    def from_iso(cls, iso_string: str) -> "CalendarDateTime":
        """Parse ISO datetime string."""
        # Real implementation would use pendulum.parse
        return cls(datetime.fromisoformat(iso_string.replace('Z', '+00:00')))

    @classmethod
    def all_day(cls, year: int, month: int, day: int) -> "CalendarDateTime":
        """Create all-day event time."""
        return cls(datetime(year, month, day))

    def to_timezone(self, timezone: str) -> "CalendarDateTime":
        """Convert to different timezone."""
        # Real implementation would use pendulum timezone conversion
        return CalendarDateTime(self.dt)

    def add_hours(self, hours: int) -> "CalendarDateTime":
        """Add hours to this time."""
        from datetime import timedelta
        return CalendarDateTime(self.dt + timedelta(hours=hours))

    def to_iso(self) -> str:
        """Convert to ISO format string."""
        return self.dt.isoformat()


@dataclass
class Attendee:
    """Calendar event attendee."""
    email: str
    name: Optional[str] = None
    status: AttendeeStatus = AttendeeStatus.NEEDS_ACTION
    is_optional: bool = False
    is_organizer: bool = False
    comment: Optional[str] = None


@dataclass
class TimeSlot:
    """Time period for events or availability."""
    start: CalendarDateTime
    end: CalendarDateTime

    @property
    def duration_minutes(self) -> int:
        """Duration in minutes."""
        delta = self.end.dt - self.start.dt
        return int(delta.total_seconds() / 60)

    def overlaps_with(self, other: "TimeSlot") -> bool:
        """Check if this slot overlaps with another."""
        return (self.start.dt < other.end.dt and
                self.end.dt > other.start.dt)

    def contains(self, dt: CalendarDateTime) -> bool:
        """Check if datetime falls within this slot."""
        return self.start.dt <= dt.dt < self.end.dt


@dataclass
class Recurrence:
    """Recurring event pattern."""
    frequency: str  # "daily", "weekly", "monthly", "yearly"
    interval: int = 1  # Every N periods
    days_of_week: list[int] = field(default_factory=list)  # 0=Monday
    day_of_month: Optional[int] = None
    month_of_year: Optional[int] = None
    until: Optional[CalendarDateTime] = None
    count: Optional[int] = None  # Number of occurrences
    rrule: Optional[str] = None  # Raw RRULE string for complex patterns


@dataclass
class Event:
    """Complete calendar event representation."""
    # Core identification
    event_id: str
    title: str
    time_slot: TimeSlot

    # Attendees and organization
    organizer: Optional[Attendee] = None
    attendees: list[Attendee] = field(default_factory=list)

    # Event properties
    description: str = ""
    location: str = ""
    status: EventStatus = EventStatus.CONFIRMED
    priority: EventPriority = EventPriority.NORMAL

    # Recurrence
    recurrence: Optional[Recurrence] = None

    # Calendar metadata
    calendar_id: str = "primary"
    created_time: Optional[CalendarDateTime] = None
    updated_time: Optional[CalendarDateTime] = None

    # Provider-specific data
    provider_data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Auto-generate event_id if not provided."""
        if not self.event_id:
            import uuid
            self.event_id = str(uuid.uuid4())

    @property
    def is_recurring(self) -> bool:
        """Check if this is a recurring event."""
        return self.recurrence is not None

    @property
    def is_all_day(self) -> bool:
        """Check if this is an all-day event."""
        # Simple heuristic: all-day if exactly 24 hours and starts at midnight
        return (self.time_slot.duration_minutes == 1440 and
                self.time_slot.start.dt.hour == 0 and
                self.time_slot.start.dt.minute == 0)

    @property
    def duration_minutes(self) -> int:
        """Event duration in minutes."""
        return self.time_slot.duration_minutes


@dataclass
class EventChanges:
    """Changes to apply to an existing event."""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    time_slot: Optional[TimeSlot] = None
    attendees: Optional[list[Attendee]] = None
    status: Optional[EventStatus] = None
    priority: Optional[EventPriority] = None
    recurrence: Optional[Recurrence] = None


@dataclass
class ConflictInfo:
    """Information about scheduling conflicts."""
    conflict_type: str  # "time_conflict", "attendee_busy", "double_booking"
    description: str
    conflicting_event_id: Optional[str] = None
    affected_attendees: list[str] = field(default_factory=list)  # Email addresses
    severity: str = "medium"  # "low", "medium", "high"
    suggestion: Optional[str] = None


@dataclass
class PermissionInfo:
    """Permissions and capabilities for an event or calendar."""
    can_read: bool = True
    can_edit: bool = False
    can_delete: bool = False
    can_invite_others: bool = False
    can_modify_attendees: bool = False
    can_see_attendees: bool = True
    is_organizer: bool = False
    role: str = "reader"  # "reader", "writer", "owner"
    reason: Optional[str] = None  # Why certain permissions are denied


@dataclass
class UpdateResult:
    """Result of a calendar update operation."""
    success: bool
    updated_event: Optional[Event] = None
    conflicts: list[ConflictInfo] = field(default_factory=list)
    affected_attendees: list[Attendee] = field(default_factory=list)
    permissions: Optional[PermissionInfo] = None
    error_message: Optional[str] = None
    provider_response: dict[str, Any] = field(default_factory=dict)


@dataclass
class InvitationResponse:
    """Response to a calendar invitation."""
    status: AttendeeStatus
    comment: Optional[str] = None
    propose_new_time: Optional[TimeSlot] = None


@dataclass
class BatchUpdateResult:
    """Result of batch event operations."""
    successful_updates: list[UpdateResult]
    failed_updates: list[tuple[str, str]]  # (event_id, error_message)
    total_processed: int = field(init=False)
    total_successful: int = field(init=False)
    total_failed: int = field(init=False)

    def __post_init__(self) -> None:
        """Calculate totals."""
        self.total_successful = len(self.successful_updates)
        self.total_failed = len(self.failed_updates)
        self.total_processed = self.total_successful + self.total_failed


@dataclass
class AvailabilityQuery:
    """Query for finding available time slots."""
    time_range: TimeSlot
    duration_minutes: int
    attendees: list[str] = field(default_factory=list)  # Email addresses
    buffer_minutes: int = 0  # Buffer between meetings
    working_hours_only: bool = True
    exclude_weekends: bool = True
    preferred_times: list[TimeSlot] = field(default_factory=list)


@dataclass
class AvailableSlot:
    """Available time slot with confidence score."""
    time_slot: TimeSlot
    confidence: float  # 0.0-1.0 confidence this slot will work
    attendee_conflicts: list[str] = field(default_factory=list)  # Who has conflicts


@dataclass
class CalendarInfo:
    """Information about a calendar."""
    calendar_id: str
    name: str
    description: str = ""
    timezone: str = "UTC"
    is_primary: bool = False
    permissions: Optional[PermissionInfo] = None
    color: Optional[str] = None
    provider_type: str = "unknown"


@dataclass
class CalendarSearchQuery:
    """Query parameters for searching calendar events."""
    query: Optional[str] = None  # Text search
    time_range: Optional[TimeSlot] = None
    attendee_email: Optional[str] = None
    organizer_email: Optional[str] = None
    calendar_ids: list[str] = field(default_factory=list)
    event_status: Optional[EventStatus] = None
    include_declined: bool = False
    max_results: int = 100


@dataclass
class CalendarSearchResult:
    """Calendar event search results."""
    events: list[Event]
    total_count: int
    has_more: bool
    next_page_token: Optional[str] = None


# Type aliases for common use cases
EventList = list[Event]
AttendeeList = list[Attendee]
ConflictList = list[ConflictInfo]
