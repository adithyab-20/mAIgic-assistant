#!/usr/bin/env python3
"""
Basic Google Calendar Operations

Demonstrates core Google Calendar operations using the registry pattern:
- Client setup via registry (uses credential metadata)
- Retrieving calendar events
- Creating new events
- Finding available time slots

Prerequisites:
- Run: uv run maigic-integrations-setup --service calendar
- Ensure credentials are properly configured

Usage:
    uv run python src/mAIgic_integrations/calendar/calendar_google_impl/examples/basic_calendar_operations.py
"""

import asyncio
import logging

# Use the high-level registry pattern
from mAIgic_integrations import create_calendar_client
from mAIgic_integrations.calendar import (
    AvailabilityQuery,
    CalendarAPIError,
    CalendarDateTime,
    Event,
    EventPriority,
    TimeSlot,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_client():
    """Initialize Google Calendar client via registry."""
    try:
        # This uses the credential metadata files created by setup
        client = create_calendar_client("google_calendar")
        return client
    except Exception as e:
        raise RuntimeError(
            f"Failed to create calendar client: {e}\n"
            "Run: uv run maigic-integrations-setup --service calendar"
        )


async def get_upcoming_events(client, days: int = 7):
    """Retrieve upcoming events."""
    print(f"Retrieving events for the next {days} days...")

    now = CalendarDateTime.now()
    future = now.add_days(days)
    time_range = TimeSlot(now, future)

    try:
        events = await client.get_events(time_range)
        print(f"Found {len(events)} events")

        for i, event in enumerate(events[:5], 1):
            duration = event.time_slot.duration_minutes
            print(f"  {i}. {event.title}")
            print(f"     {event.time_slot.start} ({duration} min)")
            if event.location:
                print(f"     Location: {event.location}")

        return events
    except CalendarAPIError as e:
        print(f"Error retrieving events: {e}")
        return []


async def create_sample_event(client):
    """Create a sample calendar event."""
    print("\nCreating sample event...")

    # Create event 2 hours from now
    start_time = CalendarDateTime.now().add_hours(2)
    end_time = start_time.add_hours(1)

    event = Event(
        event_id="",
        title="Sample Meeting",
        description="Created via mAIgic Calendar integration (registry pattern)",
        time_slot=TimeSlot(start_time, end_time),
        priority=EventPriority.NORMAL,
        attendees=[
            # Add real email addresses for actual invitations
            # Attendee(email="colleague@example.com", status=AttendeeStatus.PENDING)
        ]
    )

    try:
        result = await client.create_my_event(event)
        if result.success:
            print("Event created successfully!")
            print(f"Event ID: {result.updated_event.event_id}")
            print(f"Title: {result.updated_event.title}")
            print(f"Time: {result.updated_event.time_slot.start}")
            return result.updated_event
        else:
            print(f"Failed to create event: {result.error_message}")
            return None
    except CalendarAPIError as e:
        print(f"Error creating event: {e}")
        return None


async def find_available_slots(client):
    """Find available meeting times."""
    print("\nFinding available meeting times...")

    tomorrow = CalendarDateTime.now().add_days(1).replace(hour=9, minute=0)
    end_of_day = tomorrow.replace(hour=17, minute=0)

    query = AvailabilityQuery(
        time_range=TimeSlot(tomorrow, end_of_day),
        duration_minutes=60,
        attendees=[
            # Add attendee emails for real availability checking
            # "colleague@example.com"
        ]
    )

    try:
        slots = await client.find_available_slots(query)
        print(f"Found {len(slots)} available slots:")

        for i, slot in enumerate(slots[:3], 1):
            print(f"  {i}. {slot.time_slot.start} - {slot.time_slot.end}")
            print(f"     Confidence: {slot.confidence * 100:.0f}%")

        return slots
    except CalendarAPIError as e:
        print(f"Error finding slots: {e}")
        return []


async def cleanup_event(client, event: Event):
    """Remove the sample event."""
    if event and event.event_id:
        print("\nCleaning up sample event...")
        try:
            await client.delete_my_event(event.event_id)
            print("Sample event removed successfully")
        except CalendarAPIError as e:
            print(f"Error cleaning up event: {e}")


async def main():
    """Run basic calendar operations demo."""
    print("Google Calendar Basic Operations (Registry Pattern)")
    print("=" * 55)

    try:
        # Setup client using registry pattern
        client = await setup_client()

        async with client:
            # Get upcoming events
            await get_upcoming_events(client)

            # Create sample event
            sample_event = await create_sample_event(client)

            # Find available slots
            await find_available_slots(client)

            # Cleanup
            await cleanup_event(client, sample_event)

        print("\nDemo completed successfully!")
        print("\nNote: This example uses the registry pattern which:")
        print("- Automatically handles credential management")
        print("- Supports multiple users and profiles")
        print("- Uses metadata files created by the setup system")

    except Exception as e:
        print(f"Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Run: uv run maigic-integrations-setup --service calendar")
        print("2. Check setup status: uv run maigic-integrations-setup --list")
        print("3. Ensure Google Calendar API is enabled in Google Cloud Console")


if __name__ == "__main__":
    asyncio.run(main())
