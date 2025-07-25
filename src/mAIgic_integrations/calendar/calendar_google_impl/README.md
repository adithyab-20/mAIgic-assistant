# mAIgic Google Calendar Implementation

Complete Google Calendar integration for the mAIgic AI assistant platform. Implements the mAIgic calendar interface using Google Calendar API v3.

## Features

- **Full Calendar Operations**: Create, read, update, delete events with role-based permissions
- **OAuth2 Authentication**: Secure authentication flow with token persistence
- **Rich Event Support**: Attendees, recurrence, time zones, all-day events
- **Availability Queries**: Find free time slots using Google's Freebusy API
- **Batch Operations**: Efficient bulk event operations
- **Multiple Calendars**: Support for accessing multiple Google calendars
- **AI-Friendly Interface**: Designed specifically for AI assistant use cases

## Installation

Install as part of the mAIgic Assistant with Google Calendar support:

```bash
# Using uv (recommended)
uv add "maigic-assistant[google-calendar]"

# Using pip
pip install "maigic-assistant[google-calendar]"
```

## Quick Start

### 1. Setup Google Calendar API

1. **Enable Google Calendar API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select an existing one
   - Enable the Google Calendar API

2. **Create OAuth2 Credentials**:
   - Go to Credentials → Create Credentials → OAuth 2.0 Client IDs
   - Choose "Desktop application"
   - Download the credentials JSON file

3. **Place Credentials**:
   ```bash
   # Place the downloaded file in your project
   cp ~/Downloads/credentials.json ./google_calendar_credentials.json
   ```

### 2. Basic Usage

```python
import asyncio
from mAIgic_integrations.calendar.calendar_google_impl import (
    GoogleCalendarClient,
    GoogleCalendarConfig
)
from mAIgic_integrations.calendar import (
    Event,
    TimeSlot,
    CalendarDateTime,
    Attendee,
    AttendeeStatus
)

async def main():
    # Configure Google Calendar client
    config = GoogleCalendarConfig(
        credentials_path="google_calendar_credentials.json",
        token_path="google_calendar_token.json",
        user_timezone="US/Eastern"
    )
    
    # Use the client
    async with GoogleCalendarClient(config) as client:
        # Get today's events
        today = CalendarDateTime.now()
        tomorrow = today.add_hours(24)
        time_range = TimeSlot(today, tomorrow)
        
        events = await client.get_events(time_range)
        print(f"Found {len(events)} events today")
        
        # Create a new meeting
        meeting = Event(
            event_id="",  # Will be auto-generated
            title="Team Standup",
            time_slot=TimeSlot(
                start=today.add_hours(2),
                end=today.add_hours(2.5)
            ),
            description="Daily team standup meeting",
            location="Conference Room A",
            attendees=[
                Attendee(
                    email="alice@company.com",
                    name="Alice Smith",
                    status=AttendeeStatus.NEEDS_ACTION
                ),
                Attendee(
                    email="bob@company.com", 
                    name="Bob Johnson",
                    status=AttendeeStatus.NEEDS_ACTION
                )
            ]
        )
        
        # Create the event
        result = await client.create_my_event(meeting)
        if result.success:
            print(f"Created event: {result.updated_event.event_id}")
        else:
            print(f"Failed to create event: {result.error_message}")

# Run the example
asyncio.run(main())
```

### 3. Environment Configuration

You can use environment variables for configuration:

```bash
# Set environment variables
export GOOGLE_CALENDAR_CREDENTIALS_PATH="./credentials.json"
export GOOGLE_CALENDAR_TOKEN_PATH="./token.json"
export GOOGLE_CALENDAR_USER_TIMEZONE="US/Eastern"
export GOOGLE_CALENDAR_APPLICATION_NAME="My AI Assistant"
```

```python
# Use environment configuration
config = GoogleCalendarConfig.from_env()
```

## Advanced Usage

### Finding Available Time Slots

```python
from mAIgic_integrations.calendar import AvailabilityQuery

async def find_meeting_time():
    async with GoogleCalendarClient(config) as client:
        # Define search parameters
        next_week = TimeSlot(
            start=CalendarDateTime.now().add_hours(7 * 24),
            end=CalendarDateTime.now().add_hours(14 * 24)
        )
        
        query = AvailabilityQuery(
            time_range=next_week,
            duration_minutes=60,  # 1 hour meeting
            attendees=[
                "alice@company.com",
                "bob@company.com"
            ],
            buffer_minutes=15,  # 15 min buffer between meetings
            working_hours_only=True,
            exclude_weekends=True
        )
        
        # Find available slots
        available_slots = await client.find_available_slots(query)
        
        for slot in available_slots[:5]:  # Show first 5 options
            print(f"Available: {slot.time_slot.start.to_iso()} - {slot.time_slot.end.to_iso()}")
            print(f"Confidence: {slot.confidence:.2f}")
```

### Responding to Invitations

```python
from mAIgic_integrations.calendar import InvitationResponse, AttendeeStatus

async def respond_to_meetings():
    async with GoogleCalendarClient(config) as client:
        # Accept an invitation
        response = InvitationResponse(
            status=AttendeeStatus.ACCEPTED,
            comment="Looking forward to the meeting!"
        )
        
        result = await client.respond_to_invitation("event-id-here", response)
        if result.success:
            print("Successfully accepted invitation")
```

### Searching Events

```python
from mAIgic_integrations.calendar import CalendarSearchQuery

async def search_past_meetings():
    async with GoogleCalendarClient(config) as client:
        # Search for project meetings
        query = CalendarSearchQuery(
            query="project review",
            attendee_email="manager@company.com",
            time_range=TimeSlot(
                start=CalendarDateTime.now().add_hours(-30 * 24),  # Last 30 days
                end=CalendarDateTime.now()
            ),
            max_results=20
        )
        
        results = await client.search_events(query)
        print(f"Found {len(results.events)} project meetings")
        
        for event in results.events:
            print(f"- {event.title} on {event.time_slot.start.to_iso()}")
```

### Batch Operations

```python
async def create_multiple_events():
    async with GoogleCalendarClient(config) as client:
        # Create multiple events at once
        events = [
            Event(
                event_id="",
                title=f"Meeting {i}",
                time_slot=TimeSlot(
                    start=CalendarDateTime.now().add_hours(i * 24 + 10),
                    end=CalendarDateTime.now().add_hours(i * 24 + 11)
                )
            )
            for i in range(5)
        ]
        
        batch_result = await client.batch_create_events(events)
        print(f"Created {batch_result.total_successful} events")
        print(f"Failed {batch_result.total_failed} events")
```

## Configuration Options

### GoogleCalendarConfig

```python
@dataclass
class GoogleCalendarConfig:
    # Required
    credentials_path: str           # Path to OAuth credentials JSON
    
    # Optional
    token_path: str = "token.json"  # Where to store access tokens
    scopes: list[str] = None        # OAuth scopes (auto-determined)
    application_name: str = "mAIgic Assistant"
    user_timezone: str = "UTC"      # Default timezone
    read_only: bool = False         # Read-only access
    delegate_email: str = None      # For service account delegation
```

### OAuth Scopes

The implementation automatically selects appropriate scopes:

- **Read-only mode**: `https://www.googleapis.com/auth/calendar.readonly`
- **Full access**: 
  - `https://www.googleapis.com/auth/calendar`
  - `https://www.googleapis.com/auth/calendar.events`

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CALENDAR_CREDENTIALS_PATH` | Path to credentials JSON | `"credentials.json"` |
| `GOOGLE_CALENDAR_TOKEN_PATH` | Path for token storage | `"token.json"` |
| `GOOGLE_CALENDAR_APPLICATION_NAME` | Application identifier | `"mAIgic Assistant"` |
| `GOOGLE_CALENDAR_USER_TIMEZONE` | Default timezone | `"UTC"` |
| `GOOGLE_CALENDAR_READ_ONLY` | Read-only access | `"false"` |
| `GOOGLE_CALENDAR_DELEGATE_EMAIL` | Service account delegation | `None` |

## Error Handling

The implementation provides comprehensive error handling:

```python
from mAIgic_integrations.calendar.calendar_api.exceptions import (
    CalendarAuthenticationError,
    CalendarPermissionError,
    CalendarEventNotFoundError,
    CalendarSchedulingError,
    CalendarConnectionError
)

async def robust_calendar_operations():
    try:
        async with GoogleCalendarClient(config) as client:
            result = await client.create_my_event(event)
            
    except CalendarAuthenticationError as e:
        print(f"Authentication failed: {e}")
        # Handle re-authentication
        
    except CalendarPermissionError as e:
        print(f"Permission denied: {e}")
        # Handle permission issues
        
    except CalendarSchedulingError as e:
        print(f"Scheduling conflict: {e}")
        # Handle conflicts
        
    except CalendarConnectionError as e:
        print(f"Connection error: {e}")
        # Handle network issues
```

## Testing

### Unit Tests

```bash
# Run unit tests
uv run pytest tests/unit/ -v

# Run with coverage
uv run pytest tests/unit/ --cov=src/mAIgic_integrations/calendar/calendar_google_impl
```

### Integration Tests

Integration tests require real Google Calendar API credentials:

```bash
# Set up test credentials
cp credentials.json test_credentials.json

# Run integration tests
uv run pytest tests/integration/ -v -m integration
```

### Test Configuration

Create a `.env` file for testing:

```bash
# Test environment variables
GOOGLE_CALENDAR_CREDENTIALS_PATH=test_credentials.json
GOOGLE_CALENDAR_TOKEN_PATH=test_token.json
GOOGLE_CALENDAR_USER_TIMEZONE=UTC
```

## Limitations

### Google Calendar API Limitations

1. **Reschedule Suggestions**: Google Calendar API doesn't support sending reschedule suggestions directly
2. **Rate Limits**: Subject to Google Calendar API rate limits
3. **Attendee Responses**: Limited control over attendee response notifications
4. **Recurring Events**: Complex recurrence patterns may have limitations

### Implementation Limitations

1. **Time Zone Handling**: Currently uses simplified timezone handling (will be enhanced with pendulum)
2. **Batch Operations**: Google's batch API is used, but some operations are performed sequentially
3. **Calendar Selection**: Multi-calendar operations require explicit calendar IDs

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   ```bash
   # Ensure credentials file exists and is valid
   ls -la credentials.json
   python -c "import json; print(json.load(open('credentials.json'))['client_id'])"
   ```

2. **Permission Errors**:
   - Check OAuth scopes in Google Cloud Console
   - Verify calendar access permissions
   - Re-authenticate if needed: `rm token.json`

3. **Rate Limit Errors**:
   - Implement exponential backoff (built into Google client)
   - Reduce API call frequency
   - Use batch operations where possible

4. **Time Zone Issues**:
   - Ensure `user_timezone` matches your local timezone
   - Use `CalendarDateTime` for all time operations
   - Verify timezone format (e.g., "US/Eastern", not "EST")

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Google API client will show detailed request/response info
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/maigic/maigic-assistant.git
cd maigic-assistant

# Install with development dependencies
uv sync --extra dev

# Install pre-commit hooks
pre-commit install
```

### Code Quality

```bash
# Format code
uv run black src/mAIgic_integrations/calendar/calendar_google_impl/
uv run ruff --fix src/mAIgic_integrations/calendar/calendar_google_impl/

# Type checking
uv run mypy src/mAIgic_integrations/calendar/calendar_google_impl/

# Run all quality checks
uv run pre-commit run --all-files
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [mAIgic Calendar API Documentation](../calendar_api/README.md)
- **Google Calendar API**: [Official Documentation](https://developers.google.com/calendar/api)
- **Issues**: [GitHub Issues](https://github.com/maigic/maigic-assistant/issues)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](../../../../CONTRIBUTING.md) for detailed guidelines. 