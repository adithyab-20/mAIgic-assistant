# mAIgic Calendar Integration

Complete calendar integration capabilities with role-based permissions and intelligent scheduling support for AI assistants.

## Overview

This component provides:
- **Calendar API** (`calendar_api/`) - Abstract interfaces and type definitions
- **Future Implementations** - Google Calendar, Outlook, and other providers

## Installation

Install the calendar component as part of mAIgic Assistant:

```bash
# Install with calendar capabilities
uv sync --extra calendar

# Or using pip
pip install "maigic-assistant[calendar]"
```

## Quick Start

```python
from mAIgic_integrations.calendar import (
    CalendarClient,
    Event,
    TimeSlot,
    CalendarDateTime,
    AttendeeStatus,
    InvitationResponse
)


## Key Features

### Role-Based Interface Design
- **Organizer Methods**: `create_my_event()`, `update_my_event()`, `delete_my_event()`
- **Attendee Methods**: `respond_to_invitation()`, `suggest_reschedule()`
- **Permission-Aware**: Prevents common calendar permission errors

### AI-Friendly Context
- **Rich Event Data**: Complete event representation with attendees, recurrence, conflicts
- **Availability Queries**: Smart slot finding with confidence scores
- **Conflict Detection**: Detailed conflict information for intelligent resolution
- **Batch Operations**: Atomic operations for complex schedule changes

### Time Handling
- **CalendarDateTime**: Timezone-aware wrapper hiding complexity
- **TimeSlot**: Smart overlap detection and duration calculation
- **Recurrence**: Full recurring event pattern support

## Architecture

### Calendar API (`calendar_api/`)
- **Interfaces** - `CalendarClient` and `CalendarProvider` abstract base classes
- **Models** - Complete data structures for events, attendees, time handling
- **Exceptions** - Comprehensive error hierarchy for all failure modes

### Data Models

#### Core Types
- **Event** - Complete calendar event with organizer, attendees, timing
- **TimeSlot** - Time period with timezone and duration utilities
- **Attendee** - Participant with status and role information
- **Recurrence** - Recurring pattern definitions

#### Request/Response Types
- **EventChanges** - Modification request structure
- **UpdateResult** - Rich response with conflicts and permission info
- **AvailabilityQuery** - Smart time slot finding parameters
- **BatchUpdateResult** - Atomic operation results

#### Search & Navigation
- **CalendarSearchQuery** - Flexible event search parameters
- **CalendarInfo** - Calendar metadata and permissions

## Role-Based Permission Model

The interface uses explicit role-based methods to prevent permission errors:

### As Event Organizer
```python
# Create events you organize
result = await client.create_my_event(event)

# Modify events you organize  
await client.update_my_event(event_id, changes)

# Cancel events you organize
await client.delete_my_event(event_id)
```

### As Event Attendee
```python
# Respond to invitations
response = InvitationResponse(status=AttendeeStatus.ACCEPTED)
await client.respond_to_invitation(event_id, response)

# Suggest alternative times (provider dependent)
new_time = TimeSlot(start=tomorrow, end=tomorrow.add_hours(1))
await client.suggest_reschedule(event_id, new_time)
```

## AI Assistant Integration

Designed specifically for AI assistants that need rich calendar context:

### Context Gathering
```python
# Get schedule overview
events = await client.get_events(time_range)

# Find available meeting times
availability_query = AvailabilityQuery(
    time_range=time_range,
    duration_minutes=60,
    attendees=["alice@example.com", "bob@example.com"]
)
slots = await client.find_available_slots(availability_query)

# Search for specific events
query = CalendarSearchQuery(
    query="project review",
    attendee_email="manager@example.com"
)
results = await client.search_events(query)
```

### Intelligent Decision Making
```python
# Rich conflict and permission information
result = await client.create_my_event(event)

if not result.success:
    if result.conflicts:
        # Present conflicts to user for resolution
        for conflict in result.conflicts:
            print(f"Conflict: {conflict.conflict_type}")
            print(f"Suggestion: {conflict.suggestion}")
    
    if result.permissions:
        # Check what actions are allowed
        if not result.permissions.can_edit:
            print(f"Cannot edit: {result.permissions.reason}")
```

## Exception Hierarchy

Comprehensive error handling for all calendar operations:

- **`CalendarAPIError`** - Base exception for all calendar errors
- **`CalendarConnectionError`** - Network and service connectivity
- **`CalendarAuthenticationError`** - OAuth and credential issues
- **`CalendarPermissionError`** - Access control and role restrictions
- **`CalendarSchedulingError`** - Time conflicts and availability issues
- **`CalendarTimeError`** - Timezone and date/time handling
- **`CalendarRecurrenceError`** - Recurring event pattern problems

## Development

### Testing
```bash
# Run calendar tests
uv run pytest src/mAIgic_integrations/calendar/ -v

# Run with coverage
uv run pytest src/mAIgic_integrations/calendar/ --cov=src/mAIgic_integrations/calendar --cov-report=term-missing

# Test specific components
uv run pytest src/mAIgic_integrations/calendar/calendar_api/tests/ -v
```

### Type Checking
```bash
# Check calendar types
uv run mypy src/mAIgic_integrations/calendar/
```

## Future Provider Implementations

The architecture supports multiple calendar providers:

- **Google Calendar** - OAuth2 with Google Calendar API
- **Microsoft Outlook** - Microsoft Graph API integration  
- **Apple Calendar** - CalDAV protocol support
- **Generic CalDAV** - Any CalDAV-compatible calendar service

Each provider will implement the same `CalendarClient` interface for consistent usage patterns.

## Dependencies

### Core Dependencies
- `python>=3.12` - Modern Python features and type support

### Future Provider Dependencies
- **Google Calendar**: `google-api-python-client`, `google-auth`
- **Microsoft Outlook**: `msal`, `microsoft-graph-sdk`  
- **Time Handling**: `pendulum` for robust timezone support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 