# mAIgic Calendar API

Abstract interfaces and data models for calendar integration. This package provides provider-agnostic calendar operations designed for AI assistant use cases.

## Overview

The Calendar API defines a clean interface for calendar operations with:
- **Role-based methods** preventing permission errors
- **Rich data models** for AI context understanding  
- **Comprehensive error handling** with specific exception types
- **Time abstraction** hiding timezone complexity

## Installation

This is an interface-only package with zero dependencies:

```bash
# Installed automatically with calendar integrations
uv sync --extra calendar
```

## Core Interfaces

### CalendarClient

The main interface for calendar operations with role-aware methods:

```python
from mAIgic_integrations.calendar.calendar_api import CalendarClient

class MyCalendarClient(CalendarClient):
    async def get_events(self, time_range: TimeSlot) -> EventList:
        # Implement provider-specific event retrieval
        pass
    
    async def create_my_event(self, event: Event) -> UpdateResult:
        # Implement provider-specific event creation
        # Only for events where user is organizer
        pass
    
    async def respond_to_invitation(self, event_id: str, response: InvitationResponse) -> UpdateResult:
        # Implement provider-specific invitation response
        # For events where user is attendee
        pass
```

### CalendarProvider

Factory interface for creating clients:

```python
from mAIgic_integrations.calendar.calendar_api import CalendarProvider

class MyCalendarProvider(CalendarProvider):
    async def create_client(self, config: dict) -> CalendarClient:
        # Create provider-specific client instance
        pass
    
    def validate_config(self, config: dict) -> bool:
        # Validate configuration for this provider
        pass
```

## Role-Based Method Design

The interface separates organizer and attendee operations to prevent permission errors:

### Organizer Methods (requires organizer permissions)
- `create_my_event()` - Create events you organize
- `update_my_event()` - Modify events you organize  
- `delete_my_event()` - Cancel events you organize
- `batch_create_events()` - Create multiple events atomically
- `batch_update_events()` - Update multiple events atomically

### Attendee Methods (requires attendee permissions)
- `respond_to_invitation()` - Accept/decline/tentative responses
- `suggest_reschedule()` - Propose alternative times

### Universal Methods (read-only or minimal permissions)
- `get_events()` - Retrieve events in time range
- `find_available_slots()` - Find free time slots
- `search_events()` - Search events by criteria
- `get_event()` - Get single event details
- `get_event_permissions()` - Check permissions for event
- `get_calendars()` - List available calendars

## Data Models

### Core Types

#### Event
Complete calendar event representation:
```python
@dataclass
class Event:
    event_id: str
    title: str
    time_slot: TimeSlot
    organizer: Attendee
    attendees: AttendeeList = field(default_factory=list)
    description: str = ""
    location: str = ""
    status: EventStatus = EventStatus.CONFIRMED
    priority: EventPriority = EventPriority.NORMAL
    recurrence: Optional[Recurrence] = None
    
    @property
    def is_recurring(self) -> bool: ...
    @property  
    def is_all_day(self) -> bool: ...
    @property
    def duration_minutes(self) -> int: ...
```

#### TimeSlot
Time period with smart utilities:
```python
@dataclass  
class TimeSlot:
    start: CalendarDateTime
    end: CalendarDateTime
    
    @property
    def duration_minutes(self) -> int: ...
    
    def overlaps_with(self, other: TimeSlot) -> bool: ...
    def contains(self, dt: CalendarDateTime) -> bool: ...
```

#### CalendarDateTime
Timezone-aware time abstraction:
```python
@dataclass
class CalendarDateTime:
    dt: datetime  # Internal pendulum.DateTime
    
    @classmethod
    def now(cls, timezone: str = "UTC") -> CalendarDateTime: ...
    
    @classmethod  
    def from_iso(cls, iso_string: str) -> CalendarDateTime: ...
    
    def to_timezone(self, timezone: str) -> CalendarDateTime: ...
    def add_hours(self, hours: int) -> CalendarDateTime: ...
    def to_iso(self) -> str: ...
```

### Request/Response Types

#### UpdateResult
Rich result information for modifications:
```python
@dataclass
class UpdateResult:
    success: bool
    updated_event: Optional[Event] = None
    conflicts: ConflictList = field(default_factory=list)
    permissions: Optional[PermissionInfo] = None
    affected_attendees: AttendeeList = field(default_factory=list)
    provider_response: dict = field(default_factory=dict)
```

#### AvailabilityQuery
Smart availability search parameters:
```python
@dataclass
class AvailabilityQuery:
    time_range: TimeSlot
    duration_minutes: int
    attendees: AttendeeList = field(default_factory=list)
    preferred_times: List[TimeSlot] = field(default_factory=list)
    minimum_gap_minutes: int = 15
    exclude_weekends: bool = True
    working_hours_only: bool = True
```

## Exception Hierarchy

Comprehensive error handling for all calendar scenarios:

```python
# Base exception
class CalendarAPIError(Exception):
    def __init__(
        self, 
        message: str, 
        provider_error: Optional[Exception] = None
    ): ...

# Specific exceptions
class CalendarConnectionError(CalendarAPIError): ...
class CalendarAuthenticationError(CalendarAPIError): ...  
class CalendarPermissionError(CalendarAPIError):
    def __init__(
        self,
        message: str,
        event_id: Optional[str] = None,
        required_permission: Optional[str] = None,
        provider_error: Optional[Exception] = None,
    ): ...

class CalendarSchedulingError(CalendarAPIError):
    def __init__(
        self,
        message: str,
        conflicts: ConflictList = None,
        suggested_times: List[TimeSlot] = None,
        provider_error: Optional[Exception] = None,
    ): ...
```

## Usage Patterns

### Basic Event Operations
```python
async with client:
    # Get schedule context
    today = CalendarDateTime.now()
    tomorrow = today.add_hours(24)
    events = await client.get_events(TimeSlot(today, tomorrow))
    
    # Create new meeting (as organizer)
    meeting = Event(
        event_id="",
        title="Project Review",
        time_slot=TimeSlot(today.add_hours(2), today.add_hours(3)),
        organizer=Attendee(email="me@example.com"),
        attendees=[Attendee(email="colleague@example.com")]
    )
    result = await client.create_my_event(meeting)
    
    # Handle conflicts
    if not result.success and result.conflicts:
        print(f"Conflicts found: {len(result.conflicts)}")
        for conflict in result.conflicts:
            print(f"- {conflict.description}")
```

### Invitation Handling
```python
# Respond to meeting invitation (as attendee)
response = InvitationResponse(
    status=AttendeeStatus.ACCEPTED,
    comment="Looking forward to it!"
)
await client.respond_to_invitation("meeting-123", response)

# Suggest alternative time
alternative = TimeSlot(
    start=today.add_hours(3),
    end=today.add_hours(4)
)
await client.suggest_reschedule("meeting-123", alternative)
```

### Availability Finding
```python
# Find free time for team meeting
query = AvailabilityQuery(
    time_range=TimeSlot(today, today.add_hours(8)),
    duration_minutes=60,
    attendees=[
        Attendee(email="alice@example.com"),
        Attendee(email="bob@example.com")
    ]
)
available_slots = await client.find_available_slots(query)

for slot in available_slots:
    print(f"Available: {slot.time_slot} (confidence: {slot.confidence})")
```

## Testing

The package includes comprehensive unit tests:

```bash
# Run all tests
uv run pytest src/mAIgic_integrations/calendar/calendar_api/tests/ -v

# Test coverage
uv run pytest src/mAIgic_integrations/calendar/calendar_api/tests/ --cov=calendar_api --cov-report=term-missing

# Test specific components
uv run pytest src/mAIgic_integrations/calendar/calendar_api/tests/test_models.py -v
uv run pytest src/mAIgic_integrations/calendar/calendar_api/tests/test_interfaces.py -v
uv run pytest src/mAIgic_integrations/calendar/calendar_api/tests/test_exceptions.py -v
```

## Implementation Guide

To implement a calendar provider:

1. **Inherit from CalendarClient**:
   ```python
   class MyCalendarClient(CalendarClient):
       async def __aenter__(self): ...
       async def __aexit__(self, exc_type, exc_val, exc_tb): ...
       # Implement all abstract methods
   ```

2. **Handle Provider-Specific Configuration**:
   ```python
   class MyCalendarProvider(CalendarProvider):
       def validate_config(self, config: dict) -> bool:
           return "api_key" in config and "endpoint" in config
   ```

3. **Map Provider Errors to Calendar Exceptions**:
   ```python
   try:
       response = await provider_api.create_event(event_data)
   except ProviderConnectionError as e:
       raise CalendarConnectionError("Connection failed", provider_error=e)
   except ProviderAuthError as e:
       raise CalendarAuthenticationError("Auth failed", provider_error=e)
   ```

4. **Test Implementation**:
   ```python
   # Use interface compliance tests
   class TestMyCalendarClient(TestCase):
       async def test_interface_compliance(self):
           client = MyCalendarClient(config)
           # Verify all methods work as expected
   ```

This API provides a solid foundation for building calendar integrations that work seamlessly with AI assistants requiring rich calendar context and intelligent scheduling capabilities. 