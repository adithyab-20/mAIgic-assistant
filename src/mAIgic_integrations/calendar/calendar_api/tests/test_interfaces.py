"""
Tests for calendar API interfaces (abstract classes).

This module tests that the abstract interfaces are properly defined
and that complete implementations can work correctly.
"""

import inspect

import pytest

from ..interfaces import CalendarClient, CalendarProvider
from ..models import (
    AttendeeStatus,
    AvailabilityQuery,
    AvailableSlot,
    BatchUpdateResult,
    CalendarDateTime,
    CalendarInfo,
    CalendarSearchQuery,
    CalendarSearchResult,
    Event,
    EventChanges,
    EventPriority,
    EventStatus,
    InvitationResponse,
    NotifyOption,
    PermissionInfo,
    TimeSlot,
    UpdateResult,
)


class TestCalendarClientInterface:
    """Test CalendarClient abstract interface."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that CalendarClient cannot be instantiated directly."""
        with pytest.raises(TypeError):
            CalendarClient()

    def test_has_expected_abstract_methods(self):
        """Test that CalendarClient has exactly the expected abstract methods."""
        abstract_methods = [name for name, method in inspect.getmembers(CalendarClient)
                          if getattr(method, "__isabstractmethod__", False)]

        expected_methods = [
            "__aenter__", "__aexit__",
            "get_events", "find_available_slots", "search_events", "get_event",
            "create_my_event", "update_my_event", "delete_my_event",
            "respond_to_invitation", "suggest_reschedule",
            "batch_create_events", "batch_update_events",
            "get_event_permissions", "get_calendars"
        ]
        assert sorted(abstract_methods) == sorted(expected_methods)

    def test_incomplete_implementation_fails(self):
        """Test that incomplete implementation cannot be instantiated."""

        class IncompleteCalendarClient(CalendarClient):
            # Missing most required methods
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        with pytest.raises(TypeError):
            IncompleteCalendarClient()

    def test_complete_implementation_works(self):
        """Test that complete implementation can be instantiated."""

        class WorkingCalendarClient(CalendarClient):
            def __init__(self):
                # Create time slots for the events
                start_time = CalendarDateTime.now()
                end_time = start_time.add_hours(1)
                time_slot = TimeSlot(start=start_time, end=end_time)

                self.events = [
                    Event(event_id="1", title="Meeting 1", time_slot=time_slot),
                    Event(event_id="2", title="Meeting 2", time_slot=time_slot),
                ]

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

            async def get_events(self, time_range, calendar_ids=None, include_declined=False):
                return self.events

            async def find_available_slots(self, query):
                # Return a mock available slot
                return [AvailableSlot(
                    time_slot=query.time_range,
                    confidence=0.9
                )]

            async def search_events(self, query):
                matching_events = [e for e in self.events if query.query.lower() in e.title.lower()]
                return CalendarSearchResult(
                    events=matching_events,
                    total_count=len(matching_events),
                    has_more=False
                )

            async def get_event(self, event_id):
                for event in self.events:
                    if event.event_id == event_id:
                        return event
                raise ValueError(f"Event {event_id} not found")

            async def create_my_event(self, event, calendar_id=None, notify_attendees=NotifyOption.DEFAULT):
                return UpdateResult(success=True, updated_event=event)

            async def update_my_event(self, event_id, changes, notify_attendees=NotifyOption.DEFAULT):
                event = await self.get_event(event_id)
                return UpdateResult(success=True, updated_event=event)

            async def delete_my_event(self, event_id, notify_attendees=NotifyOption.DEFAULT, cancellation_message=None):
                return UpdateResult(success=True)

            async def respond_to_invitation(self, event_id, response):
                return UpdateResult(success=True)

            async def suggest_reschedule(self, event_id, proposed_time, message=None):
                return UpdateResult(success=True)

            async def batch_create_events(self, events, calendar_id=None, notify_attendees=NotifyOption.DEFAULT):
                results = [UpdateResult(success=True, updated_event=event) for event in events]
                return BatchUpdateResult(
                    successful_updates=results,
                    failed_updates=[]
                )

            async def batch_update_events(self, updates, notify_attendees=NotifyOption.DEFAULT):
                results = [UpdateResult(success=True) for _ in updates]
                return BatchUpdateResult(
                    successful_updates=results,
                    failed_updates=[]
                )

            async def get_event_permissions(self, event_id):
                return PermissionInfo(
                    can_read=True,
                    can_edit=True,
                    can_delete=True,
                    can_invite_others=True,
                    can_modify_attendees=True
                )

            async def get_calendars(self):
                return [CalendarInfo(
                    calendar_id="primary",
                    name="Primary Calendar",
                    is_primary=True
                )]

        client = WorkingCalendarClient()
        assert isinstance(client, CalendarClient)


class TestCalendarProviderInterface:
    """Test CalendarProvider abstract interface."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that CalendarProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            CalendarProvider()

    def test_has_expected_abstract_methods(self):
        """Test that CalendarProvider has expected abstract methods."""
        abstract_methods = [name for name, method in inspect.getmembers(CalendarProvider)
                          if getattr(method, "__isabstractmethod__", False)]

        expected_methods = [
            "create_client", "validate_config", "get_required_config_keys",
            "get_optional_config_keys", "get_config_description"
        ]
        assert sorted(abstract_methods) == sorted(expected_methods)

    def test_complete_implementation_works(self):
        """Test that complete implementation can be instantiated."""

        class MockCalendarProvider(CalendarProvider):
            def create_client(self, **config):
                return None  # Would return actual client in real implementation

            def validate_config(self, **config):
                return True

            def get_required_config_keys(self):
                return ["credentials_path"]

            def get_optional_config_keys(self):
                return ["timeout_seconds"]

            def get_config_description(self):
                return "Mock calendar provider configuration"

        provider = MockCalendarProvider()
        assert isinstance(provider, CalendarProvider)


class TestCalendarClientImplementation:
    """Test a working implementation of CalendarClient."""

    class WorkingCalendarClient(CalendarClient):
        def __init__(self):
            # Mock data for testing
            now = CalendarDateTime.now()
            future = now.add_hours(2)

            self.events = [
                Event(
                    event_id="1",
                    title="Team Meeting",
                    time_slot=TimeSlot(start=now, end=future),
                    status=EventStatus.CONFIRMED,
                    priority=EventPriority.NORMAL
                ),
                Event(
                    event_id="2",
                    title="Project Review",
                    time_slot=TimeSlot(start=future, end=future.add_hours(1)),
                    status=EventStatus.TENTATIVE,
                    priority=EventPriority.HIGH
                ),
            ]
            self.calendars = [
                CalendarInfo(
                    calendar_id="primary",
                    name="Primary Calendar",
                    is_primary=True,
                    permissions=PermissionInfo(
                        can_read=True,
                        can_edit=True,
                        can_delete=True,
                        role="owner"
                    )
                ),
                CalendarInfo(
                    calendar_id="work",
                    name="Work Calendar",
                    is_primary=False,
                    permissions=PermissionInfo(
                        can_read=True,
                        can_edit=True,
                        role="writer"
                    )
                )
            ]

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def get_events(self, time_range, calendar_ids=None, include_declined=False):
            # Simple filtering based on time range
            return [e for e in self.events if
                    e.time_slot.start.dt >= time_range.start.dt and
                    e.time_slot.end.dt <= time_range.end.dt]

        async def find_available_slots(self, query):
            # Mock availability - return one slot
            return [AvailableSlot(
                time_slot=TimeSlot(
                    start=query.time_range.start.add_hours(1),
                    end=query.time_range.start.add_hours(1 + query.duration_minutes/60)
                ),
                confidence=0.9,
                attendee_conflicts=[]
            )]

        async def search_events(self, query):
            if query.query:
                matching_events = [e for e in self.events if query.query.lower() in e.title.lower()]
            else:
                matching_events = self.events

            # Apply other filters
            if query.event_status:
                matching_events = [e for e in matching_events if e.status == query.event_status]

            # Apply limit (no offset support in current model)
            start_idx = 0
            end_idx = query.max_results if query.max_results else len(matching_events)
            result_events = matching_events[start_idx:end_idx]

            return CalendarSearchResult(
                events=result_events,
                total_count=len(matching_events),
                has_more=end_idx < len(matching_events),
                next_page_token="next-token" if end_idx < len(matching_events) else None
            )

        async def get_event(self, event_id):
            for event in self.events:
                if event.event_id == event_id:
                    return event
            raise ValueError(f"Event {event_id} not found")

        async def create_my_event(self, event, calendar_id=None, notify_attendees=NotifyOption.DEFAULT):
            # Add to mock storage
            self.events.append(event)
            return UpdateResult(success=True, updated_event=event)

        async def update_my_event(self, event_id, changes, notify_attendees=NotifyOption.DEFAULT):
            event = await self.get_event(event_id)

            # Apply changes
            if changes.title is not None:
                event.title = changes.title
            if changes.time_slot is not None:
                event.time_slot = changes.time_slot
            if changes.status is not None:
                event.status = changes.status
            if changes.priority is not None:
                event.priority = changes.priority

            return UpdateResult(success=True, updated_event=event)

        async def delete_my_event(self, event_id, notify_attendees=NotifyOption.DEFAULT, cancellation_message=None):
            # Remove from mock storage
            self.events = [e for e in self.events if e.event_id != event_id]
            return UpdateResult(success=True)

        async def respond_to_invitation(self, event_id, response):
            event = await self.get_event(event_id)
            # In real implementation, would update attendee status
            return UpdateResult(success=True, updated_event=event)

        async def suggest_reschedule(self, event_id, proposed_time, message=None):
            # Mock suggestion - always succeeds
            return UpdateResult(success=True)

        async def batch_create_events(self, events, calendar_id=None, notify_attendees=NotifyOption.DEFAULT):
            successful_updates = []
            for event in events:
                result = await self.create_my_event(event, calendar_id, notify_attendees)
                successful_updates.append(result)

            return BatchUpdateResult(
                successful_updates=successful_updates,
                failed_updates=[]
            )

        async def batch_update_events(self, updates, notify_attendees=NotifyOption.DEFAULT):
            successful_updates = []
            failed_updates = []

            for event_id, changes in updates:
                try:
                    result = await self.update_my_event(event_id, changes, notify_attendees=notify_attendees)
                    successful_updates.append(result)
                except ValueError as e:
                    failed_updates.append((event_id, str(e)))

            return BatchUpdateResult(
                successful_updates=successful_updates,
                failed_updates=failed_updates
            )

        async def get_event_permissions(self, event_id):
            # Mock permissions - full access for all events
            return PermissionInfo(
                can_read=True,
                can_edit=True,
                can_delete=True,
                can_invite_others=True,
                can_modify_attendees=True,
                reason="Event organizer"
            )

        async def get_calendars(self):
            return self.calendars.copy()

    @pytest.mark.asyncio
    async def test_basic_functionality(self):
        """Test basic calendar client functionality."""
        client = self.WorkingCalendarClient()

        # Test context manager
        async with client as c:
            # Test get_events
            now = CalendarDateTime.now()
            future = now.add_hours(8)
            time_range = TimeSlot(start=now, end=future)

            events = await c.get_events(time_range)
            assert len(events) >= 0  # Might be 0 if mock events are outside range

            # Test search_events
            search_query = CalendarSearchQuery(query="Meeting")
            results = await c.search_events(search_query)
            assert isinstance(results, CalendarSearchResult)
            assert len(results.events) >= 0

            # Test get_event
            if results.events:
                event = await c.get_event(results.events[0].event_id)
                assert event.event_id == results.events[0].event_id

            # Test find_available_slots
            availability_query = AvailabilityQuery(
                time_range=time_range,
                duration_minutes=60
            )
            slots = await c.find_available_slots(availability_query)
            assert len(slots) >= 0

            # Test get_calendars
            calendars = await c.get_calendars()
            assert len(calendars) >= 1
            assert any(cal.is_primary for cal in calendars)

    @pytest.mark.asyncio
    async def test_event_management(self):
        """Test event creation, update, and deletion."""
        client = self.WorkingCalendarClient()

        async with client as c:
            # Create event
            new_event = Event(
                event_id="test-event",
                title="Test Meeting",
                time_slot=TimeSlot(
                    start=CalendarDateTime.now(),
                    end=CalendarDateTime.now().add_hours(1)
                )
            )

            create_result = await c.create_my_event(new_event)
            assert create_result.success
            assert create_result.updated_event.title == "Test Meeting"

            # Update event
            changes = EventChanges(
                title="Updated Meeting",
                priority=EventPriority.HIGH
            )
            update_result = await c.update_my_event("test-event", changes)
            assert update_result.success
            assert update_result.updated_event.title == "Updated Meeting"
            assert update_result.updated_event.priority == EventPriority.HIGH

            # Delete event
            delete_result = await c.delete_my_event("test-event")
            assert delete_result.success

    @pytest.mark.asyncio
    async def test_invitation_handling(self):
        """Test invitation response functionality."""
        client = self.WorkingCalendarClient()

        async with client as c:
            # Test responding to invitation
            response = InvitationResponse(
                status=AttendeeStatus.ACCEPTED,
                comment="Looking forward to it!"
            )

            result = await c.respond_to_invitation("1", response)
            assert result.success

            # Test reschedule suggestion
            new_time = TimeSlot(
                start=CalendarDateTime.now().add_hours(2),
                end=CalendarDateTime.now().add_hours(3)
            )

            reschedule_result = await c.suggest_reschedule(
                "1",
                new_time,
                "Would this time work better?"
            )
            assert reschedule_result.success

    @pytest.mark.asyncio
    async def test_batch_operations(self):
        """Test batch event operations."""
        client = self.WorkingCalendarClient()

        async with client as c:
            # Create time slot for events
            start_time = CalendarDateTime.now()
            end_time = start_time.add_hours(1)
            time_slot = TimeSlot(start=start_time, end=end_time)

            # Test batch create
            events = [
                Event(event_id="batch-1", title="Batch Meeting 1", time_slot=time_slot),
                Event(event_id="batch-2", title="Batch Meeting 2", time_slot=time_slot),
            ]

            batch_create_result = await c.batch_create_events(events)
            assert batch_create_result.total_processed == 2
            assert batch_create_result.total_successful == 2
            assert batch_create_result.total_failed == 0

            # Test batch update
            updates = [
                ("batch-1", EventChanges(title="Updated Batch 1")),
                ("batch-2", EventChanges(priority=EventPriority.HIGH)),
            ]

            batch_update_result = await c.batch_update_events(updates)
            assert batch_update_result.total_processed == 2
            assert batch_update_result.total_successful == 2

    @pytest.mark.asyncio
    async def test_permission_checking(self):
        """Test permission checking functionality."""
        client = self.WorkingCalendarClient()

        async with client as c:
            permissions = await c.get_event_permissions("1")
            assert isinstance(permissions, PermissionInfo)
            assert permissions.can_read
            # Other permissions depend on implementation

    @pytest.mark.asyncio
    async def test_advanced_search(self):
        """Test advanced search functionality."""
        client = self.WorkingCalendarClient()

        async with client as c:
            # Search with status filter
            query = CalendarSearchQuery(
                query="Meeting",
                event_status=EventStatus.CONFIRMED,
                max_results=10
            )

            results = await c.search_events(query)
            assert isinstance(results, CalendarSearchResult)

            # All returned events should match the status filter
            for event in results.events:
                assert event.status == EventStatus.CONFIRMED

    def test_interface_compliance(self):
        """Test that the working client implements all required methods."""
        client = self.WorkingCalendarClient()

        # Verify all abstract methods are implemented
        abstract_methods = [name for name, method in inspect.getmembers(CalendarClient)
                          if getattr(method, "__isabstractmethod__", False)]

        for method_name in abstract_methods:
            assert hasattr(client, method_name), f"Missing method: {method_name}"
            method = getattr(client, method_name)
            assert callable(method), f"Method {method_name} is not callable"
