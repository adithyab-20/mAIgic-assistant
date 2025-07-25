# Calendar Integration

Google Calendar integration with role-based permissions and intelligent scheduling support for the mAIgic Assistant.

## Overview

This package provides:
- **Calendar API**: Abstract interfaces and type definitions
- **Google Calendar Implementation**: Full-featured Google Calendar client
- **Role-Based Interface**: Separate organizer and attendee operations
- **AI-Friendly Context**: Rich event data and conflict detection
- **Time Handling**: Timezone-aware datetime and recurrence support

## Architecture

```
calendar/
├── calendar_api/           # Abstract interfaces and types
└── calendar_google_impl/   # Google Calendar implementation
```

## Installation

```bash
# Install with calendar capabilities
uv sync --extra calendar
```

## Setup

### Google Cloud Console

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing
   - Enable Google Calendar API

2. **Configure OAuth2**
   - Go to APIs & Services > Credentials
   - Create OAuth client ID (Desktop application)
   - Download `credentials.json`

### Using Setup Wizard

```bash
# Interactive setup
uv run maigic-integrations-setup --service calendar

# Check status
uv run maigic-integrations-setup --list
```

## Usage

### Direct Client Usage

```python
from mAIgic_integrations.calendar import GoogleCalendarClient, GoogleCalendarConfig

config = GoogleCalendarConfig(
    credentials_path="credentials.json",
    token_path="token.json"
)

async with GoogleCalendarClient(config) as client:
    # Get events for today
    events = await client.get_events(time_range)
    
    # Create new event
    event = Event(
        title="Team Meeting",
        time_slot=TimeSlot(start_time, end_time)
    )
    result = await client.create_my_event(event)
```

### Registry Pattern

```python
from mAIgic_integrations import create_calendar_client

# Automatic credential discovery
client = create_calendar_client("google_calendar")
async with client:
    events = await client.get_events(time_range)
    for event in events:
        print(f"{event.title} at {event.time_slot}")
```

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

## Data Models

### Core Types

- **Event**: Complete calendar event with organizer, attendees, timing
- **TimeSlot**: Time period with timezone and duration utilities
- **Attendee**: Participant with status and role information
- **Recurrence**: Recurring pattern definitions

### Request/Response Types

- **EventChanges**: Modification request structure
- **UpdateResult**: Rich response with conflicts and permission info
- **AvailabilityQuery**: Smart time slot finding parameters
- **BatchUpdateResult**: Atomic operation results

## Role-Based Permission Model

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

# Suggest alternative times
new_time = TimeSlot(start=tomorrow, end=tomorrow.add_hours(1))
await client.suggest_reschedule(event_id, new_time)
```

## AI Assistant Integration

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
        for conflict in result.conflicts:
            print(f"Conflict: {conflict.conflict_type}")
            print(f"Suggestion: {conflict.suggestion}")
    
    if result.permissions:
        if not result.permissions.can_edit:
            print(f"Cannot edit: {result.permissions.reason}")
```

## Exception Hierarchy

Comprehensive error handling:

- **`CalendarAPIError`**: Base exception for all calendar errors
- **`CalendarConnectionError`**: Network and service connectivity
- **`CalendarAuthenticationError`**: OAuth and credential issues
- **`CalendarPermissionError`**: Access control and role restrictions
- **`CalendarSchedulingError`**: Time conflicts and availability issues
- **`CalendarTimeError`**: Timezone and date/time handling
- **`CalendarRecurrenceError`**: Recurring event pattern problems

## Examples

Run the provided examples:

```bash
uv run python src/mAIgic_integrations/calendar/calendar_google_impl/examples/basic_calendar_operations.py
```

## Testing

```bash
# Run calendar tests
uv run pytest src/mAIgic_integrations/calendar/ -v

# Run with coverage
uv run pytest src/mAIgic_integrations/calendar/ --cov=src/mAIgic_integrations/calendar --cov-report=term-missing

# Test specific components
uv run pytest src/mAIgic_integrations/calendar/calendar_api/tests/ -v
```

## Development

### Type Checking

```bash
uv run mypy src/mAIgic_integrations/calendar/
```

### Code Quality

```bash
uv run ruff check src/mAIgic_integrations/calendar/
uv run ruff format src/mAIgic_integrations/calendar/
``` 